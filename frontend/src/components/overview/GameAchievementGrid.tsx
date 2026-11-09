"use client";

import { useEffect, useState } from "react";
import AchievementIcon, { type AchievementSelection } from "@/components/overview/AchievementIcon";
import { getGameAchievements } from "@/lib/api";

interface GameAchievementGridProps {
  appId: number;
  steamIdA: string;
  steamIdB: string;
  onSelect?: (selection: AchievementSelection) => void;
}

type Result = { items: AchievementSelection[] } | { error: string };

export default function GameAchievementGrid({ appId, steamIdA, steamIdB, onSelect }: GameAchievementGridProps) {
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    Promise.all([getGameAchievements(steamIdA, appId), getGameAchievements(steamIdB, appId)])
      .then(([a, b]) => {
        const mapA = new Map(a.map((item) => [item.api_name, item]));
        const mapB = new Map(b.map((item) => [item.api_name, item]));
        const keys = new Set([...mapA.keys(), ...mapB.keys()]);
        const items = Array.from(keys, (key): AchievementSelection => {
          const first = mapA.get(key);
          const second = mapB.get(key);
          const achievement = (first ?? second)!;
          return {
            achievement: { ...achievement, description: first?.description ?? second?.description ?? null, icon_url: first?.icon_url ?? second?.icon_url ?? null },
            unlockedAtA: first?.achieved ? first.unlocked_at : null,
            unlockedAtB: second?.achieved ? second.unlocked_at : null,
            unlockedA: first?.achieved ?? false,
            unlockedB: second?.achieved ?? false,
          };
        });
        if (active) setResult({ items });
      })
      .catch(() => {
        if (active) setResult({ error: "Achievements couldn’t be loaded. Try again." });
      });
    return () => { active = false; };
  }, [appId, steamIdA, steamIdB, attempt]);

  if (!result) return <p role="status" className="py-4 text-sm text-muted">Loading achievements…</p>;
  if ("error" in result) return (
    <div role="alert" className="space-y-2 py-4 text-sm text-muted">
      <p>{result.error}</p>
      <button type="button" className="text-accent hover:underline" onClick={() => { setResult(null); setAttempt((value) => value + 1); }}>Retry</button>
    </div>
  );
  if (result.items.length === 0) return <p className="py-4 text-sm text-muted">No achievements for this game.</p>;

  return (
    <div className="flex flex-wrap gap-4 py-4">
      {result.items.map((item) => <AchievementIcon key={item.achievement.api_name} {...item} onSelect={onSelect} />)}
    </div>
  );
}
