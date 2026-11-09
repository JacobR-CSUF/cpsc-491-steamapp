interface StatusMessageProps {
  title: string;
  message: string;
}

export default function StatusMessage({ title, message }: StatusMessageProps) {
  return (
    <div className="mx-auto max-w-md rounded-2xl bg-panel px-8 py-10 text-center ring-1 ring-white/10">
      <p className="text-lg font-semibold tracking-tight">{title}</p>
      <p className="mt-2 text-sm leading-relaxed text-muted">{message}</p>
    </div>
  );
}
