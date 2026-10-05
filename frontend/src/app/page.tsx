import BackendStatus from "@/components/BackendStatus";

export default function Home() {
  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-12">
      <h1 className="mb-4 text-4xl font-bold">
        Steam-User Showdown
      </h1>

      <p className="mb-8 text-lg">
        Welcome to Steam-User Showdown.
      </p>

      <BackendStatus />
    </main>
  );
}