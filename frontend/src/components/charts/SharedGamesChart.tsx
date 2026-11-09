"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_TOOLTIP_STYLE, PLAYER_COLORS } from "@/components/charts/colors";
import type { SharedGame } from "@/lib/types";

interface SharedGamesChartProps {
  sharedGames: SharedGame[];
  nameA: string;
  nameB: string;
}

export default function SharedGamesChart({ sharedGames, nameA, nameB }: SharedGamesChartProps) {
  const data = [...sharedGames].sort((a, b) => Math.abs(b.difference) - Math.abs(a.difference)).slice(0, 10);
  if (data.length === 0) return <p className="flex h-80 items-center justify-center text-sm text-muted">No shared games.</p>;

  return (
    <div className="h-[28rem] w-full" role="group" aria-label="Shared game achievement gaps chart">
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 12, bottom: 8, left: 0 }} accessibilityLayer>
          <CartesianGrid stroke="#8f98a0" strokeOpacity={0.15} horizontal={false} />
          <XAxis type="number" allowDecimals={false} stroke="#8f98a0" tick={{ fontSize: 12 }} />
          <YAxis dataKey="name" type="category" width={100} interval={0} stroke="#8f98a0" tick={{ fontSize: 11 }} tickFormatter={(name: string) => name.length > 14 ? `${name.slice(0, 13)}…` : name} />
          <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "#ffffff", fillOpacity: 0.05 }} formatter={(value) => Number(value).toLocaleString("en-US")} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="unlocked_a" name={nameA} fill={PLAYER_COLORS.a} radius={[0, 3, 3, 0]} />
          <Bar dataKey="unlocked_b" name={nameB} fill={PLAYER_COLORS.b} radius={[0, 3, 3, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
