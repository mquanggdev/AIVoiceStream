"use client";

/** Chi tiết cuộc gọi: dòng thời gian Khách / AI, nghe lại từng lượt, độ trễ, tool, kiểm tra số liệu. */

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge, Button, Card, PageHeader } from "@/components/admin/ui";
import type { ConversationDetail, Message } from "@/lib/admin-types";
import { adminFetch, fetchAudioUrl } from "@/lib/auth";
import { callStatusMeta, formatDateTime, formatDuration, formatMs, formatUsd, toolLabel } from "@/lib/labels";

export default function CallDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [call, setCall] = useState<ConversationDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    adminFetch(`/admin/conversations/${id}`)
      .then(async (r) => {
        if (!r.ok) throw new Error("Không tìm thấy cuộc gọi");
        setCall(await r.json());
      })
      .catch((reason: Error) => setError(reason.message));
  }, [id]);

  async function exportJson() {
    const response = await adminFetch(`/admin/conversations/${id}/export`);
    if (!response.ok) return;
    const blob = new Blob([JSON.stringify(await response.json(), null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `cuoc-goi-${id}.json`;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!call) return <p className="text-sm text-slate-500">Đang tải cuộc gọi...</p>;

  const status = callStatusMeta[call.status] ?? { label: call.status, tone: "slate" as const };
  const turns = groupTurns(call.messages);

  return (
    <>
      <PageHeader
        actions={
          <>
            <Link href="/admin/calls">
              <Button variant="ghost">← Danh sách</Button>
            </Link>
            <Button onClick={exportJson} variant="secondary">
              Xuất JSON đánh giá
            </Button>
          </>
        }
        description={`Bắt đầu ${formatDateTime(call.started_at)} · ${formatDuration(call.duration_sec)} · ${call.turn_count} lượt`}
        kicker={`Cuộc gọi #${call.id}`}
        title={call.customer_name ? `Cuộc gọi với ${call.customer_name}` : "Cuộc gọi chưa để lại thông tin"}
      />

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2" subtitle="Lượt nói theo thứ tự, có thể nghe lại từng lượt" title="Hội thoại">
          <ol className="space-y-5">
            {turns.map((turn) => (
              <li key={turn.index}>
                <p className="mb-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">
                  {turn.index === 0 ? "Mở đầu" : `Lượt ${turn.index}`}
                </p>
                <div className="space-y-2">
                  {turn.messages.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                  ))}
                </div>
              </li>
            ))}
          </ol>
        </Card>

        <div className="space-y-6">
          <Card title="Thông tin">
            <dl className="space-y-2 text-sm">
              <Row label="Trạng thái" value={<Badge tone={status.tone}>{status.label}</Badge>} />
              <Row
                label="Khách"
                value={
                  call.customer_id ? (
                    <Link className="font-semibold text-cyan-700 hover:underline" href={`/admin/customers/${call.customer_id}`}>
                      {call.customer_name} · {call.customer_phone}
                    </Link>
                  ) : (
                    "Chưa để lại"
                  )
                }
              />
              <Row label="Phản hồi TB" value={formatMs(call.avg_first_audio_ms)} />
              <Row label="Chi phí AI" value={formatUsd(call.cost_usd)} />
              <Row label="Ngắt lời" value={`${call.interrupted_turns} lần`} />
              <Row label="Data" value={call.data_version ?? "—"} />
              <Row label="STT" value={call.models.stt ?? "—"} />
              <Row label="LLM" value={call.models.llm ?? "—"} />
              <Row label="TTS" value={`${call.models.tts ?? "—"} (${call.models.tts_voice ?? ""})`} />
            </dl>
          </Card>
          <Card subtitle="Agent ghi nhận trong cuộc gọi" title="Hồ sơ trong cuộc gọi">
            <pre className="max-h-80 overflow-auto rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
              {JSON.stringify(
                { profile: call.state.profile ?? {}, customer: call.state.customer ?? null },
                null,
                2
              )}
            </pre>
          </Card>
        </div>
      </div>
    </>
  );
}

function groupTurns(messages: Message[]) {
  const map = new Map<number, Message[]>();
  for (const message of messages) {
    if (!map.has(message.turn_index)) map.set(message.turn_index, []);
    map.get(message.turn_index)!.push(message);
  }
  return [...map.entries()].map(([index, items]) => ({ index, messages: items }));
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-2">
      <dt className="text-slate-500">{label}</dt>
      <dd className="text-right font-semibold text-slate-800">{value}</dd>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isCustomer = message.role === "customer";
  const meta = message.meta ?? {};
  const [showDetail, setShowDetail] = useState(false);

  return (
    <div className={`flex ${isCustomer ? "justify-start" : "justify-end"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
          isCustomer
            ? "rounded-tl-sm bg-slate-100 text-slate-800"
            : meta.is_filler
              ? "rounded-tr-sm border border-dashed border-cyan-200 bg-cyan-50/50 text-slate-500"
              : "rounded-tr-sm bg-cyan-50 text-slate-800"
        }`}
      >
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <span className={`text-[11px] font-bold uppercase tracking-wider ${isCustomer ? "text-slate-500" : "text-cyan-700"}`}>
            {isCustomer ? "Khách" : meta.is_filler ? "AI · câu lót" : "AI"}
          </span>
          {meta.interrupted ? <Badge tone="amber">Bị ngắt lời sau {meta.played_segments ?? 0} câu</Badge> : null}
          {meta.fact_check === "mismatch" ? <Badge tone="red">Chặn mã căn: {meta.blocked_codes?.join(", ")}</Badge> : null}
          {meta.unverified_prices?.length ? <Badge tone="amber">Giá chưa đối chiếu</Badge> : null}
          {meta.stt_error ? <Badge tone="red">STT lỗi</Badge> : null}
          {meta.error ? <Badge tone="red">Lỗi agent</Badge> : null}
        </div>
        <p className="whitespace-pre-wrap leading-relaxed">
          {message.content || <em className="text-slate-400">(không nhận dạng được lời nói)</em>}
        </p>
        {message.has_audio ? <AudioPlayer messageId={message.id} /> : null}
        <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-slate-500">
          {isCustomer && meta.stt_ms ? <span>STT {formatMs(meta.stt_ms)}</span> : null}
          {!isCustomer && meta.first_audio_ms ? <span>Âm thanh đầu tiên {formatMs(meta.first_audio_ms)}</span> : null}
          {!isCustomer && meta.llm_first_sentence_ms ? <span>LLM câu đầu {formatMs(meta.llm_first_sentence_ms)}</span> : null}
          {!isCustomer && meta.turn_total_ms ? <span>Cả lượt {formatMs(meta.turn_total_ms)}</span> : null}
          {meta.stt_cost_usd || meta.llm_cost_usd || meta.tts_cost_usd_est ? (
            <span>
              Chi phí {formatUsd((meta.stt_cost_usd ?? 0) + (meta.llm_cost_usd ?? 0) + (meta.tts_cost_usd_est ?? 0))}
            </span>
          ) : null}
          {meta.tool_calls?.length ? (
            <button className="font-semibold text-cyan-700 hover:underline" onClick={() => setShowDetail(!showDetail)} type="button">
              {meta.tool_calls.map((t) => toolLabel[t.name] ?? t.name).join(", ")} {showDetail ? "▲" : "▼"}
            </button>
          ) : null}
        </div>
        {showDetail && meta.tool_calls ? (
          <div className="mt-2 space-y-2">
            {meta.tool_calls.map((tool, index) => (
              <div className="rounded-lg bg-white/80 p-2 text-[11px]" key={index}>
                <p className="font-bold text-slate-700">
                  {tool.name} · {tool.ms} ms
                </p>
                <p className="mt-1 break-all font-mono text-slate-600">{tool.arguments}</p>
                <p className="mt-1 break-all font-mono text-slate-400">{tool.result_preview}</p>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function AudioPlayer({ messageId }: { messageId: number }) {
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => () => {
    if (url) URL.revokeObjectURL(url);
  }, [url]);

  if (url) return <audio autoPlay className="mt-2 h-8 w-full" controls src={url} />;
  return (
    <button
      className="mt-2 inline-flex items-center gap-1 rounded-full bg-white px-3 py-1 text-xs font-semibold text-cyan-700 ring-1 ring-cyan-200 hover:bg-cyan-50"
      disabled={loading}
      onClick={async () => {
        setLoading(true);
        setUrl(await fetchAudioUrl(messageId));
        setLoading(false);
      }}
      type="button"
    >
      ▶ {loading ? "Đang tải..." : "Nghe lại"}
    </button>
  );
}
