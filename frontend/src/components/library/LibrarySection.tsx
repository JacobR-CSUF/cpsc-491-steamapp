interface LibrarySectionProps {
  steamIdA: string;
  steamIdB: string;
}

export default function LibrarySection(props: LibrarySectionProps) {
  return (
    <section aria-labelledby="library-title">
      <h2 id="library-title" className="mb-3 text-xl font-semibold tracking-tight">
        Libraries
      </h2>
      <div className="rounded-2xl bg-panel p-6 text-sm text-muted ring-1 ring-white/10">
        Coming soon. Libraries for {props.steamIdA} and {props.steamIdB}.
      </div>
    </section>
  );
}
