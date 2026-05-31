"use client";

import { FormEvent, useEffect, useState } from "react";
import { streamChat, type Citation } from "@/lib/api";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

type ChatPanelProps = {
  workspaceId?: string;
};

export function ChatPanel({ workspaceId }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMessages([]);
    setInput("");
    setError(null);
  }, [workspaceId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const question = input.trim();
    if (!question || !workspaceId || isSending) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };
    const assistantMessageId = crypto.randomUUID();

    setMessages((current) => [
      ...current,
      userMessage,
      {
        id: assistantMessageId,
        role: "assistant",
        content: "",
      },
    ]);
    setInput("");
    setIsSending(true);
    setError(null);

    try {
      await streamChat(workspaceId, question, (chunk) => {
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantMessageId
              ? { ...message, content: `${message.content}${chunk}` }
              : message,
          ),
        );
      });
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "Could not stream this answer.";
      setError(message);
      setMessages((current) =>
        current.map((chatMessage) =>
          chatMessage.id === assistantMessageId && !chatMessage.content
            ? {
                ...chatMessage,
                content: "I could not stream this answer. Please try again.",
              }
            : chatMessage,
        ),
      );
    } finally {
      setIsSending(false);
    }
  }

  return (
    <aside className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div>
        <h2 className="text-base font-semibold text-gray-950">Chat</h2>
        <p className="mt-2 text-sm leading-6 text-gray-600">
          Ask about the analyzed transcripts. The workspace id is used as the
          chat session.
        </p>
      </div>

      <div className="mt-4 max-h-[460px] space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 ? (
          <div className="rounded-md border border-dashed border-gray-300 bg-gray-50 p-3 text-sm text-gray-500">
            {workspaceId
              ? "Ask a question after analysis."
              : "Analyze two videos to start a chat session."}
          </div>
        ) : null}

        {messages.map((message) => (
          <article
            key={message.id}
            className={`rounded-md border p-3 text-sm ${
              message.role === "user"
                ? "border-gray-900 bg-gray-900 text-white"
                : "border-gray-200 bg-gray-50 text-gray-800"
            }`}
          >
            <p className="text-xs font-semibold uppercase tracking-wide opacity-70">
              {message.role === "user" ? "You" : "Assistant"}
            </p>
            <p className="mt-2 whitespace-pre-wrap leading-6">
              {message.content || "Thinking..."}
            </p>

            {message.citations && message.citations.length > 0 ? (
              <div className="mt-3 space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Citations
                </p>
                {message.citations.map((citation) => (
                  <div
                    key={`${citation.video_id}-${citation.chunk_index}-${citation.source_url}`}
                    className="rounded border border-gray-200 bg-white p-2 text-xs text-gray-600"
                  >
                    <p className="font-medium text-gray-900">
                      {citation.platform || "source"} ·{" "}
                      {citation.video_id || "unknown video"} · chunk{" "}
                      {citation.chunk_index ?? "?"}
                    </p>
                    <p>{citation.creator || "Unknown creator"}</p>
                    {citation.source_url ? (
                      <a
                        href={citation.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-1 block break-all text-gray-900 underline"
                      >
                        {citation.source_url}
                      </a>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>

      {error ? (
        <div className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={!workspaceId || isSending}
          placeholder={
            workspaceId ? "Ask about the videos" : "Analyze videos first"
          }
          className="min-w-0 flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-gray-900 disabled:bg-gray-50 disabled:text-gray-500"
        />
        <button
          type="submit"
          disabled={!workspaceId || isSending || !input.trim()}
          className="rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {isSending ? "Thinking" : "Send"}
        </button>
      </form>
    </aside>
  );
}
