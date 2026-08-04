export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="error" role="alert">
      <span>{message}</span>
      {onRetry && <button onClick={onRetry}>Try again</button>}
    </div>
  );
}
