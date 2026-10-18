export type DatasetInfo = {
  version: string;
  is_demo: boolean;
  dataset_dir: string;
  counts: Record<string, number>;
  notes: string | null;
  embedding_model: string | null;
  imported_at: string;
};

export type DashboardStats = {
  total_calls: number;
  active_calls: number;
  total_customers: number;
  calls_with_lead: number;
  avg_turns: number;
  avg_first_audio_ms: number | null;
  fact_check_mismatch_turns: number;
  total_cost_usd: number;
  dataset: DatasetInfo | null;
  ai_configured: boolean;
};

export type ConversationSummary = {
  id: number;
  session_id: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  duration_sec: number | null;
  turn_count: number;
  customer_id: number | null;
  customer_name: string | null;
  customer_phone: string | null;
  data_version: string | null;
  avg_first_audio_ms: number | null;
  fact_check_mismatch: boolean;
  interrupted_turns: number;
  cost_usd: number;
};

export type ToolCallLog = { name: string; arguments: string; ms: number; result_preview: string };

export type MessageMeta = {
  is_filler?: boolean;
  kind?: string;
  spoken?: string;
  stt_ms?: number;
  stt_model?: string | null;
  stt_error?: string | null;
  first_audio_ms?: number | null;
  turn_total_ms?: number;
  llm_first_sentence_ms?: number;
  llm_model?: string;
  tool_calls?: ToolCallLog[];
  fact_check?: string;
  blocked_codes?: string[];
  unverified_prices?: number[];
  interrupted?: boolean;
  played_segments?: number;
  tts_failed?: number | boolean;
  error?: string;
  llm_cost_usd?: number;
  stt_cost_usd?: number | null;
  tts_cost_usd_est?: number | null;
};

export type Message = {
  id: number;
  turn_index: number;
  role: "customer" | "ai";
  content: string;
  has_audio: boolean;
  meta: MessageMeta;
  created_at: string;
};

export type ConversationDetail = ConversationSummary & {
  models: Record<string, string | null>;
  state: Record<string, unknown>;
  messages: Message[];
};

export type Customer = {
  id: number;
  full_name: string | null;
  phone: string;
  need_summary: string | null;
  interested_subdivision: string | null;
  preferred_unit_type: string | null;
  budget_max_vnd: number | null;
  preferred_contact_time: string | null;
  source: string;
  status: string;
  created_at: string;
  updated_at: string;
};
