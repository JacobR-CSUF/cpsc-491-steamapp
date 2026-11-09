"use client";

import { useEffect, useState } from "react";
import { ApiError, getAdvancedStats } from "@/lib/api";
import { formatPercent } from "@/lib/format";
import type { AdvancedStats } from "@/lib/types";

const FIRST_ROWS = 10;

interface MissingAchievementsPanelProps {
  steamId: string;
  appId: number;
  name: string;
}

type Result =
  | { status: "ready"; stats: AdvancedStats }
  | { status: "error"; message: string };

export default function MissingAchievementsPanel({
  steamId,
  appId,
  name,
}: MissingAchievementsPanelProps) {
  const key = `${steamId}:${appId}`;
  const [loaded, setLoaded] = useState<{ key: string; result: Result } | null>(null);
  const [showAllKey, setShowAllKey] = useState<string | null>(null);

  // Load again whenever the selected game (appId) changes.
  useEffect(() => {
    let active = true;
    getAdvancedStats(steamId, appId)
      .then((stats) => {
        if (active) setLoaded({ key, result: { status: "ready", stats } });
      })
      .catch((error) => {
        const message =
          error instanceof ApiError && (error.status === 403 || error.status === 404)
            ? error.detail
            : "Achievements couldn’t be loaded. Try again.";
        if (active) setLoaded({ key, result: { status: "error", message } });
      });

    return () => {
      active = false;
    };
  }, [key, steamId, appId]);

  const result = loaded?.key === key ? loaded.result : null;
  const showAll = showAllKey === key;

  let body;
  if (result === null) {
    body = <p className="text-sm text-muted">Loading achievements…</p>;
  } else if (result.status === "error") {
    body = <p className="text-sm text-muted">{result.message}</p>;
  } else {
    const { stats } = result;
    const shown = showAll ? stats.missing : stats.missing.slice(0, FIRST_ROWS);
    const hidden = stats.missing.length - shown.length;

    body = (
      <div className="space-y-5">
        <div className="space-y-2">
          <div className="flex items-baseline justify-between text-sm">
            <span>
              {stats.unlocked} of {stats.total}
            </span>
            <span className="font-semibold text-accent">{formatPercent(stats.ratio)}</span>
          </div>
          <div
            role="progressbar"
            aria-label={`${name} achievement ratio`}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={stats.ratio}
            className="h-2 overflow-hidden rounded-full bg-white/10"
          >
            <div className="h-full rounded-full bg-accent" style={{ width: `${stats.ratio}%` }} />
          </div>
        </div>

        {stats.total === 0 ? (
          <p className="text-sm text-muted">This game has no achievements</p>
        ) : stats.missing.length === 0 ? (
          <p className="text-sm text-muted">All achievements unlocked</p>
        ) : (
          <div className="space-y-3">
            <ul className="space-y-3">
              {shown.map((achievement) => (
                <li key={achievement.api_name} className="flex items-start gap-3">
                  {achievement.icon_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={achievement.icon_url}
                      alt=""
                      width={40}
                      height={40}
                      className="h-10 w-10 shrink-0 rounded"
                    />
                  ) : (
                    <span className="h-10 w-10 shrink-0 rounded bg-white/10" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-foreground">
                      {achievement.display_name}
                    </p>
                    {achievement.description && (
                      <p className="text-sm text-muted">{achievement.description}</p>
                    )}
                  </div>
                  {achievement.global_percent !== null && (
                    <span className="shrink-0 text-xs text-muted">
                      {formatPercent(achievement.global_percent)} of players
                    </span>
                  )}
                </li>
              ))}
            </ul>
            {hidden > 0 && (
              <button
                type="button"
                onClick={() => setShowAllKey(key)}
                className="rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground"
              >
                Show all ({hidden} more)
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded-xl bg-background/40 p-5 ring-1 ring-white/10">
      <h4 className="font-semibold tracking-tight">{name}</h4>
      {body}
    </div>
  );
}
