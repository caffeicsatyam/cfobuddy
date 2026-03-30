import type {
  ChatAPIResponse,
  ThreadsAPIResponse,
  FilesAPIResponse,
  UploadAPIResponse,
  StreamTokenCallback,
  StreamCompleteCallback,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? '';

function headers(extra: Record<string, string> = {}): HeadersInit {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${API_KEY}`,
    ...extra,
  };
}

// ─── Chat (non-streaming fallback) ───────────────────────────────────────────

export async function sendMessage(
  message: string,
  threadId: string
): Promise<ChatAPIResponse> {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ message, thread_id: threadId }),
  });
  if (!res.ok) throw new Error(`Chat error: ${res.statusText}`);
  return res.json() as Promise<ChatAPIResponse>;
}

// ─── Streaming Chat (SSE / chunked) ──────────────────────────────────────────
/**
 * Attempts streaming via Server-Sent Events.
 * Falls back to a regular POST request if the server doesn't support SSE.
 *
 * NOTE: The FastAPI backend currently uses a regular POST endpoint.
 * To enable true streaming add a `/chat/stream` SSE endpoint to api/main.py.
 * Until then this function calls the normal endpoint and delivers the full
 * response in one shot via onComplete.
 */
export async function sendMessageStream(
  message: string,
  threadId: string,
  onToken: StreamTokenCallback,
  onComplete: StreamCompleteCallback
): Promise<void> {
  try {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ message, thread_id: threadId }),
    });
    if (!res.ok) throw new Error(`Chat error: ${res.statusText}`);

    // ── Attempt chunked streaming ─────────────────────────────────────────
    if (res.body) {
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        onToken(chunk);
      }

      // Try to parse the accumulated JSON as the API response
      try {
        const parsed = JSON.parse(accumulated) as ChatAPIResponse;
        onComplete(parsed);
        return;
      } catch {
        // Response was streamed as text, construct a response object
        onComplete({ response: accumulated, thread_id: threadId, chart: null });
        return;
      }
    }

    // ── Fallback: read entire body ────────────────────────────────────────
    const data = (await res.json()) as ChatAPIResponse;
    onToken(data.response);
    onComplete(data);
  } catch (err) {
    throw err;
  }
}

// ─── Threads ─────────────────────────────────────────────────────────────────

export async function getThreads(): Promise<ThreadsAPIResponse> {
  const res = await fetch(`${BASE_URL}/threads`, {
    headers: headers(),
  });
  if (!res.ok) throw new Error(`Threads error: ${res.statusText}`);
  return res.json() as Promise<ThreadsAPIResponse>;
}

// ─── Files ───────────────────────────────────────────────────────────────────

export async function getFiles(): Promise<FilesAPIResponse> {
  const res = await fetch(`${BASE_URL}/files`, {
    headers: headers(),
  });
  if (!res.ok) throw new Error(`Files error: ${res.statusText}`);
  return res.json() as Promise<FilesAPIResponse>;
}

export async function uploadFile(file: File): Promise<UploadAPIResponse> {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${API_KEY}`,
    },
    body: form,
  });
  if (!res.ok) throw new Error(`Upload error: ${res.statusText}`);
  return res.json() as Promise<UploadAPIResponse>;
}

export async function getIndexingStatus(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${BASE_URL}/indexing_status`, {
    headers: headers(),
  });
  if (!res.ok) throw new Error(`Status error: ${res.statusText}`);
  return res.json() as Promise<{ status: string; message: string }>;
}

