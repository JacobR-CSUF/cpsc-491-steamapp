"use client";

import { formatNumber } from "@/lib/format";
import { LoadingSkeleton } from "@/components/Skeleton";
import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CHART_TOOLTIP_STYLE, PLAYER_COLORS } from "@/components/charts/colors";
import { getAchievementTimeline } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import type { TimelineDays } from "@/lib/types";

const DAY_OPTIONS: TimelineDays[] = [30, 60, 90];
type Scope = "game" | "all";

interface TimelineChartProps {
  steamIdA: string;
  steamIdB: string;
  appId: number;
  nameA: string;
  nameB: string;
}

interface ChartPoint {
  date: string;
  a: number;
  b: number;
}

type Result =
  | { status: "ready"; points: ChartPoint[]; totalA: number; totalB: number }
  | { status: "error"; message: string };

// Dates arrive as "YYYY-MM-DD" UTC days. Format them in UTC so a Pacific-time
// browser doesn't shift "2026-11-08" back to Nov 7.
const shortDate = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  timeZone: "UTC",
});
const longDate = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});
const toUtc = (day: string) => new Date(`${day}T00:00:00Z`);

const toggleClass = (active: boolean) =>
  `action-button rounded-full px-3 py-1 text-sm transition-colors ${
    active
      ? "bg-accent text-background"
      : "border border-white/10 text-muted hover:border-white/20 hover:text-foreground"
  }`;

export default function TimelineChart({
  steamIdA,
  steamIdB,
  appId,
  nameA,
  nameB,
}: TimelineChartProps) {
  const [days, setDays] = useState<TimelineDays>(30);
  const [scope, setScope] = useState<Scope>("game");

  const gameId = scope === "game" ? appId : undefined;
  const key = `${steamIdA}:${steamIdB}:${formatNumber(days)}:${gameId ?? "all"}`;
  const [loaded, setLoaded] = useState<{ key: string; result: Result } | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      getAchievementTimeline(steamIdA, days, gameId),
      getAchievementTimeline(steamIdB, days, gameId),
    ])
      .then(([timelineA, timelineB]) => {
        // Merge the two point lists by date.
        const byDate = new Map<string, ChartPoint>();
        for (const point of timelineA.points) {
          byDate.set(point.date, { date: point.date, a: point.unlocked, b: 0 });
        }
        for (const point of timelineB.points) {
          const row = byDate.get(point.date) ?? { date: point.date, a: 0, b: 0 };
          row.b = point.unlocked;
          byDate.set(point.date, row);
        }
        const points = [...byDate.values()].sort((x, y) => x.date.localeCompare(y.date));
        if (active) {
          setLoaded({
            key,
            result: {
              status: "ready",
              points,
              totalA: timelineA.total,
              totalB: timelineB.total,
            },
          });
        }
      })
      .catch((error) => {
        if (active) setLoaded({ key, result: { status: "error", message: errorMessage(error) } });
      });

    return () => {
      active = false;
    };
  }, [key, steamIdA, steamIdB, days, gameId]);

  const result = loaded?.key === key ? loaded.result : null;

  let body;
  if (result === null) {
    body = <LoadingSkeleton variant="chart" label="Loading activity…" />;
  } else if (result.status === "error") {
    body = <p role="alert" className="text-sm text-muted">{result.message}</p>;
  } else if (result.totalA === 0 && result.totalB === 0) {
    body = <p className="text-sm text-muted">No unlocks in the last {formatNumber(days)} days</p>;
  } else {
    body = (
      <div className="space-y-4">
        <div className="flex flex-wrap gap-6 text-sm">
          <p>
            <span title={nameA} className="inline-block max-w-full truncate align-bottom font-semibold" style={{ color: PLAYER_COLORS.a }}>
              {nameA}
            </span>{" "}
            <span className="text-muted">{formatNumber(result.totalA)} unlocks</span>
          </p>
          <p>
            <span title={nameB} className="inline-block max-w-full truncate align-bottom font-semibold" style={{ color: PLAYER_COLORS.b }}>
              {nameB}
            </span>{" "}
            <span className="text-muted">{formatNumber(result.totalB)} unlocks</span>
          </p>
        </div>
        {/* ResponsiveContainer needs a parent with a fixed height. */}
        <div className="max-w-full overflow-x-auto">
        <div className="h-72 min-w-[20rem] w-full" role="group" aria-label="Daily achievement unlocks chart">
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <LineChart
              data={result.points}
              margin={{ top: 8, right: 16, bottom: 0, left: -16 }}
              accessibilityLayer
            >
              <CartesianGrid stroke="#8f98a0" strokeOpacity={0.15} vertical={false} />
              <XAxis
                dataKey="date"
                tickFormatter={(day: string) => shortDate.format(toUtc(day))}
                stroke="#8f98a0"
                tick={{ fontSize: 12 }}
                minTickGap={24}
              />
              <YAxis tickFormatter={(value: number) => formatNumber(value)} allowDecimals={false} stroke="#8f98a0" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={CHART_TOOLTIP_STYLE}
                formatter={(value) => formatNumber(Number(value))}
                labelFormatter={(day) => longDate.format(toUtc(String(day)))}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line
                type="linear"
                dataKey="a"
                name={nameA}
                stroke={PLAYER_COLORS.a}
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="linear"
                dataKey="b"
                name={nameB}
                stroke={PLAYER_COLORS.b}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 min-w-0 rounded-2xl bg-panel p-4 sm:p-6 ring-1 ring-white/10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h4 className="font-semibold tracking-tight">Achievement activity</h4>
        <div className="flex flex-wrap gap-4">
          <div className="flex flex-wrap gap-2" role="group" aria-label="Time range">
            {DAY_OPTIONS.map((option) => (
              <button
                key={option}
                type="button"
                aria-pressed={days === option}
                onClick={() => setDays(option)}
                className={toggleClass(days === option)}
              >
                {formatNumber(option)} days
              </button>
            ))}
          </div>
          <div className="flex gap-2" role="group" aria-label="Games">
            <button
              type="button"
              aria-pressed={scope === "game"}
              onClick={() => setScope("game")}
              className={toggleClass(scope === "game")}
            >
              This game
            </button>
            <button
              type="button"
              aria-pressed={scope === "all"}
              onClick={() => setScope("all")}
              className={toggleClass(scope === "all")}
            >
              All games
            </button>
          </div>
        </div>
      </div>
      {body}
    </div>
  );
}
