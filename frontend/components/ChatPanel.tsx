export function ChatPanel() {
  return (
    <aside className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h2 className="text-base font-semibold text-gray-950">Chat</h2>
      <p className="mt-2 text-sm leading-6 text-gray-600">
        Chat wiring comes next. Analysis data is ready.
      </p>
      <input
        disabled
        placeholder="Ask about the videos"
        className="mt-4 w-full rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500"
      />
    </aside>
  );
}
