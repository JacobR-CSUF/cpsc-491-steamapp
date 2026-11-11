"use client";

import { formatNumber } from "@/lib/format";
import { useEffect, useId, useState } from "react";
import {
  CHUNK_STYLES,
  type Chunk,
  type PrivCapScreen,
} from "@/lib/privcap";

interface ChunkGridProps {
  screen: PrivCapScreen;
  onComplete: () => void;
}

export default function ChunkGrid({
  screen,
  onComplete,
}: ChunkGridProps) {
  const headingId = useId();
  const instructionId = useId();
  const [selected, setSelected] = useState<Set<string>>(() => new Set());

  const orangeChunks = screen.chunks.filter(
    (chunk) => chunk.color === "orange",
  );
  const allFound = orangeChunks.every((chunk) => selected.has(chunk.id));

  // Reveal one additional chunk for each new correct click.
  let visibleCount = Math.min(9 + selected.size, screen.chunks.length);

  const hasVisibleOrange = screen.chunks
    .slice(0, visibleCount)
    .some((chunk) => chunk.color === "orange" && !selected.has(chunk.id));

  // Avoid a dead end if the remaining orange chunks are hidden.
  if (
    allFound ||
    (!hasVisibleOrange && visibleCount < screen.chunks.length)
  ) {
    visibleCount = screen.chunks.length;
  }

  useEffect(() => {
    if (!allFound) return;

    const timer = window.setTimeout(onComplete, 5000);
    return () => window.clearTimeout(timer);
  }, [allFound, onComplete]);

  function chooseChunk(chunk: Chunk) {
    if (allFound || chunk.color !== "orange" || selected.has(chunk.id)) {
      return;
    }

    setSelected((previous) => {
      if (previous.has(chunk.id)) return previous;

      const next = new Set(previous);
      next.add(chunk.id);
      return next;
    });
  }

  return (
    <section
      aria-labelledby={headingId}
      aria-describedby={instructionId}
      className="space-y-4"
    >
      <p
        id={instructionId}
        className="rounded-xl bg-background px-4 py-3 text-sm font-medium"
      >
        Click every orange chunk showing data we collect
      </p>

      <h3 id={headingId} className="text-lg font-semibold">
        {screen.category}
      </h3>

      <div
        role="group"
        aria-label={`${screen.category} privacy facts`}
        aria-disabled={allFound}
        className="grid grid-cols-3 gap-2 sm:gap-3"
      >
        {screen.chunks.slice(0, visibleCount).map((chunk) => {
          const styles = CHUNK_STYLES[chunk.color];
          const pressed = selected.has(chunk.id);

          return (
            <button
              key={chunk.id}
              type="button"
              aria-label={`${styles.meaning}: ${chunk.text}`}
              aria-pressed={pressed}
              aria-disabled={allFound}
              onClick={() => chooseChunk(chunk)}
              className={`aspect-square min-w-0 overflow-y-auto rounded-lg p-2 text-center text-xs leading-snug font-medium break-words focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent sm:p-3 sm:text-sm ${
                pressed ? styles.selectedClasses : styles.classes
              } ${allFound ? "cursor-default" : "cursor-pointer"}`}
            >
              {chunk.text}
            </button>
          );
        })}
      </div>

      <p role="status" aria-live="polite" className="min-h-10 text-sm text-muted">
        {allFound
          ? "All orange chunks found. Take five seconds to read the other facts."
          : `${formatNumber(selected.size)} of ${formatNumber(orangeChunks.length)} orange chunks found`}
      </p>
    </section>
  );
}