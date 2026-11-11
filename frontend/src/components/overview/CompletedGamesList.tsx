"use client";

import { formatNumber } from "@/lib/format";
import { useId, useState } from "react";
import type { CompletedGame } from "@/lib/types";

export default function CompletedGamesList({ games }: { games: CompletedGame[] }) {
  const [showAll, setShowAll] = useState(false);
  const listId = useId();

  if (games.length === 0) return <p className="text-sm text-muted">None yet</p>;

  return (
    <div className="space-y-3">
      <ul id={listId} className="space-y-2 text-sm text-muted">
        {(showAll ? games : games.slice(0, 5)).map((game) => (
          <li key={game.app_id} title={game.name} className="truncate">{game.name}</li>
        ))}
      </ul>
      {games.length > 5 && (
        <button
          type="button"
          aria-expanded={showAll}
          aria-controls={listId}
          onClick={() => setShowAll((all) => !all)}
          className="text-sm text-accent underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent"
        >
          {showAll ? "Show less" : `Show all (${formatNumber(games.length)})`}
        </button>
      )}
    </div>
  );
}
