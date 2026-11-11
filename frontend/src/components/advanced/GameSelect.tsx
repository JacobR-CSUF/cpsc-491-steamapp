"use client";

import { useId } from "react";
import type { SharedGame } from "@/lib/types";

interface GameSelectProps {
  games: SharedGame[];
  value: number;
  onChange: (appId: number) => void;
}

export default function GameSelect({ games, value, onChange }: GameSelectProps) {
  const selectId = useId();
  const sorted = [...games].sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={selectId} className="text-sm text-muted">
        Game
      </label>
      <select
        id={selectId}
        value={value}
        title={games.find((game) => game.app_id === value)?.name}
        onChange={(event) => onChange(Number(event.target.value))}
        className="min-w-0 w-full max-w-sm truncate rounded-lg border border-white/10 bg-background px-3 py-2 text-sm text-foreground focus:border-accent focus:outline-none"
      >
        {sorted.map((game) => (
          <option key={game.app_id} value={game.app_id}>
            {game.name}
          </option>
        ))}
      </select>
    </div>
  );
}
