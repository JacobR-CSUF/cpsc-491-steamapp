"use client";

import SafeImage from "@/components/SafeImage";
import { useId, useState } from "react";
import { formatDate } from "@/lib/format";
import type { Achievement } from "@/lib/types";

export interface AchievementSelection {
  achievement: Achievement;
  unlockedAtA: string | null;
  unlockedAtB: string | null;
  unlockedA?: boolean;
  unlockedB?: boolean;
}

export function unlockLabel(date: string | null, unlocked = date !== null) {
  return unlocked ? date ? formatDate(date) : "Unlocked (date unavailable)" : "Locked";
}

interface AchievementIconProps extends AchievementSelection {
  onSelect?: (selection: AchievementSelection) => void;
}

export default function AchievementIcon({ achievement, unlockedAtA, unlockedAtB, unlockedA = unlockedAtA !== null, unlockedB = unlockedAtB !== null, onSelect }: AchievementIconProps) {
  const tooltipId = useId();
  const [position, setPosition] = useState({ left: 0, top: 0 });

  function positionTooltip(element: HTMLElement) {
    const rect = element.getBoundingClientRect();
    setPosition({ left: Math.max(8, Math.min(rect.left, window.innerWidth - 264)), top: rect.top });
  }

  return (
    <div className="group">
      <button
        type="button"
        aria-label={achievement.display_name}
        aria-describedby={tooltipId}
        onMouseEnter={(event) => positionTooltip(event.currentTarget)}
        onFocus={(event) => positionTooltip(event.currentTarget)}
        onClick={() => onSelect?.({ achievement, unlockedAtA, unlockedAtB, unlockedA, unlockedB })}
        className={`flex h-14 w-14 items-center justify-center overflow-hidden rounded-lg bg-background transition-shadow focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent ${unlockedA && unlockedB ? "ring-2 ring-accent ring-offset-2 ring-offset-panel" : "ring-1 ring-white/10"}`}
      >
        {achievement.icon_url ? (
          <SafeImage src={achievement.icon_url} alt="" width={56} height={56} loading="lazy" className={`h-full w-full object-cover ${!unlockedA && !unlockedB ? "grayscale opacity-50" : ""}`} />
        ) : (
          <span aria-hidden="true" className={`text-xl text-accent ${!unlockedA && !unlockedB ? "grayscale opacity-50" : ""}`}>★</span>
        )}
      </button>
      <div
        id={tooltipId}
        role="tooltip"
        style={{ left: position.left, top: position.top }}
        className="pointer-events-none fixed z-30 hidden w-64 -translate-y-full rounded-lg border border-white/20 bg-background p-3 text-sm shadow-xl group-hover:block group-focus-within:block"
      >
        <p className="mb-1 font-semibold">{achievement.display_name}</p>
        <p className="text-muted">Player A: {unlockLabel(unlockedAtA, unlockedA)}</p>
        <p className="text-muted">Player B: {unlockLabel(unlockedAtB, unlockedB)}</p>
      </div>
    </div>
  );
}
