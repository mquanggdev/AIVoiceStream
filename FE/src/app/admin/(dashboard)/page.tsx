"use client";

import { useEffect, useState } from "react";

import { CallsTable } from "@/components/admin/calls-table";
import { Card, PageHeader, StatCard } from "@/components/admin/ui";
import type { ConversationSummary, DashboardStats } from "@/lib/admin-types";
import { adminFetch } from "@/lib/auth";
import { formatDateTime, formatMs, formatUsd } from "@/lib/labels";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [calls, setCalls] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      adminFetch("/admin/stats").then((r) => (r.ok ? r.json() : null)),
      adminFetch("/admin/conversations?limit=10").then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([statsData, callsData]) => {
        setStats(statsData);
        setCalls(callsData);
      })
      .finally(() => setLoading(false));
  }, []);

  const dataset = stats?.dataset;

  return (
    <>
      <PageHeader
        description="Theo dõi các cuộc gọi tư vấn bằng giọng nói, chất lượng phản hồi và khách đã để lại thông tin."
        kicker="Tổng quan"
        title="Trợ lý tư vấn giọng nói"
      />

      {dataset?.is_demo ? (
        <div className="mb-5 rounded-xl border border-amber-300 bg-amber-50 px-5 py-4 text-sm text-amber-900">
          <p className="font-bold">ĐANG DÙNG DATA DEMO ({dataset.version})</p>
          <p className="mt-1">
            Mã căn, giá, trạng thái và chính sách là dữ liệu giả lập để test hệ thống. Không dùng để tư vấn thật.
          </p>
        </div>
      ) : null}
      {stats && !stats.ai_configured ? (
        <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-800">
          <p className="font-bold">Chưa cấu hình OPENROUTER_API_KEY</p>
          <p className="mt-1">Cuộc gọi sẽ không nhận dạng giọng nói và không trả lời được. Điền key vào file .env rồi khởi động lại backend.</p>
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard caption={`${stats?.active_calls ?? 0} cuộc đang diễn ra`} label="Cuộc gọi" value={stats?.total_calls ?? "—"} />
        <StatCard
          caption={`${stats?.calls_with_lead ?? 0} cuộc gọi có để lại thông tin`}
          label="Khách để lại thông tin"
          value={stats?.total_customers ?? "—"}
        />
        <StatCard
          caption="Từ lúc khách ngừng nói đến khi nghe tiếng agent"
          label="Phản hồi trung bình"
          value={formatMs(stats?.avg_first_audio_ms)}
        />
        <StatCard
          caption={`${stats?.fact_check_mismatch_turns ?? 0} câu bị chặn do sai số liệu · TB ${stats?.avg_turns ?? 0} lượt/cuộc`}
          label="Chi phí AI (tổng)"
          value={formatUsd(stats?.total_cost_usd)}
        />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2" subtitle="Bấm vào một dòng để nghe lại cuộc gọi" title="Cuộc gọi gần đây">
          <CallsTable calls={calls} loading={loading} pageSize={10} />
        </Card>
        <Card subtitle="Bộ dữ liệu agent đang dùng" title="Dữ liệu">
          {dataset ? (
            <dl className="space-y-2 text-sm">
              {[
                ["Phiên bản", dataset.version],
                ["Thư mục", dataset.dataset_dir],
                ["Import lúc", formatDateTime(dataset.imported_at)],
                ["Phân khu", dataset.counts.subdivisions],
                ["Tòa", dataset.counts.buildings],
                ["Căn hộ", dataset.counts.units?.toLocaleString("vi-VN")],
                ["Chính sách", dataset.counts.sales_policies],
                ["Tài liệu / đoạn", `${dataset.counts.knowledge_docs} / ${dataset.counts.knowledge_chunks}`],
                ["Embedding", dataset.embedding_model ?? "Chưa có (dùng BM25)"],
              ].map(([label, value]) => (
                <div className="flex justify-between gap-3 border-b border-slate-100 pb-2" key={String(label)}>
                  <dt className="text-slate-500">{label}</dt>
                  <dd className="text-right font-semibold text-slate-800">{value}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <p className="text-sm text-slate-500">Chưa import dữ liệu.</p>
          )}
        </Card>
      </div>
    </>
  );
}
