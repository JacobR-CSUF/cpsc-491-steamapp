"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import PlayerAvatar from "@/components/PlayerAvatar";
import RecentOpponents from "@/components/RecentOpponents";
import SteamIdInput from "@/components/SteamIdInput";
import { getProfileStatus } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import { isValidSteamId } from "@/lib/steamId";

export default function Home() {
  const router = useRouter();
  const [playerA, setPlayerA] = useState("");
  const [playerB, setPlayerB] = useState("");
  const [errorA, setErrorA] = useState("");
  const [errorB, setErrorB] = useState("");
  const [requestError, setRequestError] = useState("");
  const [checking, setChecking] = useState(false);
  const requestVersion = useRef(0);

  const a = playerA.trim();
  const b = playerB.trim();
  const canCompete =
    isValidSteamId(a) && isValidSteamId(b) && a !== b;

  function changePlayerA(value: string) {
    requestVersion.current += 1;
    setPlayerA(value);
    setErrorA("");
    setRequestError("");
    setChecking(false);
  }

  function changePlayerB(value: string) {
    requestVersion.current += 1;
    setPlayerB(value);
    setErrorB("");
    setRequestError("");
    setChecking(false);
  }

  async function compete() {
    if (!canCompete || checking) return;

    const version = ++requestVersion.current;
    setChecking(true);
    setErrorA("");
    setErrorB("");
    setRequestError("");

    try {
      const [statusA, statusB] = await Promise.all([
        getProfileStatus(a),
        getProfileStatus(b),
      ]);

      if (version !== requestVersion.current) return;

      setErrorA(statusA.status === "public" ? "" : statusA.message);
      setErrorB(statusB.status === "public" ? "" : statusB.message);

      if (statusA.status === "public" && statusB.status === "public") {
        router.push(`/compare?a=${a}&b=${b}`);
      }
    } catch (error) {
      if (version === requestVersion.current) {
        setRequestError(errorMessage(error));
      }
    } finally {
      if (version === requestVersion.current) {
        setChecking(false);
      }
    }
  }

  return (
    <section className="mx-auto max-w-4xl py-12">
      <div className="grid gap-10 md:grid-cols-2 md:gap-16">
        <div className="flex flex-col items-center gap-6">
          <PlayerAvatar steamId={playerA} />
          <div className="w-full">
            <SteamIdInput
              label="Your SteamID64"
              value={playerA}
              onChange={changePlayerA}
              error={errorA}
            />
            <RecentOpponents
              steamId={playerA}
              onSelect={changePlayerB}
            />
          </div>
        </div>

        <div className="flex flex-col items-center gap-6">
          <PlayerAvatar steamId={playerB} />
          <SteamIdInput
            label="Opponent SteamID64"
            value={playerB}
            onChange={changePlayerB}
            error={errorB}
          />
        </div>
      </div>

      <div className="mt-14 flex flex-col items-center gap-5">
        {requestError && (
          <p role="alert" className="text-center text-sm text-red-400">
            {requestError}
          </p>
        )}
        {a !== "" && a === b && (
          <p role="alert" className="text-center text-sm text-red-400">
            Choose two different Steam profiles.
          </p>
        )}
        <button
          type="button"
          onClick={compete}
          disabled={!canCompete || checking}
          aria-busy={checking}
          className="rounded-full bg-accent px-10 py-3 text-base font-semibold text-background transition-colors hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {checking ? "Checking profiles…" : "Compete"}
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