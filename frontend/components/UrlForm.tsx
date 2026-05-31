"use client";

import { FormEvent, useState } from "react";

type UrlFormProps = {
  isLoading: boolean;
  error: string | null;
  onSubmit: (videoAUrl: string, videoBUrl: string) => Promise<void>;
};

export function UrlForm({ isLoading, error, onSubmit }: UrlFormProps) {
  const [videoAUrl, setVideoAUrl] = useState("");
  const [videoBUrl, setVideoBUrl] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(videoAUrl.trim(), videoBUrl.trim());
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
    >
      <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto] md:items-end">
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-gray-700">
            Video A URL
          </span>
          <input
            value={videoAUrl}
            onChange={(event) => setVideoAUrl(event.target.value)}
            placeholder="YouTube or Instagram Reel URL"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-gray-900"
            required
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium text-gray-700">
            Video B URL
          </span>
          <input
            value={videoBUrl}
            onChange={(event) => setVideoBUrl(event.target.value)}
            placeholder="YouTube or Instagram Reel URL"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-gray-900"
            required
          />
        </label>

        <button
          type="submit"
          disabled={isLoading}
          className="h-10 rounded-md bg-gray-900 px-4 text-sm font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {isLoading ? "Analyzing..." : "Analyze videos"}
        </button>
      </div>

      {error ? (
        <p className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      ) : null}
    </form>
  );
}
