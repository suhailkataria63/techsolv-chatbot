type Comparison = {
  winner: string;
  score_a: number;
  score_b: number;
  comparison_summary: string;
  strengths_video_a: string[];
  strengths_video_b: string[];
  improvement_suggestions: string[];
};

type ComparisonPanelProps = {
  comparison?: Comparison | null;
};

export function ComparisonPanel({ comparison }: ComparisonPanelProps) {
  if (!comparison) {
    return (
      <section className="rounded-lg border border-dashed border-gray-300 bg-white p-4 text-sm text-gray-500">
        Comparison results will appear after both videos are analyzed.
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 border-b border-gray-200 pb-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Comparison
          </p>
          <h2 className="mt-1 text-lg font-semibold text-gray-950">
            Winner: {comparison.winner.replace("_", " ")}
          </h2>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <Score label="Video A" value={comparison.score_a} />
          <Score label="Video B" value={comparison.score_b} />
        </div>
      </div>

      <p className="mt-4 text-sm leading-6 text-gray-700">
        {comparison.comparison_summary}
      </p>

      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <List title="Video A strengths" items={comparison.strengths_video_a} />
        <List title="Video B strengths" items={comparison.strengths_video_b} />
        <List
          title="Improvements"
          items={comparison.improvement_suggestions}
        />
      </div>
    </section>
  );
}

function Score({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-semibold text-gray-950">{value.toFixed(1)}</p>
    </div>
  );
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
      <ul className="mt-2 space-y-2 text-sm text-gray-700">
        {items.map((item) => (
          <li key={item} className="rounded-md border border-gray-200 bg-gray-50 p-2">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
