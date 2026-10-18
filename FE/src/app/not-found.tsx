import Link from "next/link";

export default function NotFound() {
  return (
    <section className="flex min-h-[60vh] flex-col items-center justify-center px-6 py-20 text-center">
      <span className="text-6xl font-extrabold text-cyan-500">404</span>
      <h1 className="mt-4 text-2xl font-bold text-slate-900">Chưa tìm thấy trang</h1>
      <p className="mt-2 max-w-md text-slate-500">Đường dẫn chưa chính xác hoặc trang đã được chuyển đi.</p>
      <Link
        className="mt-6 rounded-lg bg-cyan-500 px-5 py-2.5 text-sm font-bold text-slate-950 transition hover:bg-cyan-400"
        href="/phan-khu"
      >
        Quay lại danh sách phân khu
      </Link>
    </section>
  );
}
