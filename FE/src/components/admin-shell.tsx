"use client";

/** Khung admin — sidebar slate-950 + accent cyan, đồng bộ theme public site. */

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

import { AdminUser, adminFetch, TOKEN_KEY } from "@/lib/auth";

const navigation = [
  { href: "/admin", label: "Tổng quan", icon: "📊" },
  { href: "/admin/calls", label: "Cuộc gọi", icon: "📞" },
  { href: "/admin/customers", label: "Khách để lại thông tin", icon: "👥" },
];

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<AdminUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    adminFetch("/auth/me")
      .then(async (response) => {
        if (response.ok) setMe(await response.json());
      })
      .finally(() => setReady(true));
  }, []);

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    router.replace("/admin/login");
  }

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-slate-500">
        Đang xác thực phiên làm việc...
      </div>
    );
  }
  if (!me) return null;

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 flex w-60 flex-col bg-slate-950 text-slate-300">
        <Link className="flex items-center gap-3 px-5 py-5" href="/admin">
          <Image
            alt="Ocean Park Voice Agent"
            className="rounded-lg object-cover"
            height={36}
            src="/media_files/advisor-avatar.jpg"
            width={36}
          />
          <span className="text-sm font-bold text-white">
            Ocean Park
            <span className="block text-[11px] font-medium text-slate-400">Trợ lý tư vấn giọng nói</span>
          </span>
        </Link>

        <nav className="mt-2 flex-1 space-y-1 px-3">
          {navigation.map((item) => {
            const active =
              pathname === item.href || (item.href !== "/admin" && pathname.startsWith(`${item.href}/`));
            return (
              <Link
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  active ? "bg-cyan-500/15 text-cyan-300" : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`}
                href={item.href}
                key={item.href}
              >
                <span aria-hidden>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-white/10 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-cyan-500/20 text-sm font-bold text-cyan-300">
              {me.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-white">{me.full_name}</p>
              <p className="truncate text-xs text-slate-400">{me.email}</p>
            </div>
            <button
              className="rounded-lg p-1.5 text-slate-400 transition hover:bg-white/10 hover:text-white"
              onClick={logout}
              title="Đăng xuất"
              type="button"
            >
              ⎋
            </button>
          </div>
        </div>
      </aside>

      <div className="ml-60 flex min-h-screen flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/90 px-6 py-3 backdrop-blur">
          <p className="text-sm font-semibold text-slate-700">Vinhomes Ocean Park · Quản trị trợ lý giọng nói</p>
          <Link className="text-sm font-semibold text-cyan-600 transition hover:text-cyan-500" href="/" target="_blank">
            Xem website ↗
          </Link>
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
