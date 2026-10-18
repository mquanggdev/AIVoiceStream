"""Nhãn tiếng Việt cho các mã enum trong dữ liệu (dùng khi agent nói với khách)."""

VIEW_LABELS = {
    "ho_ngoc_trai": "view hồ Ngọc Trai",
    "bien_ho": "view biển hồ",
    "ho_canh_quan": "view hồ cảnh quan nội khu",
    "vuon_nhat": "view vườn Nhật",
    "cong_vien": "view công viên",
    "noi_khu": "view nội khu",
    "thanh_pho": "view thành phố",
}
# từ khóa khách hay nói → mã view
VIEW_KEYWORDS = [
    ("ngoc trai", "ho_ngoc_trai"),
    ("bien", "bien_ho"),
    ("lagoon", "bien_ho"),
    ("vuon nhat", "vuon_nhat"),
    ("cong vien", "cong_vien"),
    ("noi khu", "noi_khu"),
    ("thanh pho", "thanh_pho"),
    ("ho canh quan", "ho_canh_quan"),
    ("ho", "ho_ngoc_trai"),
]
DIRECTION_LABELS = {
    "N": "Bắc", "S": "Nam", "E": "Đông", "W": "Tây",
    "NE": "Đông Bắc", "NW": "Tây Bắc", "SE": "Đông Nam", "SW": "Tây Nam",
}
DIRECTION_KEYWORDS = {
    "dong nam": "SE", "tay nam": "SW", "dong bac": "NE", "tay bac": "NW",
    "dong": "E", "tay": "W", "nam": "S", "bac": "N",
}
STATUS_LABELS = {
    "available": "đang mở bán",
    "booked": "đã có khách đặt chỗ",
    "sold": "đã bán",
    "not_released": "chưa mở bán",
    "unknown": "chưa rõ tình trạng",
}
PRICE_TYPE_LABELS = {
    "cdt_list": "giá niêm yết của chủ đầu tư",
    "secondary_asking": "giá chủ nhà rao bán tham khảo",
    "secondary_sold": "giá đã giao dịch tham khảo",
    "estimate": "giá ước tính",
}
FURNISHING_LABELS = {
    "raw": "bàn giao thô",
    "basic": "bàn giao cơ bản",
    "full_built_in": "nội thất liền tường",
    "full_furnished": "full nội thất",
}
HANDOVER_LABELS = {
    "handed_over": "đã bàn giao",
    "under_construction": "đang xây dựng",
    "not_started": "chưa khởi công",
    "unknown": "chưa rõ",
}
UNIT_TYPE_LABELS = {
    "STUDIO": "studio",
    "1PN": "1 phòng ngủ",
    "1PN+1": "1 phòng ngủ + 1",
    "2PN": "2 phòng ngủ",
    "2PN+1": "2 phòng ngủ + 1",
    "3PN": "3 phòng ngủ",
    "4PN": "4 phòng ngủ",
    "DUPLEX": "duplex",
    "PENTHOUSE": "penthouse",
    "SHOPHOUSE": "shophouse",
}
POLICY_TYPE_LABELS = {
    "payment_schedule": "lịch thanh toán",
    "discount": "chiết khấu",
    "loan_support": "hỗ trợ vay",
    "gift": "quà tặng",
    "other": "chính sách khác",
}
