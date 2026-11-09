"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import PlayerAvatar from "@/components/PlayerAvatar";
import RecentOpponents from "@/components/RecentOpponents";
import SteamIdInput from "@/components/SteamIdInput";
import { isValidSteamId } from "@/lib/steamId";

export default function Home() {
  const router = useRouter();
  const [playerA, setPlayerA] = useState("");
  const [playerB, setPlayerB] = useState("");

  const a = playerA.trim();
  const b = playerB.trim();
  const canCompete = isValidSteamId(a) && isValidSteamId(b) && a !== b;

  function compete() {
    router.push(`/compare?a=${a}&b=${b}`);
  }

  return (
    <section className="mx-auto max-w-4xl py-12">
      <div className="grid gap-10 md:grid-cols-2 md:gap-16">
        <div className="flex flex-col items-center gap-6">
          <PlayerAvatar steamId={playerA} />
          <div className="w-full">
            <SteamIdInput label="Your SteamID64" value={playerA} onChange={setPlayerA} />
            <RecentOpponents steamId={playerA} onSelect={setPlayerB} />
          </div>
        </div>

        <div className="flex flex-col items-center gap-6">
          <PlayerAvatar steamId={playerB} />
          <SteamIdInput label="Opponent SteamID64" value={playerB} onChange={setPlayerB} />
        </div>
      </div>

      <div className="mt-14 flex flex-col items-center gap-5">
        <button
          type="button"
          onClick={compete}
          disabled={!canCompete}
          className="rounded-full bg-accent px-10 py-3 text-base font-semibold text-background transition-colors hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Compete
        </button>
        <p className="text-sm text-muted">
          Find your SteamID64 on{" "}
          <a
            href="https://steamid.io/"
            target="_blank"
            rel="noreferrer"
            className="text-accent underline-offset-4 hover:underline"
          >
            this handy website
          </a>
          .
        </p>
      </div>
    </section>
  );
}
