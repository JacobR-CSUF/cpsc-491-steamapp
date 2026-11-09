"use client";

import { useEffect, useState } from "react";
import { getOpponents } from "@/lib/api";
import { isValidSteamId } from "@/lib/steamId";
import type { Opponent } from "@/lib/types";

interface RecentOpponentsProps {
  steamId: string;
  onSelect: (steamId: string) => void;
}

export default function RecentOpponents({ steamId, onSelect }: RecentOpponentsProps) {
  const [loaded, setLoaded] = useState<{ id: string; opponents: Opponent[] }>({
    id: "",
    opponents: [],
  });
  const trimmed = steamId.trim();

  useEffect(() => {
    if (!isValidSteamId(trimmed)) return;

    let active = true;
    getOpponents(trimmed)
      .then((opponents) => {
        if (active) setLoaded({ id: trimmed, opponents });
      })
      .catch(() => {
        if (active) setLoaded({ id: trimmed, opponents: [] });
      });

    return () => {
      active = false;
    };
  }, [trimmed]);

  const opponents = loaded.id === trimmed ? loaded.opponents : [];

  if (opponents.length === 0) {
    return null;
  }

  return (
    <div className="mt-4">
      <p className="mb-2 text-sm text-muted">Recent opponents</p>
      <ul className="flex flex-wrap gap-2">
        {opponents.map(({ player }) => (
          <li key={player.steam_id}>
            <button
              type="button"
              onClick={() => onSelect(player.steam_id)}
              className="flex items-center gap-2 rounded-full border border-white/10 bg-panel py-1.5 pr-3.5 pl-1.5 text-sm text-foreground transition-colors hover:border-accent/60"
            >
              {player.avatar_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={player.avatar_url}
                  alt=""
                  width={24}
                  height={24}
                  className="h-6 w-6 rounded-full"
                />
              ) : (
                <span className="h-6 w-6 rounded-full bg-white/10" />
              )}
              {player.persona_name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
