export type Video = {
  platform?: string;
  title?: string | null;
  creator?: string | null;
  views?: number | null;
  likes?: number | null;
  comments?: number | null;
  duration_seconds?: number | null;
  upload_date?: string | null;
  engagement_rate?: number | null;
  transcript_source?: string | null;
  rag_ingestion?: {
    status?: string;
    stored_chunks?: number;
    error?: string | null;
  } | null;
};

type VideoCardProps = {
  label: string;
  video?: Video;
};

function formatNumber(value?: number | null) {
  if (value === null || value === undefined) {
    return "Missing";
  }

  return new Intl.NumberFormat("en").format(value);
}

function formatDuration(value?: number | null) {
  if (!value) {
    return "Missing";
  }

  const minutes = Math.floor(value / 60);
  const seconds = value % 60;
  return minutes ? `${minutes}m ${seconds}s` : `${seconds}s`;
}

function statusClass(status?: string) {
  if (status === "success") {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  if (status === "failed") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }

  return "border-gray-200 bg-gray-50 text-gray-600";
}

export function VideoCard({ label, video }: VideoCardProps) {
  if (!video) {
    return (
      <section className="rounded-lg border border-dashed border-gray-300 bg-white p-4 text-sm text-gray-500">
        {label} will appear here after analysis.
      </section>
    );
  }

  const ingestionStatus = video.rag_ingestion?.status || "not started";

  return (
    <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            {label} · {video.platform || "unknown"}
          </p>
          <h2 className="mt-1 line-clamp-2 text-base font-semibold text-gray-950">
            {video.title || "Untitled video"}
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            {video.creator || "Unknown creator"}
          </p>
        </div>
      </div>

      <dl className="grid grid-cols-2 gap-3 text-sm">
        <Metric label="Views" value={formatNumber(video.views)} />
        <Metric label="Likes" value={formatNumber(video.likes)} />
        <Metric label="Comments" value={formatNumber(video.comments)} />
        <Metric label="Duration" value={formatDuration(video.duration_seconds)} />
        <Metric label="Uploaded" value={video.upload_date || "Missing"} />
        <Metric
          label="Engagement"
          value={
            video.engagement_rate === null || video.engagement_rate === undefined
              ? "Missing"
              : `${video.engagement_rate}%`
          }
        />
      </dl>

      <div className="mt-4 grid gap-2 text-sm">
        <div className="flex items-center justify-between rounded-md border border-gray-200 px-3 py-2">
          <span className="text-gray-600">Transcript</span>
          <span className="font-medium text-gray-900">
            {video.transcript_source || "unavailable"}
          </span>
        </div>
        <div
          className={`rounded-md border px-3 py-2 text-sm ${statusClass(
            ingestionStatus,
          )}`}
        >
          RAG ingestion: {ingestionStatus}
          {video.rag_ingestion?.stored_chunks !== undefined
            ? ` · ${video.rag_ingestion.stored_chunks} chunks`
            : ""}
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
      <dt className="text-xs text-gray-500">{label}</dt>
      <dd className="mt-1 font-medium text-gray-950">{value}</dd>
    </div>
  );
}
