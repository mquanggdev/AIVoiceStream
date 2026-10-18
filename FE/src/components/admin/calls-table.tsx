"use client";

import { ColumnDef } from "@tanstack/react-table";
import { useRouter } from "next/navigation";
import { useMemo } from "react";

import { DataTable } from "@/components/admin/data-table";
import { Badge } from "@/components/admin/ui";
import type { ConversationSummary } from "@/lib/admin-types";
import { callStatusMeta, formatDateTime, formatDuration, formatMs, formatUsd } from "@/lib/labels";

export function CallsTable({
  calls,
  loading,
  pageSize = 15,
}: {
  calls: ConversationSummary[];
  loading?: boolean;
  pageSize?: number;
}) {
  const router = useRouter();
  const columns = useMemo<ColumnDef<ConversationSummary, unknown>[]>(
    () => [
      {
        header: "Bắt đầu",
        accessorKey: "started_at",
        cell: ({ row }) => (
          <div>
            <p className="font-semibold text-slate-900">{formatDateTime(row.original.started_at)}</p>
            <p className="font-mono text-[11px] text-slate-400">#{row.original.id}</p>
          </div>
        ),
      },
      {
        header: "Trạng thái",
        accessorKey: "status",
        cell: ({ getValue }) => {
          const meta = callStatusMeta[String(getValue())] ?? { label: String(getValue()), tone: "slate" as const };
          return <Badge tone={meta.tone}>{meta.label}</Badge>;
        },
      },
      { header: "Thời lượng", accessorKey: "duration_sec", cell: ({ getValue }) => formatDuration(getValue() as number) },
      { header: "Số lượt", accessorKey: "turn_count" },
      {
        header: "Khách",
        accessorKey: "customer_name",
        cell: ({ row }) =>
          row.original.customer_phone ? (
            <div>
              <p className="font-semibold text-slate-900">{row.original.customer_name || "—"}</p>
              <p className="text-xs text-slate-500">{row.original.customer_phone}</p>
            </div>
          ) : (
            <span className="text-slate-400">Chưa để lại</span>
          ),
      },
      {
        header: "Phản hồi TB",
        accessorKey: "avg_first_audio_ms",
        cell: ({ getValue }) => formatMs(getValue() as number | null),
      },
      {
        header: "Kiểm tra số liệu",
        accessorKey: "fact_check_mismatch",
        cell: ({ row }) => (
          <div className="flex flex-wrap gap-1">
            {row.original.fact_check_mismatch ? <Badge tone="red">Có câu bị chặn</Badge> : <Badge tone="green">OK</Badge>}
            {row.original.interrupted_turns ? <Badge tone="amber">{row.original.interrupted_turns} lần ngắt lời</Badge> : null}
          </div>
        ),
      },
      { header: "Chi phí", accessorKey: "cost_usd", cell: ({ getValue }) => formatUsd(getValue() as number) },
      {
        header: "Data",
        accessorKey: "data_version",
        cell: ({ getValue }) => <span className="font-mono text-xs text-slate-500">{String(getValue() ?? "—")}</span>,
      },
    ],
    []
  );

  return (
    <DataTable
      columns={columns}
      data={calls}
      emptyMessage="Chưa có cuộc gọi nào. Mở website và bấm “Gọi tư vấn” để thử."
      loading={loading}
      onRowClick={(row) => router.push(`/admin/calls/${row.id}`)}
      pageSize={pageSize}
    />
  );
}
