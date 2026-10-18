/**
 * Thu âm micro + phát hiện ngắt câu (VAD năng lượng) → trả về từng câu nói dạng WAV 16 kHz mono.
 *
 * - Hiệu chỉnh tiếng ồn nền 600 ms TRƯỚC khi agent chào; sau đó chỉ cập nhật khi agent im lặng
 *   (dùng loa ngoài, tiếng agent vọng vào micro không được tính là "ồn nền" — nếu không ngưỡng sẽ trôi lên mãi).
 * - Khi agent đang nói: theo dõi riêng mức tiếng vọng; khách phải nói to hơn hẳn tiếng vọng mới tính là ngắt lời.
 * - Giữ ngưỡng cao thêm 400 ms sau khi agent nói xong (đuôi tiếng vọng).
 * - Giữ 400 ms âm thanh trước thời điểm phát hiện tiếng nói để không mất âm đầu.
 */

const TARGET_SAMPLE_RATE = 16_000;
const FRAME_MS = 20;
const PRE_ROLL_MS = 400;
const CALIBRATION_MS = 600;
const SILENCE_END_MS = 700;
const MIN_SPEECH_MS = 350;
const MAX_UTTERANCE_MS = 25_000;
const START_FRAMES = 3; // 60 ms liên tục trên ngưỡng
const BARGE_IN_FRAMES = 12; // 240 ms khi agent đang nói
const BARGE_IN_FACTOR = 1.8;
const ECHO_FACTOR = 3; // ngắt lời: phải to gấp 3 lần mức tiếng vọng
const ECHO_TAIL_MS = 400;
const MIN_THRESHOLD = 0.008;
const MAX_THRESHOLD = 0.05;
const MAX_NOISE_FLOOR = 0.012;
const MAX_BARGE_IN_THRESHOLD = 0.15;
const CALIBRATION_TIMEOUT_MS = 2_000;

const WORKLET_SOURCE = `
class CaptureProcessor extends AudioWorkletProcessor {
  constructor() { super(); this.buffer = []; this.size = 0; this.target = Math.round(sampleRate * ${FRAME_MS} / 1000); }
  process(inputs) {
    const channel = inputs[0] && inputs[0][0];
    if (channel) {
      this.buffer.push(channel.slice(0));
      this.size += channel.length;
      if (this.size >= this.target) {
        const out = new Float32Array(this.size);
        let offset = 0;
        for (const chunk of this.buffer) { out.set(chunk, offset); offset += chunk.length; }
        this.port.postMessage(out, [out.buffer]);
        this.buffer = []; this.size = 0;
      }
    }
    return true;
  }
}
registerProcessor("capture-processor", CaptureProcessor);
`;

export type CaptureCallbacks = {
  onSpeechStart: () => void;
  onUtterance: (wav: Blob, durationMs: number) => void;
  onDiscard?: () => void;
  onLevel?: (level: number, threshold: number) => void;
};

export class VoiceCapture {
  private context: AudioContext | null = null;
  private stream: MediaStream | null = null;
  private node: AudioWorkletNode | null = null;
  private sampleRate = 48_000;

  private calibrated = false;
  private calibrationLevels: number[] = [];
  private onCalibrated: (() => void) | null = null;
  private noiseFloor = 0.004;
  private echoFloor = 0.004;
  private agentSpeakingNow = false;
  private echoTailUntil = 0;
  private aboveCount = 0;
  private belowMs = 0;
  private speaking = false;
  private speechMs = 0;
  private preRoll: Float32Array[] = [];
  private preRollSamples = 0;
  private utterance: Float32Array[] = [];
  private paused = false;

  /** true khi agent đang phát âm thanh → ngưỡng ngắt lời cao hơn. */
  get agentSpeaking() {
    return this.agentSpeakingNow;
  }

  set agentSpeaking(value: boolean) {
    if (this.agentSpeakingNow && !value) this.echoTailUntil = performance.now() + ECHO_TAIL_MS;
    if (!this.agentSpeakingNow && value) this.echoFloor = Math.max(this.echoFloor, this.noiseFloor);
    this.agentSpeakingNow = value;
  }

  private get echoActive() {
    return this.agentSpeakingNow || performance.now() < this.echoTailUntil;
  }

  constructor(private callbacks: CaptureCallbacks) {}

  async start() {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 },
    });
    this.context = new AudioContext();
    this.sampleRate = this.context.sampleRate;
    const moduleUrl = URL.createObjectURL(new Blob([WORKLET_SOURCE], { type: "application/javascript" }));
    await this.context.audioWorklet.addModule(moduleUrl);
    URL.revokeObjectURL(moduleUrl);
    const source = this.context.createMediaStreamSource(this.stream);
    this.node = new AudioWorkletNode(this.context, "capture-processor");
    this.node.port.onmessage = (event: MessageEvent<Float32Array>) => this.handleFrame(event.data);
    source.connect(this.node);
    // không nối ra loa (tránh tự nghe lại giọng mình)

    // Chờ đo xong tiếng ồn nền (lúc chưa phát âm thanh nào) rồi mới cho agent chào
    await new Promise<void>((resolve) => {
      this.onCalibrated = resolve;
      setTimeout(resolve, CALIBRATION_TIMEOUT_MS);
    });
  }

  pause() {
    this.paused = true;
    this.resetUtterance();
  }

  resume() {
    this.paused = false;
  }

  async stop() {
    this.node?.disconnect();
    this.stream?.getTracks().forEach((track) => track.stop());
    await this.context?.close().catch(() => undefined);
    this.node = null;
    this.stream = null;
    this.context = null;
  }

  private get threshold() {
    const base = Math.min(MAX_THRESHOLD, Math.max(MIN_THRESHOLD, this.noiseFloor * 3.5));
    if (!this.echoActive) return base;
    return Math.min(MAX_BARGE_IN_THRESHOLD, Math.max(base * BARGE_IN_FACTOR, this.echoFloor * ECHO_FACTOR));
  }

  private handleFrame(frame: Float32Array) {
    let sum = 0;
    for (let i = 0; i < frame.length; i++) sum += frame[i] * frame[i];
    const level = Math.sqrt(sum / frame.length);
    const frameMs = (frame.length / this.sampleRate) * 1000;

    if (!this.calibrated) {
      this.calibrationLevels.push(level);
      if (this.calibrationLevels.length * frameMs >= CALIBRATION_MS) {
        const sorted = [...this.calibrationLevels].sort((a, b) => a - b);
        this.noiseFloor = Math.min(MAX_NOISE_FLOOR, Math.max(0.002, sorted[Math.floor(sorted.length / 2)]));
        this.echoFloor = this.noiseFloor;
        this.calibrated = true;
        this.onCalibrated?.();
      }
      return;
    }

    this.callbacks.onLevel?.(level, this.threshold);
    if (this.paused) return;

    if (!this.speaking) {
      this.pushPreRoll(frame);
      if (level > this.threshold) {
        this.aboveCount += 1;
        const needed = this.echoActive ? BARGE_IN_FRAMES : START_FRAMES;
        if (this.aboveCount >= needed) {
          this.speaking = true;
          this.speechMs = 0;
          this.belowMs = 0;
          this.utterance = [...this.preRoll];
          this.callbacks.onSpeechStart();
        }
      } else {
        this.aboveCount = 0;
        if (this.agentSpeakingNow) {
          // đang phát tiếng agent: học mức tiếng vọng (nhanh), KHÔNG đụng tới ồn nền
          this.echoFloor = this.echoFloor * 0.95 + level * 0.05;
        } else if (!this.echoActive) {
          // im lặng thật: cập nhật dần ồn nền, có trần để không trôi lên quá cao
          this.noiseFloor = Math.min(MAX_NOISE_FLOOR, this.noiseFloor * 0.98 + level * 0.02);
        }
      }
      return;
    }

    this.utterance.push(frame);
    this.speechMs += frameMs;
    if (level < this.threshold * 0.8) {
      this.belowMs += frameMs;
    } else {
      this.belowMs = 0;
    }
    if (this.belowMs >= SILENCE_END_MS || this.speechMs >= MAX_UTTERANCE_MS) {
      this.finishUtterance();
    }
  }

  private pushPreRoll(frame: Float32Array) {
    this.preRoll.push(frame);
    this.preRollSamples += frame.length;
    const maxSamples = (PRE_ROLL_MS / 1000) * this.sampleRate;
    while (this.preRollSamples > maxSamples && this.preRoll.length > 1) {
      this.preRollSamples -= this.preRoll.shift()!.length;
    }
  }

  private finishUtterance() {
    const chunks = this.utterance;
    const spokenMs = this.speechMs - this.belowMs;
    this.resetUtterance();
    if (spokenMs < MIN_SPEECH_MS) {
      this.callbacks.onDiscard?.();
      return;
    }
    const samples = mergeChunks(chunks);
    const wav = encodeWav(downsample(samples, this.sampleRate, TARGET_SAMPLE_RATE), TARGET_SAMPLE_RATE);
    this.callbacks.onUtterance(wav, Math.round((samples.length / this.sampleRate) * 1000));
  }

  private resetUtterance() {
    this.speaking = false;
    this.aboveCount = 0;
    this.belowMs = 0;
    this.speechMs = 0;
    this.utterance = [];
    this.preRoll = [];
    this.preRollSamples = 0;
  }
}

function mergeChunks(chunks: Float32Array[]) {
  const length = chunks.reduce((total, chunk) => total + chunk.length, 0);
  const out = new Float32Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    out.set(chunk, offset);
    offset += chunk.length;
  }
  return out;
}

function downsample(samples: Float32Array, fromRate: number, toRate: number) {
  if (fromRate === toRate) return samples;
  const ratio = fromRate / toRate;
  const length = Math.floor(samples.length / ratio);
  const out = new Float32Array(length);
  for (let i = 0; i < length; i++) {
    const start = Math.floor(i * ratio);
    const end = Math.min(samples.length, Math.floor((i + 1) * ratio));
    let sum = 0;
    for (let j = start; j < end; j++) sum += samples[j];
    out[i] = sum / Math.max(1, end - start);
  }
  return out;
}

function encodeWav(samples: Float32Array, sampleRate: number) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  const writeString = (offset: number, value: string) => {
    for (let i = 0; i < value.length; i++) view.setUint8(offset + i, value.charCodeAt(i));
  };
  writeString(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, samples.length * 2, true);
  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Blob([view], { type: "audio/wav" });
}
