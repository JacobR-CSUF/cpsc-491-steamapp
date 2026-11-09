"use client";

import { useEffect, useId, useRef } from "react";
import { unlockLabel, type AchievementSelection } from "@/components/overview/AchievementIcon";

interface AchievementDetailCardProps extends AchievementSelection {
  nameA: string;
  nameB: string;
  onClose: () => void;
}

export default function AchievementDetailCard({ achievement, unlockedAtA, unlockedAtB, unlockedA = unlockedAtA !== null, unlockedB = unlockedAtB !== null, nameA, nameB, onClose }: AchievementDetailCardProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    const dialog = dialogRef.current;
    const previousFocus = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    dialog?.showModal();
    closeRef.current?.focus();
    document.body.style.overflow = "hidden";
    return () => {
      dialog?.close();
      document.body.style.overflow = previousOverflow;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    };
  }, []);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
      onCancel={(event) => { event.preventDefault(); onClose(); }}
      onKeyDown={(event) => {
        if (event.key === "Tab") {
          event.preventDefault();
          closeRef.current?.focus();
        }
      }}
      onClick={(event) => { if (event.target === event.currentTarget) onClose(); }}
      className="fixed inset-0 m-auto max-h-[85vh] w-[calc(100%_-_2rem)] max-w-lg overflow-y-auto rounded-2xl border border-white/20 bg-panel p-0 text-foreground shadow-2xl backdrop:bg-black/75"
    >
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex min-w-0 items-center gap-4">
            {achievement.icon_url && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={achievement.icon_url} alt="" width={64} height={64} className="h-16 w-16 shrink-0 rounded-lg" />
            )}
            <h2 id={titleId} className="break-words text-xl font-semibold text-accent">{achievement.display_name}</h2>
          </div>
          <button ref={closeRef} type="button" aria-label="Close" onClick={onClose} className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/10 text-xl text-muted hover:border-accent/60 hover:text-accent focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent">×</button>
        </div>
        <p id={descriptionId} className="mt-6 whitespace-pre-wrap break-words text-sm leading-relaxed text-muted">
          {achievement.description ?? (achievement.hidden ? "Hidden achievement" : "No description")}
        </p>
        <dl className="mt-6 grid gap-4 border-t border-white/10 pt-5 sm:grid-cols-2">
          <div className="min-w-0">
            <dt className="break-words text-sm text-muted">{nameA}</dt>
            <dd className="mt-1 font-medium">{unlockLabel(unlockedAtA, unlockedA)}</dd>
          </div>
          <div className="min-w-0">
            <dt className="break-words text-sm text-muted">{nameB}</dt>
            <dd className="mt-1 font-medium">{unlockLabel(unlockedAtB, unlockedB)}</dd>
          </div>
        </dl>
      </div>
    </dialog>
  );
}
