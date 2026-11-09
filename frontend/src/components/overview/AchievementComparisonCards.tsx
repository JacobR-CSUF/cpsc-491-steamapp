import CompletedGamesList from "@/components/overview/CompletedGamesList";
import { formatPercent } from "@/lib/format";
import type { Comparison, Player } from "@/lib/types";

interface AchievementComparisonCardsProps {
  comparison: Comparison;
  playerA: Player;
  playerB: Player;
}

function lead(difference: number, nameA: string, nameB: string, percentage = false) {
  if (difference === 0) return "Tied";
  const amount = Math.abs(difference).toLocaleString("en-US", { maximumFractionDigits: percentage ? 2 : 0 });
  return `${difference > 0 ? nameA : nameB} leads by ${amount}${percentage ? " percentage points" : ""}`;
}

export default function AchievementComparisonCards({ comparison, playerA, playerB }: AchievementComparisonCardsProps) {
  const a = comparison.player_a;
  const b = comparison.player_b;
  const cards = [
    {
      title: "Achievements",
      values: [a, b].map((stats) => `${stats.achievements_unlocked.toLocaleString("en-US")} / ${stats.achievements_available.toLocaleString("en-US")}`),
      difference: comparison.achievements_difference,
    },
    {
      title: "Completion rate",
      values: [formatPercent(a.completion_rate), formatPercent(b.completion_rate)],
      difference: comparison.completion_rate_difference,
    },
    {
      title: "100% completed",
      values: [a.completed_games.length.toLocaleString("en-US"), b.completed_games.length.toLocaleString("en-US")],
      difference: a.completed_games.length - b.completed_games.length,
    },
  ];

  return (
    <div className="mt-8 grid gap-4 xl:grid-cols-3">
      {cards.map((card) => (
        <section key={card.title} aria-label={card.title} className="min-w-0 rounded-xl border border-white/10 bg-background/40 p-4">
          <h3 className="font-semibold">{card.title}</h3>
          <div className="mt-4 grid grid-cols-2 gap-4">
            {[playerA, playerB].map((player, index) => (
              <div key={player.steam_id} className="min-w-0 space-y-2">
                <p className="break-words text-sm text-muted">{player.persona_name}</p>
                <p className={`text-lg font-semibold tabular-nums ${index === 0 ? card.difference > 0 ? "text-accent" : "" : card.difference < 0 ? "text-accent" : ""}`}>{card.values[index]}</p>
                {card.title === "100% completed" && <CompletedGamesList games={index === 0 ? a.completed_games : b.completed_games} />}
              </div>
            ))}
          </div>
          <p className="mt-4 border-t border-white/10 pt-3 text-sm text-accent">
            {lead(card.difference, playerA.persona_name, playerB.persona_name, card.title === "Completion rate")}
          </p>
        </section>
      ))}
    </div>
  );
}
