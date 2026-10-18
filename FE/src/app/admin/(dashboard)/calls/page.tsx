"use client";

import { useEffect, useState } from "react";

import { CallsTable } from "@/components/admin/calls-table";
import { Card, Field, PageHeader, Select } from "@/components/admin/ui";
import type { ConversationSummary } from "@/lib/admin-types";
import { adminFetch } from "@/lib/auth";

export default function CallsPage() {
  const [calls, setCalls] = useState<ConversationSummary[]>([]);
  const [status, setStatus] = useState("");
  const [lead, setLead] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams({ limit: "500" });
    if (status) params.set("status", status);
    if (lead) params.set("has_customer", lead);
    setLoading(true);
    adminFetch(`/admin/conversations?${params}`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setCalls)
      .finally(() => setLoading(false));
  }, [status, lead]);

  return (
    <>
      <PageHeader
        description="Mỗi cuộc gọi lưu đầy đủ lượt nói của Khách và AI kèm ghi âm, độ trễ và tool đã dùng để đánh giá."
        kicker="Cuộc gọi"
        title="Lịch sử cuộc gọi"
      />
      <Card>
        <div className="mb-4 grid max-w-xl gap-3 sm:grid-cols-2">
          <Field label="Trạng thái">
            <Select onChange={(e) => setStatus(e.target.value)} value={status}>
              <option value="">Tất cả</option>
              <option value="active">Đang gọi</option>
              <option value="ended">Khách kết thúc</option>
              <option value="closed">Khách đóng trang</option>
              <option value="abandoned">Mất kết nối</option>
            </Select>
          </Field>
          <Field label="Thông tin khách">
            <Select onChange={(e) => setLead(e.target.value)} value={lead}>
              <option value="">Tất cả</option>
              <option value="true">Đã để lại thông tin</option>
              <option value="false">Chưa để lại</option>
            </Select>
          </Field>
        </div>
        <CallsTable calls={calls} loading={loading} />
      </Card>
    </>
  );
}
