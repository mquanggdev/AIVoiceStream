"""Hybrid search trên knowledge chunks: BM25 tiếng Việt (bỏ dấu) + cosine embedding, gộp bằng RRF.

Chỉ dùng cho câu hỏi định tính (tiện ích, vị trí, thiết kế, pháp lý chung...).
Giá, mã căn, diện tích KHÔNG lấy từ đây — xem `catalog.py`.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.ai.embeddings import try_embed_query
from src.core.text import tokens
from src.models.entities import DatasetVersion, KnowledgeChunk, Subdivision

RRF_K = 60
BM25_K1 = 1.5
BM25_B = 0.75


@dataclass
class _Doc:
    chunk_id: str
    subdivision_id: int | None
    subdivision_name: str | None
    topic: str
    title: str
    content: str
    terms: Counter
    length: int
    embedding: list[float] | None
    norm: float = 0.0


@dataclass
class KnowledgeIndex:
    version_key: tuple
    docs: list[_Doc] = field(default_factory=list)
    doc_freq: Counter = field(default_factory=Counter)
    avg_len: float = 1.0

    def bm25(self, query_terms: list[str], candidates: list[int]) -> list[tuple[int, float]]:
        n_docs = len(self.docs)
        scores = []
        for i in candidates:
            doc = self.docs[i]
            score = 0.0
            for term in query_terms:
                tf = doc.terms.get(term, 0)
                if not tf:
                    continue
                df = self.doc_freq[term]
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                score += idf * tf * (BM25_K1 + 1) / (tf + BM25_K1 * (1 - BM25_B + BM25_B * doc.length / self.avg_len))
            if score > 0:
                scores.append((i, score))
        return sorted(scores, key=lambda item: item[1], reverse=True)

    def cosine(self, vector: list[float], candidates: list[int]) -> list[tuple[int, float]]:
        q_norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        scores = []
        for i in candidates:
            doc = self.docs[i]
            if not doc.embedding or len(doc.embedding) != len(vector):
                continue
            dot = sum(a * b for a, b in zip(doc.embedding, vector, strict=True))
            scores.append((i, dot / (q_norm * doc.norm)))
        return sorted(scores, key=lambda item: item[1], reverse=True)


def _terms(text: str) -> list[str]:
    words = tokens(text)
    return words + [f"{a}_{b}" for a, b in zip(words, words[1:], strict=False)]


_INDEX: KnowledgeIndex | None = None


def get_index(db: Session) -> KnowledgeIndex:
    """Index trong bộ nhớ, tự dựng lại khi đổi dataset hoặc khi có thêm embedding."""
    global _INDEX
    version = db.scalar(select(DatasetVersion).where(DatasetVersion.is_active.is_(True)))
    embedded = db.scalar(select(KnowledgeChunk.id).where(KnowledgeChunk.embedding.is_not(None)).limit(1)) is not None
    key = (version.id if version else 0, version.embedding_model if version else None, embedded)
    if _INDEX is not None and _INDEX.version_key == key:
        return _INDEX

    names = {s.id: s.name for s in db.scalars(select(Subdivision)).all()}
    index = KnowledgeIndex(version_key=key)
    for chunk in db.scalars(select(KnowledgeChunk).order_by(KnowledgeChunk.id)).all():
        sub_name = names.get(chunk.subdivision_id) if chunk.subdivision_id else None
        terms = Counter(_terms(f"{sub_name or ''} {chunk.content}"))
        doc = _Doc(
            chunk_id=chunk.chunk_id,
            subdivision_id=chunk.subdivision_id,
            subdivision_name=sub_name,
            topic=chunk.topic,
            title=chunk.title,
            content=chunk.content,
            terms=terms,
            length=sum(terms.values()),
            embedding=chunk.embedding,
        )
        if doc.embedding:
            doc.norm = math.sqrt(sum(v * v for v in doc.embedding)) or 1.0
        index.docs.append(doc)
        index.doc_freq.update(set(terms))
    if index.docs:
        index.avg_len = sum(d.length for d in index.docs) / len(index.docs)
    _INDEX = index
    return index


def reset_index() -> None:
    global _INDEX
    _INDEX = None


async def search_knowledge(
    db: Session,
    query: str,
    *,
    subdivision_id: int | None = None,
    top_k: int = 3,
    use_embedding: bool = True,
) -> list[dict]:
    index = get_index(db)
    if not index.docs:
        return []
    if subdivision_id is not None:
        candidates = [i for i, d in enumerate(index.docs) if d.subdivision_id == subdivision_id]
    else:
        candidates = list(range(len(index.docs)))

    ranked_lists = [index.bm25(_terms(query), candidates)]
    if use_embedding and any(index.docs[i].embedding for i in candidates):
        vector = await try_embed_query(query)
        if vector:
            ranked_lists.append(index.cosine(vector, candidates))

    fused: Counter = Counter()
    for ranked in ranked_lists:
        for rank, (i, _score) in enumerate(ranked[:20], start=1):
            fused[i] += 1.0 / (RRF_K + rank)

    results = []
    for i, score in fused.most_common(top_k):
        doc = index.docs[i]
        results.append(
            {
                "chunk_id": doc.chunk_id,
                "subdivision": doc.subdivision_name or "Toàn đại đô thị",
                "topic": doc.topic,
                "title": doc.title,
                "content": doc.content,
                "score": round(score, 5),
            }
        )
    if not results and subdivision_id is not None:
        return await search_knowledge(db, query, subdivision_id=None, top_k=top_k, use_embedding=use_embedding)
    return results
