"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import AdvancedTab from "@/components/advanced/AdvancedTab";
import PlayerHeader from "@/components/compare/PlayerHeader";
import StatusMessage from "@/components/compare/StatusMessage";
import LibrarySection from "@/components/library/LibrarySection";
import OverviewPanel from "@/components/overview/OverviewPanel";
import { ApiError, compare, getPlayer } from "@/lib/api";
import { isValidSteamId } from "@/lib/steamId";
import type { Comparison, Player } from "@/lib/types";

const INVALID = {
  title: "Invalid SteamID64",
  message: "One of these SteamID64s is invalid.",
};

type Result =
  | { status: "ready"; comparison: Comparison; playerA: Player; playerB: Player }
  | { status: "error"; title: string; message: string };

function describeError(error: unknown): Result {
  if (error instanceof ApiError) {
    if (error.status === 403 || error.status === 404) {
      return { status: "error", title: "Comparison unavailable", message: error.detail };
    }
    if (error.status === 422) {
      return { status: "error", ...INVALID };
    }
  }
  return {
    status: "error",
    title: "Steam unavailable",
    message: "Steam couldn’t be reached. Try again.",
  };
}

export default function ComparisonView() {
  const router = useRouter();
  const params = useSearchParams();
  const a = (params.get("a") ?? "").trim();
  const b = (params.get("b") ?? "").trim();
  const key = `${a}:${b}`;
  const valid = isValidSteamId(a) && isValidSteamId(b) && a !== b;

  const [loaded, setLoaded] = useState<{ key: string; result: Result } | null>(null);

  useEffect(() => {
    if (!valid) return;

    let active = true;
    Promise.all([compare(a, b), getPlayer(a), getPlayer(b)])
      .then(([comparison, playerA, playerB]) => {
        if (active) {
          setLoaded({ key, result: { status: "ready", comparison, playerA, playerB } });
        }
      })
      .catch((error) => {
        if (active) setLoaded({ key, result: describeError(error) });
      });

    return () => {
      active = false;
    };
  }, [a, b, key, valid]);

  const result = loaded?.key === key ? loaded.result : null;

  let content;
  if (!valid) {
    content = <StatusMessage {...INVALID} />;
  } else if (result === null) {
    content = (
      <StatusMessage
        title="Comparing players…"
        message="The first comparison of a large library can take a minute."
      />
    );
  } else if (result.status === "error") {
    content = <StatusMessage title={result.title} message={result.message} />;
  } else {
    const { comparison, playerA, playerB } = result;
    content = (
      <div className="space-y-12">
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-6">
          <PlayerHeader player={playerA} />
          <span className="text-lg text-muted">vs</span>
          <PlayerHeader player={playerB} />
        </div>
        <OverviewPanel comparison={comparison} playerA={playerA} playerB={playerB} />
        <LibrarySection steamIdA={a} steamIdB={b} />
        <AdvancedTab steamIdA={a} steamIdB={b} sharedGames={comparison.shared_games} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Comparison</h1>
        <button
          type="button"
          onClick={() => router.push("/")}
          className="rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground"
        >
          Reset View
        </button>
      </div>
      {content}
    </div>
  );
}
