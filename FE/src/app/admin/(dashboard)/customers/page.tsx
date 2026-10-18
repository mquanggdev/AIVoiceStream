"use client";

/** Khách để lại tên + SĐT trong cuộc gọi voice. */

import { ColumnDef } from "@tanstack/react-table";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/admin/data-table";
import { Badge, Button, Card, Field, PageHeader, Select, TextInput } from "@/components/admin/ui";
import type { Customer } from "@/lib/admin-types";
import { adminFetch } from "@/lib/auth";
import { customerStatusMeta, formatDateTime, formatMoney, unitTypeLabel } from "@/lib/labels";

export default function CustomersPage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);

  function load(nextStatus = status) {
    const params = new URLSearchParams({ limit: "500" });
    if (search.trim()) params.set("search", search.trim());
    if (nextStatus) params.set("status", nextStatus);
    setLoading(true);
    adminFetch(`/admin/customers?${params}`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setCustomers)
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const columns = useMemo<ColumnDef<Customer, unknown>[]>(
    () => [
      {
        header: "Khách hàng",
        accessorKey: "full_name",
        cell: ({ row }) => (
          <div>
            <p className="font-semibold text-slate-900">{row.original.full_name || "Chưa rõ tên"}</p>
            <p className="font-mono text-xs text-slate-500">{row.original.phone}</p>
          </div>
        ),
      },
      {
        header: "Nhu cầu",
        accessorKey: "need_summary",
        cell: ({ row }) => (
          <div className="max-w-md">
            <p className="line-clamp-2 text-slate-700">{row.original.need_summary || "—"}</p>
            <p className="mt-1 text-xs text-slate-500">
              {[
                row.original.interested_subdivision,
                row.original.preferred_unit_type && unitTypeLabel[row.original.preferred_unit_type],
                row.original.budget_max_vnd && `≤ ${formatMoney(row.original.budget_max_vnd)}`,
              ]
                .filter(Boolean)
                .join(" · ")}
            </p>
          </div>
        ),
      },
      { header: "Giờ tiện liên hệ", accessorKey: "preferred_contact_time", cell: ({ getValue }) => String(getValue() ?? "—") },
      {
        header: "Trạng thái",
        accessorKey: "status",
        cell: ({ getValue }) => {
          const meta = customerStatusMeta[String(getValue())] ?? { label: String(getValue()), tone: "slate" as const };
          return <Badge tone={meta.tone}>{meta.label}</Badge>;
        },
      },
      { header: "Cập nhật", accessorKey: "updated_at", cell: ({ getValue }) => formatDateTime(String(getValue())) },
    ],
    []
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    load();
  }

  return (
    <>
      <PageHeader
        description="Tên và số điện thoại agent ghi nhận qua giọng nói (đã đọc lại để khách xác nhận)."
        kicker="Khách hàng"
        title="Khách để lại thông tin"
      />
      <Card>
        <form className="mb-4 grid items-end gap-3 sm:grid-cols-[1fr_200px_auto]" onSubmit={submit}>
          <Field label="Tìm theo tên hoặc SĐT">
            <TextInput onChange={(e) => setSearch(e.target.value)} placeholder="Nhập tên hoặc số điện thoại" value={search} />
          </Field>
          <Field label="Trạng thái">
            <Select
              onChange={(e) => {
                setStatus(e.target.value);
                load(e.target.value);
              }}
              value={status}
            >
              <option value="">Tất cả</option>
              {Object.entries(customerStatusMeta).map(([value, meta]) => (
                <option key={value} value={value}>
                  {meta.label}
                </option>
              ))}
            </Select>
          </Field>
          <Button type="submit" variant="primary">
            Tìm
          </Button>
        </form>
        <DataTable
          columns={columns}
          data={customers}
          emptyMessage="Chưa có khách nào để lại thông tin qua cuộc gọi."
          loading={loading}
          onRowClick={(row) => router.push(`/admin/customers/${row.id}`)}
        />
      </Card>
    </>
  );
}
