import type { SharedGame } from "@/lib/types";

interface AdvancedTabProps {
  steamIdA: string;
  steamIdB: string;
  sharedGames: SharedGame[];
}

export default function AdvancedTab(props: AdvancedTabProps) {
  return (
    <section aria-labelledby="advanced-title">
      <h2 id="advanced-title" className="mb-3 text-xl font-semibold tracking-tight">
        Advanced
      </h2>
      <div className="rounded-2xl bg-panel p-6 text-sm text-muted ring-1 ring-white/10">
        Coming soon. {props.sharedGames.length} games to choose from for {props.steamIdA} and{" "}
        {props.steamIdB}.
      </div>
    </section>
  );
}
