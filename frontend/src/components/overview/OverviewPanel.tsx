"use client";

import { useId, useState } from "react";
import AchievementComparisonCards from "@/components/overview/AchievementComparisonCards";
import ComparisonCharts from "@/components/overview/ComparisonCharts";
import StatRow from "@/components/overview/StatRow";
import { formatCents } from "@/lib/format";
import type { Comparison, Player } from "@/lib/types";

interface OverviewPanelProps {
  comparison: Comparison;
  playerA: Player;
  playerB: Player;
}

export default function OverviewPanel({ comparison, playerA, playerB }: OverviewPanelProps) {
  const [expanded, setExpanded] = useState(true);
  const panelId = useId();
  const titleId = useId();
  const statsA = comparison.player_a;
  const statsB = comparison.player_b;

  return (
    <section aria-labelledby={titleId} className="overflow-hidden rounded-2xl bg-panel ring-1 ring-white/10">
      <div className="flex items-center justify-between gap-4 px-4 py-5 sm:px-6">
        <h2 id={titleId} className="text-xl font-semibold tracking-tight">
          Overview
        </h2>
        <button
          type="button"
          aria-expanded={expanded}
          aria-controls={panelId}
          onClick={() => setExpanded((open) => !open)}
          className="rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-accent/60 hover:text-accent focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent"
        >
          {expanded ? "Minimize" : "Expand"}
        </button>
      </div>
      <div id={panelId} hidden={!expanded} className="border-t border-white/10 px-4 pb-6 sm:px-6">
        <table className="w-full table-fixed">
          <caption className="sr-only">Headline statistics for {playerA.persona_name} and {playerB.persona_name}</caption>
          <thead>
            <tr>
              <th scope="col" className="break-words py-5 pr-2 text-left text-sm font-semibold sm:pr-6">{playerA.persona_name}</th>
              <th scope="col"><span className="sr-only">Statistic</span></th>
              <th scope="col" className="break-words py-5 pl-2 text-right text-sm font-semibold sm:pl-6">{playerB.persona_name}</th>
            </tr>
          </thead>
          <tbody>
            <StatRow
              label="Account value"
              valueA={statsA.account_value_cents}
              valueB={statsB.account_value_cents}
              format={(value, player) => formatCents(value, player === "a" ? statsA.currency : statsB.currency)}
            />
            <StatRow label="Achievements unlocked" valueA={statsA.achievements_unlocked} valueB={statsB.achievements_unlocked} />
            <StatRow label="Games owned" valueA={statsA.games_owned} valueB={statsB.games_owned} />
            <StatRow label="Games played" valueA={statsA.games_played} valueB={statsB.games_played} />
            <StatRow label="100% completed games" valueA={statsA.completed_games.length} valueB={statsB.completed_games.length} />
          </tbody>
        </table>
        <div className="border-t border-white/10 pt-5 text-center">
          <p className="text-sm text-muted">Mutual achievements</p>
          <p className="mt-1 text-2xl font-semibold tabular-nums text-accent">
            {comparison.mutual_achievements.toLocaleString("en-US")}
          </p>
        </div>
        <AchievementComparisonCards comparison={comparison} playerA={playerA} playerB={playerB} />
        <ComparisonCharts comparison={comparison} playerA={playerA} playerB={playerB} />
      </div>
    </section>
  );
}
