export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="loading" role="status">
      <span className="spinner" />
      <span>{label}…</span>
      <span className="skeleton" aria-hidden="true" />
    </div>
  );
}
