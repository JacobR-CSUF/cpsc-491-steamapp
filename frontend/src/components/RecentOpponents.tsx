"use client";

import SafeImage from "@/components/SafeImage";
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
          <li key={player.steam_id} className="min-w-0 max-w-full">
            <button
              type="button"
              onClick={() => onSelect(player.steam_id)}
              title={player.persona_name}
              className="action-button flex max-w-full items-center gap-2 rounded-full border border-white/10 bg-panel py-1.5 pr-3.5 pl-1.5 text-sm text-foreground transition-colors hover:border-accent/60"
            >
              {player.avatar_url ? (
                <SafeImage
                  src={player.avatar_url}
                  alt=""
                  width={24}
                  height={24}
                  className="h-6 w-6 rounded-full"
                />
              ) : (
                <span className="h-6 w-6 rounded-full bg-white/10" />
              )}
              <span className="truncate">{player.persona_name}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
