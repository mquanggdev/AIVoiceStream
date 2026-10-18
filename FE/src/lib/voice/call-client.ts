/**
 * Client cuộc gọi voice: gửi câu nói (WAV) lên backend, đọc stream NDJSON,
 * phát lần lượt từng câu trả lời (MP3) và hỗ trợ ngắt lời.
 */

import { API_URL } from "@/lib/api";

type VoiceEvent =
  | { type: "call"; session_id: string; is_demo_data: boolean }
  | { type: "state"; value: "thinking" | "speaking" }
  | { type: "transcript"; turn_index: number; text: string }
  | { type: "audio"; seq: number; filler: boolean; mime: string; data: string }
  | { type: "speak_text"; seq: number; text: string; filler?: boolean }
  | { type: "tool"; name: string }
  | { type: "done"; turn_index?: number; ended?: boolean }
  | { type: "error"; message: string };

type QueueItem = { kind: "buffer"; buffer: AudioBuffer } | { kind: "text"; text: string };

export type CallClientCallbacks = {
  onThinking: () => void;
  onSpeakingChange: (speaking: boolean) => void;
  onTurnDone: () => void;
  onError: (message: string) => void;
};

export class CallClient {
  sessionId: string | null = null;
  private output: AudioContext | null = null;
  private queue: QueueItem[] = [];
  private current: AudioBufferSourceNode | null = null;
  private playing = false;
  private streamOpen = false;
  private abort: AbortController | null = null;
  private turnIndex = 0;
  private playedSegments = 0;
  private generation = 0;

  constructor(private callbacks: CallClientCallbacks) {}

  /** Phải gọi trong sự kiện click để trình duyệt cho phép phát âm thanh. */
  unlockAudio() {
    if (!this.output) this.output = new AudioContext();
    void this.output.resume();
  }

  get isBusy() {
    return this.streamOpen || this.playing || this.queue.length > 0;
  }

  async start(): Promise<{ sessionId: string; isDemoData: boolean }> {
    let info = { sessionId: "", isDemoData: false };
    await this.run(fetchStream(`${API_URL}/voice/calls`, { method: "POST" }), (event) => {
      if (event.type === "call") {
        this.sessionId = event.session_id;
        info = { sessionId: event.session_id, isDemoData: event.is_demo_data };
      }
    });
    if (!this.sessionId) throw new Error("Không khởi tạo được cuộc gọi");
    return info;
  }

  async sendUtterance(wav: Blob) {
    if (!this.sessionId) return;
    const form = new FormData();
    form.append("session_id", this.sessionId);
    form.append("audio", wav, "turn.wav");
    this.callbacks.onThinking();
    await this.run(fetchStream(`${API_URL}/voice/turn`, { method: "POST", body: form }));
  }

  async end() {
    if (!this.sessionId) return;
    this.stopPlayback();
    await this.run(fetchStream(`${API_URL}/voice/calls/${this.sessionId}/end`, { method: "POST" }));
    this.sessionId = null; // đã kết thúc bình thường → không gửi beacon nữa
    await this.waitForPlayback();
  }

  /** Khách nói chen: dừng phát, hủy lượt đang chạy, báo backend. */
  interrupt() {
    const wasBusy = this.isBusy;
    this.abort?.abort();
    this.stopPlayback();
    if (wasBusy && this.sessionId && this.turnIndex > 0) {
      void fetch(`${API_URL}/voice/interrupt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          turn_index: this.turnIndex,
          played_segments: this.playedSegments,
        }),
      }).catch(() => undefined);
    }
  }

  /** Heartbeat: báo server cuộc gọi vẫn mở (khách có thể đang im lặng). */
  async ping(): Promise<boolean> {
    if (!this.sessionId) return false;
    try {
      const response = await fetch(`${API_URL}/voice/calls/${this.sessionId}/ping`, { method: "POST" });
      return response.ok ? Boolean((await response.json()).active) : true;
    } catch {
      return true; // mất mạng tạm thời: để server tự quyết định theo timeout
    }
  }

  /**
   * Khách đóng tab / F5 / rời trang: fetch thường bị hủy khi trang unload,
   * sendBeacon vẫn được trình duyệt gửi đi. Gửi text/plain để không cần CORS preflight.
   */
  hangupBeacon() {
    if (!this.sessionId || typeof navigator === "undefined") return;
    const url = `${API_URL}/voice/calls/${this.sessionId}/hangup`;
    const sent = navigator.sendBeacon?.(url, new Blob([], { type: "text/plain" }));
    if (!sent) void fetch(url, { method: "POST", keepalive: true }).catch(() => undefined);
    this.sessionId = null;
  }

  close() {
    this.abort?.abort();
    this.stopPlayback();
    void this.output?.close().catch(() => undefined);
    this.output = null;
  }

  private async run(
    streamFactory: (signal: AbortSignal) => AsyncGenerator<VoiceEvent>,
    onEvent?: (event: VoiceEvent) => void
  ) {
    this.abort?.abort();
    const controller = new AbortController();
    this.abort = controller;
    const generation = ++this.generation;
    this.streamOpen = true;
    this.playedSegments = 0;
    try {
      for await (const event of streamFactory(controller.signal)) {
        if (generation !== this.generation) break;
        onEvent?.(event);
        await this.handle(event);
      }
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        this.callbacks.onError("Mất kết nối tới máy chủ. Vui lòng thử lại.");
      }
    } finally {
      if (generation === this.generation) {
        this.streamOpen = false;
        if (!this.playing && this.queue.length === 0) this.callbacks.onTurnDone();
      }
    }
  }

  private async handle(event: VoiceEvent) {
    switch (event.type) {
      case "transcript":
        this.turnIndex = event.turn_index;
        break;
      case "audio": {
        const buffer = await this.decode(event.data);
        if (buffer) this.enqueue({ kind: "buffer", buffer });
        break;
      }
      case "speak_text":
        this.enqueue({ kind: "text", text: event.text });
        break;
      case "error":
        this.callbacks.onError(event.message);
        break;
      default:
        break;
    }
  }

  private async decode(base64: string): Promise<AudioBuffer | null> {
    if (!this.output) this.output = new AudioContext();
    const bytes = Uint8Array.from(atob(base64), (char) => char.charCodeAt(0));
    try {
      return await this.output.decodeAudioData(bytes.buffer);
    } catch {
      return null;
    }
  }

  private enqueue(item: QueueItem) {
    this.queue.push(item);
    if (!this.playing) void this.playNext();
  }

  private async playNext() {
    const item = this.queue.shift();
    if (!item) {
      this.playing = false;
      this.callbacks.onSpeakingChange(false);
      if (!this.streamOpen) this.callbacks.onTurnDone();
      return;
    }
    if (!this.playing) {
      this.playing = true;
      this.callbacks.onSpeakingChange(true);
    }
    const generation = this.generation;
    if (item.kind === "buffer" && this.output) {
      await new Promise<void>((resolve) => {
        const source = this.output!.createBufferSource();
        source.buffer = item.buffer;
        source.connect(this.output!.destination);
        source.onended = () => resolve();
        this.current = source;
        source.start();
      });
      this.current = null;
    } else if (item.kind === "text") {
      await speakWithBrowser(item.text);
    }
    if (generation !== this.generation) return;
    this.playedSegments += 1;
    void this.playNext();
  }

  private stopPlayback() {
    this.generation += 1;
    this.queue = [];
    try {
      this.current?.stop();
    } catch {
      // đã dừng
    }
    this.current = null;
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    if (this.playing) {
      this.playing = false;
      this.callbacks.onSpeakingChange(false);
    }
  }

  private async waitForPlayback() {
    while (this.playing || this.queue.length > 0) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
}

function fetchStream(url: string, init: RequestInit) {
  return async function* (signal: AbortSignal): AsyncGenerator<VoiceEvent> {
    const response = await fetch(url, { ...init, signal });
    if (!response.ok || !response.body) {
      let detail = `Lỗi máy chủ (${response.status})`;
      try {
        detail = (await response.json()).detail ?? detail;
      } catch {
        // không phải JSON
      }
      throw new Error(detail);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let newline = buffer.indexOf("\n");
      while (newline >= 0) {
        const line = buffer.slice(0, newline).trim();
        buffer = buffer.slice(newline + 1);
        if (line) yield JSON.parse(line) as VoiceEvent;
        newline = buffer.indexOf("\n");
      }
    }
    if (buffer.trim()) yield JSON.parse(buffer) as VoiceEvent;
  };
}

/** Dự phòng khi TTS của server lỗi: đọc bằng giọng tiếng Việt của trình duyệt. */
function speakWithBrowser(text: string): Promise<void> {
  return new Promise((resolve) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return resolve();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "vi-VN";
    const voice = window.speechSynthesis.getVoices().find((v) => v.lang.toLowerCase().startsWith("vi"));
    if (voice) utterance.voice = voice;
    utterance.onend = () => resolve();
    utterance.onerror = () => resolve();
    window.speechSynthesis.speak(utterance);
  });
}
