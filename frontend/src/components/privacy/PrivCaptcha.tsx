"use client";

import { formatNumber } from "@/lib/format";
import { useCallback, useEffect, useId, useRef, useState } from "react";
import ChunkGrid from "@/components/privacy/ChunkGrid";
import {
  CHUNK_STYLES,
  PRIVCAP_SCREENS,
  markPrivCapComplete,
  type ChunkColor,
} from "@/lib/privcap";

interface PrivCaptchaProps {
  onComplete: () => void;
  onClose: () => void;
}

const COLORS: ChunkColor[] = ["orange", "teal", "yellow", "pink"];

const BUTTON_CLASS =
  "action-button rounded-full bg-accent px-6 py-2 text-sm font-semibold text-background transition-opacity hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

export default function PrivCaptcha({
  onComplete,
  onClose,
}: PrivCaptchaProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const titleId = useId();

  // -1 is the legend; the final index is the completion screen.
  const [step, setStep] = useState(-1);
  const finished = step === PRIVCAP_SCREENS.length;
  const screen = step >= 0 && !finished ? PRIVCAP_SCREENS[step] : null;

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    const previousFocus = document.activeElement;
    const previousOverflow = document.body.style.overflow;

    dialog.showModal();
    document.body.style.overflow = "hidden";

    return () => {
      dialog.close();
      document.body.style.overflow = previousOverflow;

      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) {
        previousFocus.focus({ preventScroll: true });
      }
    };
  }, []);

  useEffect(() => {
    headingRef.current?.focus({ preventScroll: true });
    dialogRef.current?.scrollTo({ top: 0 });
  }, [step]);

  const advance = useCallback(() => {
    setStep((current) => current + 1);
  }, []);

  function finish() {
    markPrivCapComplete();
    onComplete();
  }

  return (
    <dialog
      ref={dialogRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      className="fixed inset-0 m-auto max-h-[90dvh] w-[calc(100%_-_2rem)] max-w-xl overflow-y-auto rounded-2xl border border-white/10 bg-panel p-4 text-foreground shadow-xl backdrop:bg-black/70 sm:p-6"
    >
      <div className="mb-5 flex items-start justify-between gap-4">
        <h2
          ref={headingRef}
          id={titleId}
          tabIndex={-1}
          className="text-xl font-semibold tracking-tight focus:outline-none"
        >
          {finished ? "Privacy check complete" : "Privacy check"}
        </h2>

        <button
          type="button"
          onClick={onClose}
          aria-label="Close privacy check"
          className="flex size-8 shrink-0 items-center justify-center rounded-full border border-white/10 text-muted transition-colors hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <span aria-hidden="true">×</span>
        </button>
      </div>

      {step === -1 && (
        <div className="space-y-5">
          <p className="text-sm leading-relaxed text-muted">
            Before your first comparison, explore four short groups of
            privacy facts. Select every orange chunk showing data we
            collect. After each group, you will have five seconds to read
            the remaining facts.
          </p>

          <ul className="grid gap-3 sm:grid-cols-2">
            {COLORS.map((color) => (
              <li
                key={color}
                className={`rounded-xl p-4 text-sm font-medium ${CHUNK_STYLES[color].classes}`}
              >
                <span className="mb-1 block capitalize">{color}</span>
                {CHUNK_STYLES[color].meaning}
              </li>
            ))}
          </ul>

          <button type="button" onClick={advance} className={BUTTON_CLASS}>
            Start
          </button>
        </div>
      )}

      {screen && (
        <div className="space-y-3">
          <p className="text-sm text-muted">
            {formatNumber(step + 1)} of {formatNumber(PRIVCAP_SCREENS.length)}
          </p>
          <ChunkGrid
            key={screen.category}
            screen={screen}
            onComplete={advance}
          />
        </div>
      )}

      {finished && (
        <div className="space-y-5">
          <p className="text-sm leading-relaxed text-muted">
            You have explored the key privacy facts. Continue to finish
            and let this browser remember the current policy version.
          </p>
          <button type="button" onClick={finish} className={BUTTON_CLASS}>
            Continue
          </button>
        </div>
      )}

      <div className="mt-6 border-t border-white/10 pt-4">
        <a
          href="/privacy"
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-accent underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Read the full policy
          <span className="sr-only"> (opens in a new tab)</span>
        </a>
      </div>
    </dialog>
  );
}