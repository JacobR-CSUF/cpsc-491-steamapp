import Link from "next/link";

export default function NotFound() {
  return (
    <section className="mx-auto max-w-md space-y-4 py-12 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">
        Page not found
      </h1>
      <p className="text-muted">
        This page doesn’t exist.
      </p>
      <Link
        href="/"
        className="inline-block text-accent underline-offset-4 hover:underline"
      >
        Back to Compare
      </Link>
    </section>
  );
}