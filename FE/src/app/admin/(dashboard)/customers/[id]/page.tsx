"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { CallsTable } from "@/components/admin/calls-table";
import { Button, Card, Field, PageHeader, Select, TextArea } from "@/components/admin/ui";
import type { ConversationSummary, Customer } from "@/lib/admin-types";
import { adminFetch } from "@/lib/auth";
import { customerStatusMeta, formatDateTime, formatMoney, unitTypeLabel } from "@/lib/labels";

export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [calls, setCalls] = useState<ConversationSummary[]>([]);
  const [status, setStatus] = useState("new");
  const [need, setNeed] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    adminFetch(`/admin/customers/${id}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (!data) return;
        setCustomer(data.customer);
        setCalls(data.conversations);
        setStatus(data.customer.status);
        setNeed(data.customer.need_summary ?? "");
      });
  }, [id]);

  async function save() {
    setSaving(true);
    setMessage("");
    const response = await adminFetch(`/admin/customers/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status, need_summary: need }),
    });
    setSaving(false);
    if (response.ok) {
      setCustomer(await response.json());
      setMessage("Đã lưu");
    } else {
      setMessage("Không lưu được");
    }
  }

  if (!customer) return <p className="text-sm text-slate-500">Đang tải...</p>;

  return (
    <>
      <PageHeader
        actions={
          <Link href="/admin/customers">
            <Button variant="ghost">← Danh sách</Button>
          </Link>
        }
        description={`Ghi nhận lúc ${formatDateTime(customer.created_at)} qua cuộc gọi voice`}
        kicker="Khách hàng"
        title={`${customer.full_name || "Chưa rõ tên"} · ${customer.phone}`}
      />
      <div className="grid gap-6 xl:grid-cols-3">
        <Card title="Thông tin agent ghi nhận">
          <dl className="space-y-2 text-sm">
            {[
              ["Phân khu quan tâm", customer.interested_subdivision ?? "—"],
              ["Loại căn", customer.preferred_unit_type ? unitTypeLabel[customer.preferred_unit_type] : "—"],
              ["Ngân sách tối đa", formatMoney(customer.budget_max_vnd)],
              ["Giờ tiện liên hệ", customer.preferred_contact_time ?? "—"],
            ].map(([label, value]) => (
              <div className="flex justify-between gap-3 border-b border-slate-100 pb-2" key={label}>
                <dt className="text-slate-500">{label}</dt>
                <dd className="text-right font-semibold text-slate-800">{value}</dd>
              </div>
            ))}
          </dl>
          <div className="mt-4 space-y-3">
            <Field label="Trạng thái xử lý">
              <Select onChange={(e) => setStatus(e.target.value)} value={status}>
                {Object.entries(customerStatusMeta).map(([value, meta]) => (
                  <option key={value} value={value}>
                    {meta.label}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Tóm tắt nhu cầu">
              <TextArea onChange={(e) => setNeed(e.target.value)} rows={4} value={need} />
            </Field>
            <div className="flex items-center gap-3">
              <Button disabled={saving} onClick={save} variant="primary">
                {saving ? "Đang lưu..." : "Lưu"}
              </Button>
              {message ? <span className="text-sm text-slate-500">{message}</span> : null}
            </div>
          </div>
        </Card>
        <Card className="xl:col-span-2" subtitle="Bấm để nghe lại" title="Các cuộc gọi">
          <CallsTable calls={calls} pageSize={10} />
        </Card>
      </div>
    </>
  );
}
