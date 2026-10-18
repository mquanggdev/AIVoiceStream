/** Nhãn tiếng Việt cho enum hiển thị trên trang admin. */

export type BadgeTone = "slate" | "cyan" | "green" | "amber" | "red" | "violet" | "blue";

type LabeledValue = { label: string; tone: BadgeTone };

export const customerStatusMeta: Record<string, LabeledValue> = {
  new: { label: "Mới", tone: "cyan" },
  contacted: { label: "Đã liên hệ", tone: "blue" },
  closed: { label: "Đã xử lý", tone: "green" },
};

export const callStatusMeta: Record<string, LabeledValue> = {
  active: { label: "Đang gọi", tone: "green" },
  ended: { label: "Khách kết thúc", tone: "slate" },
  closed: { label: "Khách đóng trang", tone: "blue" },
  abandoned: { label: "Mất kết nối", tone: "amber" },
};

export const unitTypeLabel: Record<string, string> = {
  STUDIO: "Studio",
  "1PN": "1 phòng ngủ",
  "1PN+1": "1 phòng ngủ + 1",
  "2PN": "2 phòng ngủ",
  "2PN+1": "2 phòng ngủ + 1",
  "3PN": "3 phòng ngủ",
  "4PN": "4 phòng ngủ",
};

export const toolLabel: Record<string, string> = {
  search_units: "Tìm căn",
  get_unit: "Tra mã căn",
  get_subdivision: "Thông tin phân khu",
  list_subdivisions: "Danh sách phân khu",
  compare_subdivisions: "So sánh phân khu",
  get_sales_policy: "Chính sách bán hàng",
  search_knowledge: "Tìm tài liệu",
  save_customer_info: "Lưu thông tin khách",
};

export function formatMoney(vnd: number | null | undefined) {
  if (!vnd) return "—";
  if (vnd >= 1_000_000_000) return `${(vnd / 1_000_000_000).toLocaleString("vi-VN", { maximumFractionDigits: 2 })} tỷ`;
  return `${Math.round(vnd / 1_000_000).toLocaleString("vi-VN")} triệu`;
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) return "—";
  const date = new Date(value.endsWith("Z") || value.includes("+") ? value : `${value}Z`);
  return date.toLocaleString("vi-VN", { hour12: false });
}

export function formatDuration(seconds: number | null | undefined) {
  if (seconds == null) return "—";
  const minutes = Math.floor(seconds / 60);
  const rest = Math.round(seconds % 60);
  return minutes ? `${minutes} phút ${rest} giây` : `${rest} giây`;
}

export function formatMs(ms: number | null | undefined) {
  if (ms == null) return "—";
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)} s` : `${ms} ms`;
}

export function formatUsd(value: number | null | undefined) {
  if (value == null) return "—";
  if (value === 0) return "$0";
  // số rất nhỏ (STT một lượt ~ $0.00002) hiển thị theo cent để không trông như bằng 0
  if (value < 0.001) return `${Number((value * 100).toPrecision(2))}¢`;
  return `$${value < 0.01 ? value.toFixed(4) : value.toFixed(3)}`;
}
