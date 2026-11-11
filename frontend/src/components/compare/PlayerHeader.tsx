import SafeImage from "@/components/SafeImage";
import type { Player } from "@/lib/types";

interface PlayerHeaderProps {
  player: Player;
}

export default function PlayerHeader({ player }: PlayerHeaderProps) {
  return (
    <div className="flex min-w-0 flex-col items-center gap-3 text-center">
      <div className="h-24 w-24 overflow-hidden rounded-full bg-panel ring-1 ring-white/10">
        {player.avatar_url && (
          <SafeImage
            src={player.avatar_url}
            alt={player.persona_name}
            width={96}
            height={96}
            className="h-full w-full object-cover"
          />
        )}
      </div>
      <div className="min-w-0 w-full">
        <p title={player.persona_name} className="truncate text-lg font-semibold tracking-tight">{player.persona_name}</p>
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
