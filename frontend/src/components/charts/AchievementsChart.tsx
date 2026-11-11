"use client";

import { formatNumber } from "@/lib/format";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_TOOLTIP_STYLE, PLAYER_COLORS } from "@/components/charts/colors";
import type { PlayerStats } from "@/lib/types";

interface AchievementsChartProps {
  statsA: PlayerStats;
  statsB: PlayerStats;
  nameA: string;
  nameB: string;
}

export default function AchievementsChart({ statsA, statsB, nameA, nameB }: AchievementsChartProps) {
  const data = [
    { label: "Unlocked", a: statsA.achievements_unlocked, b: statsB.achievements_unlocked },
    { label: "Available", a: statsA.achievements_available, b: statsB.achievements_available },
  ];

  return (
    <div className="max-w-full overflow-x-auto">
    <div className="min-w-[20rem] h-80 w-full" role="group" aria-label="Achievement totals chart">
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <BarChart data={data} margin={{ top: 16, right: 8, bottom: 8, left: 0 }} accessibilityLayer>
          <CartesianGrid stroke="#8f98a0" strokeOpacity={0.15} vertical={false} />
          <XAxis dataKey="label" stroke="#8f98a0" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tickFormatter={(value: number) => formatNumber(value)} stroke="#8f98a0" width={52} tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "#ffffff", fillOpacity: 0.05 }} formatter={(value) => formatNumber(Number(value))} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="a" name={nameA} fill={PLAYER_COLORS.a} radius={[4, 4, 0, 0]} />
          <Bar dataKey="b" name={nameB} fill={PLAYER_COLORS.b} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
    </div>
  );
}
