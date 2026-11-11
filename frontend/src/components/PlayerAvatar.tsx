"use client";

import SafeImage from "@/components/SafeImage";
import { useEffect, useState } from "react";
import { getPlayer } from "@/lib/api";
import { isValidSteamId } from "@/lib/steamId";
import type { Player } from "@/lib/types";

interface PlayerAvatarProps {
  steamId: string;
}

export default function PlayerAvatar({ steamId }: PlayerAvatarProps) {
  const [loaded, setLoaded] = useState<{ id: string; player: Player | null }>({
    id: "",
    player: null,
  });
  const trimmed = steamId.trim();

  useEffect(() => {
    if (!isValidSteamId(trimmed)) return;

    let active = true;
    getPlayer(trimmed)
      .then((player) => {
        if (active) setLoaded({ id: trimmed, player });
      })
      .catch(() => {
        if (active) setLoaded({ id: trimmed, player: null });
      });

    return () => {
      active = false;
    };
  }, [trimmed]);

  const player = loaded.id === trimmed ? loaded.player : null;

  return (
    <div className="flex min-w-0 w-full flex-col items-center gap-3">
      <div className="flex h-24 w-24 items-center justify-center overflow-hidden rounded-full bg-panel ring-1 ring-white/10">
        {player?.avatar_url ? (
          <SafeImage
            src={player.avatar_url}
            alt={player.persona_name}
            width={96}
            height={96}
            className="h-full w-full object-cover"
          />
        ) : (
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            aria-hidden="true"
            className="h-10 w-10 text-muted/60"
          >
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-3.3 3.6-6 8-6s8 2.7 8 6" />
          </svg>
        )}
      </div>
      <p title={player?.persona_name} className="h-5 max-w-full truncate text-sm text-muted">{player?.persona_name ?? "\u00a0"}</p>
    </div>
  );
}
