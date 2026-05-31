const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

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
