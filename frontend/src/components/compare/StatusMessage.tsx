interface StatusMessageProps {
  title: string;
  message: string;
  onRetry?: () => void;
}

export default function StatusMessage({
  title,
  message,
  onRetry,
}: StatusMessageProps) {
  return (
    <div className="mx-auto max-w-md rounded-2xl bg-panel px-8 py-10 text-center ring-1 ring-white/10">
      <p className="text-lg font-semibold tracking-tight">{title}</p>
      <p className="mt-2 text-sm leading-relaxed text-muted">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-5 rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground"
        >
          Try again
        </button>
      )}
    </div>
  );
}