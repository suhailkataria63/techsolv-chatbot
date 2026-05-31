"use client";

import { useState } from "react";
import { ChatPanel } from "@/components/ChatPanel";
import { ComparisonPanel } from "@/components/ComparisonPanel";
import { UrlForm } from "@/components/UrlForm";
import { VideoCard, type Video } from "@/components/VideoCard";
import { compareWorkspace, createWorkspace } from "@/lib/api";

type Workspace = {
  workspace_id: string;
  video_a: Video;
  video_b: Video;
};

type Comparison = {
  winner: string;
  score_a: number;
  score_b: number;
  comparison_summary: string;
  strengths_video_a: string[];
  strengths_video_b: string[];
  improvement_suggestions: string[];
};

export default function Home() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(videoAUrl: string, videoBUrl: string) {
    setIsLoading(true);
    setError(null);
    setComparison(null);

    try {
      const created = (await createWorkspace(videoAUrl, videoBUrl)) as Workspace;
      setWorkspace(created);

      const report = (await compareWorkspace(
        created.workspace_id,
      )) as Comparison;
      setComparison(report);
    } catch (caughtError) {
      setWorkspace(null);
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "Could not analyze these videos.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-950">
            Social Video RAG
          </h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-gray-600">
            Analyze two social videos, compare their performance signals, and
            prepare transcript context for retrieval chat.
          </p>
        </header>

        <UrlForm
          isLoading={isLoading}
          error={error}
          onSubmit={handleAnalyze}
        />

        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <VideoCard label="Video A" video={workspace?.video_a} />
              <VideoCard label="Video B" video={workspace?.video_b} />
            </div>

            <ComparisonPanel comparison={comparison} />
          </div>

          <ChatPanel />
        </div>
      </div>
    </main>
  );
}
