"""Đọc một bộ data theo đặc tả v3 từ thư mục (cleaned_data/demo_v3, cleaned_data/v3...)."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_FILES = ("subdivisions.jsonl", "buildings.jsonl", "units.csv", "knowledge_docs.jsonl")


@dataclass
class Dataset:
    root: Path
    manifest: dict = field(default_factory=dict)
    project: dict = field(default_factory=dict)
    subdivisions: list[dict] = field(default_factory=list)
    buildings: list[dict] = field(default_factory=list)
    units: list[dict] = field(default_factory=list)
    sales_policies: list[dict] = field(default_factory=list)
    knowledge_docs: list[dict] = field(default_factory=list)

    @property
    def version(self) -> str:
        return str(self.manifest.get("dataset_version") or f"unversioned:{self.root.name}")

    @property
    def is_demo(self) -> bool:
        return bool(self.manifest.get("is_demo", False))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{line_no}: JSON không hợp lệ ({exc.msg})") from exc
    return rows


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_dataset(root: str | Path) -> Dataset:
    root = Path(root)
    missing = [name for name in REQUIRED_FILES if not (root / name).exists()]
    if missing:
        raise FileNotFoundError(f"Thiếu file trong {root}: {', '.join(missing)}")
    with (root / "units.csv").open(encoding="utf-8", newline="") as handle:
        units = list(csv.DictReader(handle))
    return Dataset(
        root=root,
        manifest=_read_json(root / "manifest.json"),
        project=_read_json(root / "project.json"),
        subdivisions=_read_jsonl(root / "subdivisions.jsonl"),
        buildings=_read_jsonl(root / "buildings.jsonl"),
        units=units,
        sales_policies=_read_jsonl(root / "sales_policies.jsonl"),
        knowledge_docs=_read_jsonl(root / "knowledge_docs.jsonl"),
    )
