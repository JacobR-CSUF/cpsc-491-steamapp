"use client";

import Link from "next/link";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ reset }: ErrorPageProps) {
  return (
    <section className="mx-auto max-w-md space-y-4 py-12 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">
        Something went wrong
      </h1>
      <p className="text-muted">
        Try loading this page again or return to Compare.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-4">
        <button
          type="button"
          onClick={() => reset()}
          className="action-button rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground"
        >
          Try again
        </button>
        <Link
          href="/"
          className="text-sm text-accent underline-offset-4 hover:underline"
        >
          Back to Compare
        </Link>
      </div>
    </section>
  );
}