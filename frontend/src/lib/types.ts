// ─── Chat & Messaging ────────────────────────────────────────────────────────

export type MessageRole = 'user' | 'assistant';

export interface ChartData {
  type: string;
  data: Record<string, unknown>;
  layout?: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  chart?: ChartData | null;
  timestamp: Date;
  isLoading?: boolean;
}

// ─── Threads ─────────────────────────────────────────────────────────────────

export interface Thread {
  id: string;
  label: string;
}

// ─── Files ───────────────────────────────────────────────────────────────────

export interface UploadedFile {
  name: string;
  type: string;
  size: string;
}

// ─── API Response Types ───────────────────────────────────────────────────────

export interface ChatAPIResponse {
  response: string;
  thread_id: string;
  chart?: ChartData | null;
}

export interface ThreadsAPIResponse {
  threads: string[];
}

export interface FilesAPIResponse {
  files: UploadedFile[];
}

export interface UploadAPIResponse {
  message: string;
  filename: string;
}

// ─── Streaming ───────────────────────────────────────────────────────────────

/** Callback invoked for each streamed token. */
export type StreamTokenCallback = (token: string) => void;
/** Callback invoked when streaming is complete with the full response. */
export type StreamCompleteCallback = (full: ChatAPIResponse) => void;
