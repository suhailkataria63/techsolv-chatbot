const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export type Citation = {
  video_id: string | null;
  platform: string | null;
  creator: string | null;
  chunk_index: number | null;
  source_url: string | null;
};

export type ChatResponse = {
  session_id: string;
  answer: string;
  citations: Citation[];
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed with ${response.status}`;

    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the status-based message if the API does not return JSON.
    }

    throw new Error(message);
  }

  return response.json();
}

export function createWorkspace(videoAUrl: string, videoBUrl: string) {
  return request("/api/workspace/create", {
    method: "POST",
    body: JSON.stringify({
      video_a_url: videoAUrl,
      video_b_url: videoBUrl,
    }),
  });
}

export function getWorkspace(workspaceId: string) {
  return request(`/api/workspace/${workspaceId}`);
}

export function compareWorkspace(workspaceId: string) {
  return request(`/api/workspace/${workspaceId}/compare`);
}

export function queryChat(sessionId: string, message: string) {
  return request<ChatResponse>("/api/chat/query", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      message,
    }),
  });
}

export async function streamChat(
  sessionId: string,
  message: string,
  onChunk: (chunk: string) => void,
) {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error(`Stream request failed with ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Stream response was empty.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    onChunk(decoder.decode(value, { stream: true }));
  }

  const finalChunk = decoder.decode();
  if (finalChunk) {
    onChunk(finalChunk);
  }
}
