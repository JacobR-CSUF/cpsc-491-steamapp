import type { Comparison, Player } from "@/lib/types";

interface OverviewPanelProps {
  comparison: Comparison;
  playerA: Player;
  playerB: Player;
}

export default function OverviewPanel(props: OverviewPanelProps) {
  return (
    <section aria-labelledby="overview-title">
      <h2 id="overview-title" className="mb-3 text-xl font-semibold tracking-tight">
        General overview
      </h2>
      <div className="rounded-2xl bg-panel p-6 text-sm text-muted ring-1 ring-white/10">
        Coming soon. {props.comparison.shared_games.length} shared games between{" "}
        {props.playerA.persona_name} and {props.playerB.persona_name}.
      </div>
    </section>
  );
}
