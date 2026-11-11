import { LoadingSkeleton } from "@/components/Skeleton";
import { useEffect, useId, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PLAYER_COLORS } from "@/components/charts/colors";
import StatusMessage from "@/components/compare/StatusMessage";
import { getPlaytimeGraph } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import { formatDate, formatHours, formatNumber } from "@/lib/format";
import type { PlaytimeGraph as PlaytimeGraphData } from "@/lib/types";

/*
PlaytimeGraph component is responsible for displaying a graph of achievements unlocked against estimated hours played for a specific game.
  It fetches the playtime graph data from the Steam API and displays it in a line chart using Recharts.
  The component handles loading states, error states, and provides accessibility features like focus management and keyboard navigation.
*/

interface PlaytimeGraphProps {
  steamId: string;
  appId: number;
}

type Result =
  | { status: "ready"; graph: PlaytimeGraphData }
  | { status: "error"; title: string; message: string };

interface Datum {
  time: number;
  hours: number;
  name: string;
  unlockedAt: string;
}

// Recharts draws in SVG, so these are plain colors that match the theme.
const MUTED = "#8f98a0";
const GRID = "rgba(255, 255, 255, 0.08)";

function describeError(error: unknown): Result {
  return {
    status: "error",
    title: "Playtime graph unavailable",
    message: errorMessage(error),
  };
}

function formatTick(time: number): string {
  return formatDate(new Date(time).toISOString());
}

// Pick a few evenly spaced dates for the x-axis. Recharts' own tick generator
// repeats a tick when every unlock happened at (nearly) the same moment, which
// is common when Steam syncs old achievements, so we skip labels that repeat.
function buildTicks(min: number, max: number): number[] {
  const ticks: number[] = [];
  const seen = new Set<string>();
  const steps = min === max ? 1 : 4;
  for (let i = 0; i < steps; i++) {
    const time = steps === 1 ? min : Math.round(min + ((max - min) * i) / (steps - 1));
    const label = formatTick(time);
    if (!seen.has(label)) {
      seen.add(label);
      ticks.push(time);
    }
  }
  return ticks;
}

function PointTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: readonly { payload?: Datum }[];
}) {
  const point = payload?.[0]?.payload;
  if (!active || !point) return null;

  return (
    <div className="max-w-56 rounded-lg bg-background px-3 py-2 text-xs shadow-lg ring-1 ring-white/15">
      <p className="font-medium text-foreground">{point.name}</p>
      <p className="mt-1 text-muted">{formatDate(point.unlockedAt)}</p>
      <p className="text-muted">
        Estimated hours:{" "}
        <span className="font-semibold text-accent">{formatHours(point.hours * 60)}</span>
      </p>
    </div>
  );
}

function Chart({ graph }: { graph: PlaytimeGraphData }) {
  const data: Datum[] = graph.points
    .map((point) => ({
      time: new Date(point.unlocked_at).getTime(),
      hours: point.estimated_hours,
      name: point.display_name,
      unlockedAt: point.unlocked_at,
    }))
    .sort((a, b) => a.time - b.time);
  const ticks = buildTicks(data[0].time, data[data.length - 1].time);

  return (
    <div className="min-w-0 max-w-full space-y-2 overflow-x-auto">
      {/* ResponsiveContainer needs a parent with a fixed height. */}
      <div
        role="img"
        aria-label={`Chart of ${data.length} unlocked ${data.length === 1 ? "achievement" : "achievements"} against estimated hours played`}
        className="h-64 min-w-[20rem] w-full"
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
            <CartesianGrid stroke={GRID} vertical={false} />
            <XAxis
              dataKey="time"
              type="number"
              scale="time"
              domain={["dataMin", "dataMax"]}
              padding={{ left: 16, right: 16 }}
              tickFormatter={formatTick}
              ticks={ticks}
              tick={{ fill: MUTED, fontSize: 11 }}
              stroke={GRID}
            />
            <YAxis
              tickFormatter={(value: number) => formatNumber(value, 1)}
              dataKey="hours"
              width={56}
              tick={{ fill: MUTED, fontSize: 11 }}
              stroke={GRID}
              label={{
                value: "Estimated hours",
                angle: -90,
                position: "insideLeft",
                offset: 8,
                style: { fill: MUTED, fontSize: 11, textAnchor: "middle" },
              }}
            />
            <Tooltip
              content={<PointTooltip />}
              cursor={{ stroke: MUTED, strokeDasharray: "3 3" }}
            />
            <Line
              type="monotone"
              dataKey="hours"
              stroke={PLAYER_COLORS.a}
              strokeWidth={2}
              dot={{ r: 3, fill: PLAYER_COLORS.a, stroke: PLAYER_COLORS.a }}
              activeDot={{ r: 5 }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {graph.estimated && (
        <p className="text-xs text-muted">
          Hours are estimated from when each achievement was unlocked.
        </p>
      )}
    </div>
  );
}

export default function PlaytimeGraph({ steamId, appId }: PlaytimeGraphProps) {
  const panelId = useId();
  const key = `${steamId}:${appId}`;
  const [open, setOpen] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [loaded, setLoaded] = useState<{ key: string; result: Result } | null>(null);

  const result = loaded?.key === key ? loaded.result : null;
  const needsLoad = open && result === null;

  // Load once, the first time the card is expanded.
  useEffect(() => {
    if (!needsLoad) return;
    let active = true;
    getPlaytimeGraph(steamId, appId)
      .then((graph) => {
        if (active) setLoaded({ key, result: { status: "ready", graph } });
      })
      .catch((error) => {
        if (active) setLoaded({ key, result: describeError(error) });
      });

    return () => {
      active = false;
    };
  }, [needsLoad, steamId, appId, key, attempt]);

  function retry() {
    setLoaded(null);
    setAttempt((count) => count + 1);
  }

  let body;
  if (result === null) {
    body = (
      <LoadingSkeleton variant="chart" label="Loading playtime graph…" />
    );
  } else if (result.status === "error") {
    body = (
      <div className="space-y-3">
        <StatusMessage title={result.title} message={result.message} />
        <button
          type="button"
          onClick={retry}
          className="action-button rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground"
        >
          Try again
        </button>
      </div>
    );
  } else if (result.graph.points.length === 0) {
    body = <p className="text-sm text-muted">No achievements unlocked yet</p>;
  } else {
    body = <Chart graph={result.graph} />;
  }

  return (
    <div className="rounded-xl bg-background/60 ring-1 ring-white/10">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        aria-controls={panelId}
        className="flex w-full items-center justify-between gap-3 rounded-xl px-4 py-3 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
      >
        <span>
          <span className="block text-sm font-medium text-foreground">Playtime</span>
          <span className="block text-xs text-muted">
            {open ? "Achievements unlocked vs. hours played" : "Show achievements vs. hours played"}
          </span>
        </span>
        <svg
          viewBox="0 0 16 16"
          width="14"
          height="14"
          aria-hidden="true"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`}
        >
          <path d="M3 6l5 5 5-5" />
        </svg>
      </button>
      {open && (
        <div id={panelId} className="border-t border-white/10 p-4">
          {body}
        </div>
      )}
    </div>
  );
}
