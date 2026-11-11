interface SkeletonProps {
  className?: string;
}

export default function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div aria-hidden="true" className={"animate-pulse rounded-xl bg-panel ring-1 ring-inset ring-white/10 motion-reduce:animate-none " + className} />
  );
}

interface LoadingSkeletonProps {
  label: string;
  variant?: "overview" | "library" | "chart" | "list";
}

export function LoadingSkeleton({ label, variant = "list" }: LoadingSkeletonProps) {
  return (
    <div role="status" aria-label={label} className="min-w-0 space-y-4">
      <p className="text-sm text-muted">{label}</p>
      {variant === "overview" ? (
        <>
          <div className="grid grid-cols-2 gap-6">
            {[0, 1].map((index) => (
              <div key={index} className="flex flex-col items-center gap-3">
                <Skeleton className="h-24 w-24 rounded-full" />
                <Skeleton className="h-5 w-28" />
              </div>
            ))}
          </div>
          <Skeleton className="h-96 w-full" />
        </>
      ) : variant === "library" ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 12 }, (_, index) => <Skeleton key={index} className="h-14 w-full" />)}
        </div>
      ) : variant === "chart" ? (
        <Skeleton className="h-72 w-full" />
      ) : (
        <div className="space-y-3">
          {Array.from({ length: 5 }, (_, index) => <Skeleton key={index} className="h-12 w-full" />)}
        </div>
      )}
    </div>
  );
}
