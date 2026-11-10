import { useId } from "react";
import { formatHours } from "@/lib/format";
import type { OwnedGame } from "@/lib/types";

/*
For the GameTile component, we want to display a tile for
  each game that shows the game's icon, name, and playtime information.
  The tile should be clickable, allowing users to select a game.
  When hovered or focused, a tooltip should appear with additional details about the game.
*/

interface GameTileProps {
  game: OwnedGame;
  onSelect: (appId: number) => void;
  selected?: boolean;
}

export default function GameTile({ game, onSelect, selected = false }: GameTileProps) {
  const tooltipId = useId();

  return (
    <div className="group relative">
      <button
        type="button"
        onClick={() => onSelect(game.app_id)}
        data-app-id={game.app_id}
        aria-describedby={tooltipId}
        aria-current={selected ? "true" : undefined}
        className="flex w-full items-center gap-3 rounded-xl bg-background/60 p-2.5 text-left ring-1 ring-white/10 transition-shadow hover:ring-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent aria-[current=true]:ring-2 aria-[current=true]:ring-accent"
      >
        {game.icon_url ? (
          // Steam icons are small remote images, so a plain <img> is enough.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={game.icon_url}
            alt=""
            width={32}
            height={32}
            loading="lazy"
            className="size-8 shrink-0 rounded"
          />
        ) : (
          <span
            aria-hidden="true"
            className="flex size-8 shrink-0 items-center justify-center rounded bg-panel text-xs text-muted"
          >
            {game.name.charAt(0).toUpperCase()}
          </span>
        )}
        <span className="min-w-0 truncate text-sm text-foreground">{game.name}</span>
      </button>

      <div
        id={tooltipId}
        role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 z-20 mb-2 w-max max-w-56 -translate-x-1/2 rounded-lg bg-background px-3 py-2 text-xs opacity-0 shadow-lg ring-1 ring-white/15 transition-opacity group-focus-within:opacity-100 group-hover:opacity-100"
      >
        <p className="font-medium text-foreground">{game.name}</p>
        <p className="mt-1 text-muted">
          Total playtime:{" "}
          <span className="font-semibold text-accent">
            {formatHours(game.playtime_minutes)}
          </span>
        </p>
        {game.recent_playtime_minutes > 0 && (
          <p className="text-muted">
            Last 2 weeks:{" "}
            <span className="text-foreground">
              {formatHours(game.recent_playtime_minutes)}
            </span>
          </p>
        )}
      </div>
    </div>
  );
}
