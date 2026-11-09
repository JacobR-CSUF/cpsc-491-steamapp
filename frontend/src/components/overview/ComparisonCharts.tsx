import AchievementsChart from "@/components/charts/AchievementsChart";
import SharedGamesChart from "@/components/charts/SharedGamesChart";
import type { Comparison, Player } from "@/lib/types";

export default function ComparisonCharts({ comparison, playerA, playerB }: { comparison: Comparison; playerA: Player; playerB: Player }) {
  return (
    <div className="mt-8 grid min-w-0 gap-6 lg:grid-cols-2">
      <figure className="min-w-0 rounded-xl border border-white/10 bg-background/40 p-3 sm:p-4">
        <figcaption className="mb-4 font-semibold">Achievement totals</figcaption>
        <AchievementsChart statsA={comparison.player_a} statsB={comparison.player_b} nameA={playerA.persona_name} nameB={playerB.persona_name} />
      </figure>
      <figure className="min-w-0 rounded-xl border border-white/10 bg-background/40 p-3 sm:p-4">
        <figcaption className="font-semibold">Biggest shared game gaps</figcaption>
        <p className="mb-4 mt-1 text-sm text-muted">Up to 10 games, ranked by achievement difference.</p>
        <SharedGamesChart sharedGames={comparison.shared_games} nameA={playerA.persona_name} nameB={playerB.persona_name} />
      </figure>
    </div>
  );
}
