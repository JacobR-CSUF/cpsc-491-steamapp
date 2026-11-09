import type { Player } from "@/lib/types";

interface PlayerHeaderProps {
  player: Player;
}

export default function PlayerHeader({ player }: PlayerHeaderProps) {
  return (
    <div className="flex flex-col items-center gap-3 text-center">
      <div className="h-24 w-24 overflow-hidden rounded-full bg-panel ring-1 ring-white/10">
        {player.avatar_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={player.avatar_url}
            alt={player.persona_name}
            width={96}
            height={96}
            className="h-full w-full object-cover"
          />
        )}
      </div>
      <div>
        <p className="text-lg font-semibold tracking-tight">{player.persona_name}</p>
        {player.profile_url && (
          <a
            href={player.profile_url}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-accent underline-offset-4 hover:underline"
          >
            Steam profile
          </a>
        )}
      </div>
    </div>
  );
}
