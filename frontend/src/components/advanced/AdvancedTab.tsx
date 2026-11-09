"use client";

import { useEffect, useId, useState } from "react";
import { getPlayer } from "@/lib/api";
import type { SharedGame } from "@/lib/types";

interface AdvancedTabProps {
  steamIdA: string;
  steamIdB: string;
  sharedGames: SharedGame[];
}

// The shared game with the most combined unlocks (unlocked_a + unlocked_b).
// On a tie, the game listed first wins.
function mostPlayedGame(games: SharedGame[]): SharedGame | undefined {
  let best: SharedGame | undefined;
  for (const game of games) {
    if (!best || game.unlocked_a + game.unlocked_b > best.unlocked_a + best.unlocked_b) {
      best = game;
    }
  }
  return best;
}

export default function AdvancedTab({ steamIdA, steamIdB, sharedGames }: AdvancedTabProps) {
  const panelId = useId();
  const [expanded, setExpanded] = useState(false);

  // Selected game. KAN-64's dropdown will change it.
  const [selectedAppId] = useState<number | undefined>(
    () => mostPlayedGame(sharedGames)?.app_id,
  );
  // If the games change (a new comparison), fall back to the new default.
  const selected =
    sharedGames.find((game) => game.app_id === selectedAppId) ?? mostPlayedGame(sharedGames);

  // Player names for the section labels, loaded the first time the tab opens.
  const key = `${steamIdA}:${steamIdB}`;
  const [names, setNames] = useState<{ key: string; a: string; b: string } | null>(null);

  useEffect(() => {
    if (!expanded) return;

    let active = true;
    Promise.all([getPlayer(steamIdA), getPlayer(steamIdB)])
      .then(([playerA, playerB]) => {
        if (active) setNames({ key, a: playerA.persona_name, b: playerB.persona_name });
      })
      .catch(() => {
        // Fall back to the generic labels below.
      });

    return () => {
      active = false;
    };
  }, [expanded, key, steamIdA, steamIdB]);

  const nameA = names?.key === key ? names.a : "Player A";
  const nameB = names?.key === key ? names.b : "Player B";

  return (
    <section aria-labelledby="advanced-title">
      <h2 id="advanced-title" className="mb-3 text-xl font-semibold tracking-tight">
        <button
          type="button"
          aria-expanded={expanded}
          aria-controls={panelId}
          onClick={() => setExpanded((open) => !open)}
          className="flex items-center gap-2 transition-colors hover:text-accent"
        >
          Advanced
          <span aria-hidden="true" className="text-sm text-muted">
            {expanded ? "▲" : "▼"}
          </span>
        </button>
      </h2>

      {expanded && (
        <div id={panelId} className="rounded-2xl bg-panel p-6 ring-1 ring-white/10">
          {selected ? (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold tracking-tight text-accent">
                  {selected.name}
                </h3>
                <p className="text-sm text-muted">
                  {nameA} vs {nameB}
                </p>
              </div>
              {/* KAN-64 to KAN-67 sections go here. */}
            </div>
          ) : (
            <p className="text-sm text-muted">No shared games to analyze</p>
          )}
        </div>
      )}
    </section>
  );
}
