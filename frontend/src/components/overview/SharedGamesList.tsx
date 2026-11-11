"use client";

import { formatNumber } from "@/lib/format";
import { useId, useState } from "react";
import type { AchievementSelection } from "@/components/overview/AchievementIcon";
import GameAchievementGrid from "@/components/overview/GameAchievementGrid";
import type { Comparison } from "@/lib/types";

interface SharedGamesListProps {
  comparison: Comparison;
  steamIdA: string;
  steamIdB: string;
  onSelect?: (selection: AchievementSelection) => void;
}

export default function SharedGamesList({ comparison, steamIdA, steamIdB, onSelect }: SharedGamesListProps) {
  const [expandedAppId, setExpandedAppId] = useState<number | null>(null);
  const id = useId();

  return (
    <section aria-label="Shared games" className="mt-8 border-t border-white/10 pt-6">
      <h3 className="text-lg font-semibold">Shared games</h3>
      <p className="mb-4 mt-1 text-sm text-muted">Expand a game to compare achievements. A blue ring marks achievements unlocked by both players.</p>
      {comparison.shared_games.length === 0 ? <p className="text-sm text-muted">No shared games.</p> : (
        <ul className="divide-y divide-white/10">
          {comparison.shared_games.map((game) => {
            const expanded = expandedAppId === game.app_id;
            const panelId = `${id}-${game.app_id}`;
            return (
              <li key={game.app_id}>
                <button
                  type="button"
                  aria-expanded={expanded}
                  aria-controls={panelId}
                  onClick={() => setExpandedAppId(expanded ? null : game.app_id)}
                  className="flex w-full flex-wrap items-center justify-between gap-3 rounded-lg px-2 py-4 text-left transition-colors hover:bg-white/5 focus-visible:outline-2 focus-visible:outline-accent"
                >
                  <span title={game.name} className="min-w-0 flex-1 truncate font-medium">{game.name}</span>
                  <span className="flex gap-4 text-sm tabular-nums text-muted">
                    <span><span className="sr-only">Player A: </span>{formatNumber(game.unlocked_a)} / {formatNumber(game.total)}</span>
                    <span><span className="sr-only">Player B: </span>{formatNumber(game.unlocked_b)} / {formatNumber(game.total)}</span>
                    <span aria-hidden="true" className="text-accent">{expanded ? "−" : "+"}</span>
                  </span>
                </button>
                <div id={panelId} hidden={!expanded}>
                  {expanded && <GameAchievementGrid key={`${steamIdA}:${steamIdB}:${game.app_id}`} appId={game.app_id} steamIdA={steamIdA} steamIdB={steamIdB} onSelect={onSelect} />}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
