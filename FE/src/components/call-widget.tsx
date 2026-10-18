"use client";

/**
 * Giao diện cuộc gọi tư vấn bằng giọng nói. Khách chỉ nghe và nói, không hiện phụ đề.
 * Luồng: bấm "Gọi tư vấn" → agent chào → khách nói tự nhiên (tự nhận ngắt câu) → agent trả lời bằng giọng nói.
 */

import Image from "next/image";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { CallClient } from "@/lib/voice/call-client";
import { VoiceCapture } from "@/lib/voice/capture";

type CallState =
  | "idle"
  | "connecting"
  | "listening"
  | "user_speaking"
  | "thinking"
  | "speaking"
  | "ending"
  | "ended"
  | "error";

const STATUS_TEXT: Record<CallState, string> = {
  idle: "",
  connecting: "Đang kết nối...",
  listening: "Đang nghe anh chị...",
  user_speaking: "Đang nghe anh chị...",
  thinking: "Đang xử lý...",
  speaking: "Đang nói...",
  ending: "Đang kết thúc cuộc gọi...",
  ended: "Cuộc gọi đã kết thúc",
  error: "Có lỗi xảy ra",
};

const HEARTBEAT_MS = 20_000;

function formatTimer(seconds: number) {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export function CallWidget() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [state, setState] = useState<CallState>("idle");
  const [error, setError] = useState("");
  const [seconds, setSeconds] = useState(0);
  const [level, setLevel] = useState(0);
  const [muted, setMuted] = useState(false);

  const clientRef = useRef<CallClient | null>(null);
  const captureRef = useRef<VoiceCapture | null>(null);
  const stateRef = useRef<CallState>("idle");
  const startedAtRef = useRef<number>(0);

  const updateState = useCallback((next: CallState) => {
    stateRef.current = next;
    setState(next);
  }, []);

  const cleanup = useCallback(async () => {
    // Cuộc gọi còn mở (lỗi giữa chừng, rời trang...) → báo server đóng ngay thay vì để treo
    clientRef.current?.hangupBeacon();
    await captureRef.current?.stop();
    captureRef.current = null;
    clientRef.current?.close();
    clientRef.current = null;
  }, []);

  useEffect(() => {
    if (!["listening", "user_speaking", "thinking", "speaking"].includes(state)) return;
    const timer = setInterval(() => setSeconds(Math.floor((Date.now() - startedAtRef.current) / 1000)), 500);
    return () => clearInterval(timer);
  }, [state]);

  useEffect(() => () => void cleanup(), [cleanup]);

  // F5 / đóng tab / chuyển trang: JS bị hủy nên phải dùng sendBeacon để server biết cuộc gọi đã đóng
  useEffect(() => {
    const onPageHide = () => clientRef.current?.hangupBeacon();
    window.addEventListener("pagehide", onPageHide);
    return () => window.removeEventListener("pagehide", onPageHide);
  }, []);

  // Heartbeat 20s/lần: server đóng cuộc gọi "mất kết nối" nếu quá 90s không có ping hay lượt nói.
  // Chỉ phụ thuộc "cuộc gọi đang mở" — nếu phụ thuộc state, interval bị reset mỗi lần đổi nghe/nói.
  const callOpen = ["listening", "user_speaking", "thinking", "speaking"].includes(state);
  useEffect(() => {
    if (!callOpen) return;
    const timer = setInterval(async () => {
      const client = clientRef.current;
      if (!client) return;
      const active = await client.ping();
      if (!active && clientRef.current === client) {
        setError("Cuộc gọi đã bị ngắt do mất kết nối. Anh chị bấm Gọi lại để tiếp tục.");
        await cleanup();
        updateState("ended");
      }
    }, HEARTBEAT_MS);
    return () => clearInterval(timer);
  }, [callOpen, cleanup, updateState]);

  if (pathname?.startsWith("/admin")) return null;

  const isLive = ["listening", "user_speaking", "thinking", "speaking"].includes(state);

  async function startCall() {
    setOpen(true);
    setError("");
    setSeconds(0);
    setMuted(false);
    updateState("connecting");

    const client = new CallClient({
      onThinking: () => updateState("thinking"),
      onSpeakingChange: (speaking) => {
        if (captureRef.current) captureRef.current.agentSpeaking = speaking;
        if (speaking) updateState("speaking");
      },
      onTurnDone: () => {
        if (["speaking", "thinking", "connecting"].includes(stateRef.current)) updateState("listening");
      },
      onError: (message) => setError(message),
    });
    client.unlockAudio();
    clientRef.current = client;

    const capture = new VoiceCapture({
      onSpeechStart: () => {
        if (client.isBusy) client.interrupt();
        updateState("user_speaking");
      },
      onUtterance: (wav) => {
        void client.sendUtterance(wav);
      },
      onDiscard: () => {
        if (stateRef.current === "user_speaking") updateState(client.isBusy ? "speaking" : "listening");
      },
      onLevel: (value, threshold) => setLevel(Math.min(1, value / (threshold * 2))),
    });

    // Hiệu chỉnh tiếng ồn nền TRƯỚC khi agent chào (tránh đo nhầm tiếng loa → ngưỡng quá cao)

    try {
      await capture.start();
    } catch {
      setError("Không truy cập được micro. Anh chị vui lòng cho phép trình duyệt dùng micro rồi thử lại.");
      updateState("error");
      await cleanup();
      return;
    }
    captureRef.current = capture;

    try {
      startedAtRef.current = Date.now();
      await client.start();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Không kết nối được tổng đài tư vấn.");
      updateState("error");
      await cleanup();
    }
  }

  async function endCall() {
    if (!clientRef.current) {
      setOpen(false);
      updateState("idle");
      return;
    }
    updateState("ending");
    await captureRef.current?.stop();
    captureRef.current = null;
    try {
      await clientRef.current.end();
    } finally {
      await cleanup();
      updateState("ended");
    }
  }

  function toggleMute() {
    const capture = captureRef.current;
    if (!capture) return;
    if (muted) capture.resume();
    else capture.pause();
    setMuted(!muted);
  }

  function closePanel() {
    setOpen(false);
    updateState("idle");
  }

  const ringScale = state === "user_speaking" || state === "listening" ? 1 + level * 0.35 : 1;

  return (
    <>
      {!open ? (
        <button
          aria-label="Gọi tư vấn bằng giọng nói"
          className="fixed bottom-6 right-6 z-[60] flex items-center gap-3 rounded-full bg-cyan-500 py-3 pl-3 pr-5 font-bold text-slate-950 shadow-xl shadow-cyan-500/30 transition hover:bg-cyan-400"
          onClick={startCall}
          type="button"
        >
          <span className="relative flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-cyan-300">
            <span className="absolute inset-0 animate-ping rounded-full bg-cyan-400/40" />
            <PhoneIcon />
          </span>
          Gọi tư vấn
        </button>
      ) : null}

      {open ? (
        <div className="fixed inset-0 z-[70] flex items-end justify-center bg-slate-950/50 p-4 backdrop-blur-sm sm:items-center">
          <section
            aria-live="polite"
            className="w-full max-w-sm overflow-hidden rounded-3xl bg-gradient-to-b from-slate-900 via-slate-950 to-slate-950 text-white shadow-2xl"
          >
            <header className="px-6 pt-6 text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Vinhomes Ocean Park</p>
              <p className="mt-1 font-mono text-sm text-slate-400">{isLive ? formatTimer(seconds) : " "}</p>
            </header>

            <div className="flex flex-col items-center px-6 py-8">
              <div className="relative flex h-44 w-44 items-center justify-center">
                <span
                  className={`absolute inset-0 rounded-full bg-cyan-400/10 transition-transform duration-100 ${
                    state === "speaking" ? "animate-pulse" : ""
                  }`}
                  style={{ transform: `scale(${ringScale})` }}
                />
                <span
                  className={`absolute inset-4 rounded-full border-2 ${
                    state === "speaking"
                      ? "border-cyan-300"
                      : state === "user_speaking"
                        ? "border-emerald-300"
                        : "border-white/10"
                  }`}
                />
                <Image
                  alt="Trợ lý tư vấn Mai"
                  className="relative rounded-full object-cover ring-4 ring-slate-800"
                  height={112}
                  src="/media_files/advisor-avatar.jpg"
                  width={112}
                />
              </div>
              <h2 className="mt-5 text-xl font-bold">Mai</h2>
              <p className="text-sm text-slate-400">Trợ lý tư vấn căn hộ</p>
              <p className="mt-4 flex h-6 items-center gap-2 text-sm font-semibold text-cyan-200">
                {state === "thinking" ? <Dots /> : null}
                {STATUS_TEXT[state]}
              </p>
              {muted && isLive ? <p className="mt-1 text-xs text-amber-300">Micro đang tắt</p> : null}
              {isLive && !muted ? (
                <div aria-hidden className="mt-3 h-1 w-32 overflow-hidden rounded-full bg-white/10" title="Mức micro">
                  <div
                    className={`h-full rounded-full transition-[width] duration-75 ${level >= 0.5 ? "bg-emerald-400" : "bg-slate-500"}`}
                    style={{ width: `${Math.round(level * 100)}%` }}
                  />
                </div>
              ) : null}
              {error ? <p className="mt-3 text-center text-sm text-red-300">{error}</p> : null}
            </div>

            <footer className="flex items-center justify-center gap-6 border-t border-white/5 bg-black/20 px-6 py-5">
              {isLive ? (
                <>
                  <button
                    aria-label={muted ? "Bật micro" : "Tắt micro"}
                    className={`flex h-14 w-14 items-center justify-center rounded-full transition ${
                      muted ? "bg-amber-400 text-slate-950" : "bg-white/10 text-white hover:bg-white/20"
                    }`}
                    onClick={toggleMute}
                    type="button"
                  >
                    <MicIcon muted={muted} />
                  </button>
                  <button
                    aria-label="Kết thúc cuộc gọi"
                    className="flex h-14 w-14 items-center justify-center rounded-full bg-red-500 text-white shadow-lg shadow-red-500/30 transition hover:bg-red-400"
                    onClick={endCall}
                    type="button"
                  >
                    <PhoneIcon hangup />
                  </button>
                </>
              ) : state === "connecting" || state === "ending" ? (
                <button
                  className="rounded-full bg-white/10 px-6 py-3 text-sm font-semibold text-slate-300"
                  disabled
                  type="button"
                >
                  {STATUS_TEXT[state]}
                </button>
              ) : (
                <>
                  <button
                    className="rounded-full bg-white/10 px-5 py-3 text-sm font-semibold transition hover:bg-white/20"
                    onClick={closePanel}
                    type="button"
                  >
                    Đóng
                  </button>
                  <button
                    className="rounded-full bg-cyan-500 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-400"
                    onClick={startCall}
                    type="button"
                  >
                    Gọi lại
                  </button>
                </>
              )}
            </footer>
            <p className="px-6 pb-4 text-center text-[11px] text-slate-500">
              Nên dùng tai nghe để cuộc gọi rõ hơn. Cuộc gọi được ghi âm để nâng cao chất lượng tư vấn.
            </p>
          </section>
        </div>
      ) : null}
    </>
  );
}

function Dots() {
  return (
    <span className="flex gap-1">
      {[0, 150, 300].map((delay) => (
        <span
          className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-300"
          key={delay}
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </span>
  );
}

function PhoneIcon({ hangup = false }: { hangup?: boolean }) {
  return (
    <svg
      aria-hidden
      className={`h-6 w-6 ${hangup ? "rotate-[135deg]" : ""}`}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      viewBox="0 0 24 24"
    >
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );
}

function MicIcon({ muted }: { muted: boolean }) {
  return (
    <svg aria-hidden className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <rect height="12" rx="3" width="6" x="9" y="2" />
      <path d="M19 10v1a7 7 0 0 1-14 0v-1M12 18v4M8 22h8" strokeLinecap="round" />
      {muted ? <path d="M3 3l18 18" strokeLinecap="round" /> : null}
    </svg>
  );
}
