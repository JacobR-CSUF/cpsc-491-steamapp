"use client";

import { LoadingSkeleton } from "@/components/Skeleton";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import AdvancedTab from "@/components/advanced/AdvancedTab";
import PlayerHeader from "@/components/compare/PlayerHeader";
import StatusMessage from "@/components/compare/StatusMessage";
import LibrarySection from "@/components/library/LibrarySection";
import OverviewPanel from "@/components/overview/OverviewPanel";
import { compare, getPlayer } from "@/lib/api";
import { isValidSteamId } from "@/lib/steamId";
import type { Comparison, Player } from "@/lib/types";
import Link from "next/link";
import { errorMessage } from "@/lib/errors";
import PrivCaptcha from "@/components/privacy/PrivCaptcha";
import { hasCompletedPrivCap } from "@/lib/privcap";

type Result =
  | { status: "ready"; comparison: Comparison; playerA: Player; playerB: Player }
  | { status: "error"; title: string; message: string };

function describeError(error: unknown): Result {
  return {
    status: "error",
    title: "Comparison unavailable",
    message: errorMessage(error),
  };
}

function ComparisonResults() {
  const router = useRouter();
  const params = useSearchParams();
  const a = (params.get("a") ?? "").trim();
  const b = (params.get("b") ?? "").trim();
  const key = `${a}:${b}`;
  const valid = isValidSteamId(a) && isValidSteamId(b);
  const samePlayer = valid && a === b;
  const [attempt, setAttempt] = useState(0);
  const [loaded, setLoaded] = useState<{ key: string; result: Result } | null>(null);

  useEffect(() => {
    if (!valid || samePlayer) return;

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
  }, [a, b, key, valid, samePlayer, attempt]);

  const result = loaded?.key === key ? loaded.result : null;
    function retry() {
    setLoaded(null);
    setAttempt((value) => value + 1);
  }

  let content;
  if (!valid || samePlayer) {
    content = (
      <div className="space-y-4 text-center">
        <StatusMessage
          title="Comparison unavailable"
          message={
            samePlayer
              ? "Choose two different Steam profiles."
              : "This comparison link is incomplete."
          }
        />
        <Link href="/" className="text-accent underline-offset-4 hover:underline">
          Back to Compare
        </Link>
      </div>
    );
  } else if (result === null) {
    content = (
      <LoadingSkeleton variant="overview" label="Comparing players… The first comparison of a large library can take a minute." />
    );
  } else if (result.status === "error") {
    content = (
      <StatusMessage
        title={result.title}
        message={result.message}
        onRetry={retry}
      />
    );
    } else {
    const { comparison, playerA, playerB } = result;
    content = (
      <div className="space-y-12">
        <div className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-3 sm:gap-6">
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
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Comparison</h1>
        <button
          type="button"
          onClick={() => router.push("/")}
          className="action-button rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground"
        >
          Reset View
        </button>
      </div>
      {content}
    </div>
  );
}

export default function ComparisonView() {
  const router = useRouter();
  const params = useSearchParams();
  const a = (params.get("a") ?? "").trim();
  const b = (params.get("b") ?? "").trim();
  const valid = isValidSteamId(a) && isValidSteamId(b) && a !== b;

  const [allowed, setAllowed] = useState<boolean | null>(null);

  useEffect(() => {
    // Read browser storage after mounting, never during server rendering.
    const timer = window.setTimeout(() => {
      setAllowed(hasCompletedPrivCap());
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  // KAN-70 handles these links without making backend requests.
  if (!valid) {
    return <ComparisonResults />;
  }

  if (allowed === null) {
    return (
      <StatusMessage
        title="Preparing comparison…"
        message="Checking whether you have completed the privacy check."
      />
    );
  }

  if (!allowed) {
    return (
      <PrivCaptcha
        onComplete={() => setAllowed(true)}
        onClose={() => router.replace("/")}
      />
    );
  }

  return <ComparisonResults />;
}
