import { useEffect, useId, useRef, useState } from "react";
import type { ReactNode } from "react";
import StatusMessage from "@/components/compare/StatusMessage";
import { ApiError, getGameDetail } from "@/lib/api";
import PlaytimeGraph from "@/components/library/PlaytimeGraph";
import ScreenshotGallery from "@/components/library/ScreenshotGallery";
import { formatDate, formatHours } from "@/lib/format";
import type { GameDetail } from "@/lib/types";


/*
GameDetailModal component is responsible for displaying detailed information about a selected game.
  It fetches the game details from the Steam API and displays them in a modal dialog.
  The modal includes information such as total playtime, last played date, achievements, and more.
  It handles loading states, error states, and provides accessibility features like focus management and keyboard navigation.
*/

interface GameDetailModalProps {
  steamId: string;
  appId: number;
  onClose: () => void;
}

type Result =
  | { status: "ready"; detail: GameDetail }
  | { status: "error"; title: string; message: string };

function describeError(error: unknown): Result {
  if (error instanceof ApiError && (error.status === 403 || error.status === 404)) {
    return { status: "error", title: "Game details unavailable", message: error.detail };
  }
  return {
    status: "error",
    title: "Steam unavailable",
    message: "Steam could not be reached. Try again.",
  };
}

// Steam only sends the exact date for the API key owner's own account.
function lastPlayedText(detail: GameDetail): string {
  if (detail.last_played_at) return formatDate(detail.last_played_at);
  return detail.played_recently ? "In the last 2 weeks" : "More than 2 weeks ago";
}

function Stat({
  label,
  className,
  children,
}: {
  label: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={className}>
      <dt className="text-xs uppercase tracking-wide text-muted">{label}</dt>
      <dd className="mt-1 text-foreground">{children}</dd>
    </div>
  );
}

function Details({ detail }: { detail: GameDetail }) {
  const { achievements_unlocked: unlocked, achievements_total: total } = detail;
  const percent = total > 0 ? Math.round((unlocked / total) * 100) : 0;
  const last = detail.last_achievement;

  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-5 text-lg">
      <Stat label="Total playtime">
        <span className="font-semibold text-accent">{formatHours(detail.playtime_minutes)}</span>
      </Stat>
      <Stat label="Last 2 weeks">{formatHours(detail.recent_playtime_minutes)}</Stat>
      <Stat label="Last played" className="col-span-2">
        {lastPlayedText(detail)}
      </Stat>
      <Stat label="Achievements" className="col-span-2">
        {total > 0 ? (
          <>
            {unlocked} of {total}
            <span className="ml-2 text-sm text-muted">{percent}%</span>
            <div
              role="progressbar"
              aria-label="Achievement progress"
              aria-valuemin={0}
              aria-valuemax={total}
              aria-valuenow={unlocked}
              className="mt-2 h-2 overflow-hidden rounded-full bg-background"
            >
              <div className="h-full rounded-full bg-accent" style={{ width: `${percent}%` }} />
            </div>
          </>
        ) : (
          <span className="text-muted">This game has no achievements</span>
        )}
      </Stat>
      <Stat label="Last achievement" className="col-span-2">
        {last ? (
          <>
            {last.display_name}
            {last.unlocked_at && (
              <span className="block text-sm text-muted">{formatDate(last.unlocked_at)}</span>
            )}
          </>
        ) : (
          <span className="text-muted">None yet</span>
        )}
      </Stat>
    </dl>
  );
}

export default function GameDetailModal({ steamId, appId, onClose }: GameDetailModalProps) {
  const titleId = useId();
  const screenshotsId = useId();
  const panelRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const onCloseRef = useRef(onClose);

  const key = `${steamId}:${appId}`;
  const [loaded, setLoaded] = useState<{ key: string; result: Result } | null>(null);

  // Always call the latest onClose without re-running the focus effect below.
  useEffect(() => {
    onCloseRef.current = onClose;
  });

  useEffect(() => {
    let active = true;
    getGameDetail(steamId, appId)
      .then((detail) => {
        if (active) setLoaded({ key, result: { status: "ready", detail } });
      })
      .catch((error) => {
        if (active) setLoaded({ key, result: describeError(error) });
      });

    return () => {
      active = false;
    };
  }, [steamId, appId, key]);

  // Focus the close button, keep Tab inside the dialog, close on Escape,
  // lock page scroll, and hand focus back to the clicked tile on close.
  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        // Something inside the dialog (the screenshot viewer) already handled it.
        if (event.defaultPrevented) return;
        onCloseRef.current();
        return;
      }
      if (event.key !== "Tab" || !panelRef.current) return;

      const focusable = panelRef.current.querySelectorAll<HTMLElement>(
        "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])",
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
      previouslyFocused?.focus();
    };
  }, []);

  const result = loaded?.key === key ? loaded.result : null;
  const detail = result?.status === "ready" ? result.detail : null;

  let content;
  if (result === null) {
    content = (
      <StatusMessage
        title="Loading game details..."
        message="This can take a moment if Steam is slow."
      />
    );
  } else if (result.status === "error") {
    content = <StatusMessage title={result.title} message={result.message} />;
  } else {
    content = (
      <div className="space-y-8">
        <Details detail={result.detail} />
        <PlaytimeGraph key={key} steamId={steamId} appId={appId} />
        <section aria-labelledby={screenshotsId}>
          <h3 id={screenshotsId} className="mb-3 text-xs uppercase tracking-wide text-muted">
            Screenshots
          </h3>
          <ScreenshotGallery screenshots={result.detail.screenshots} />
        </section>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div aria-hidden="true" onClick={onClose} className="absolute inset-0 bg-black/70" />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-panel p-6 ring-1 ring-white/10"
      >
        <div className="mb-6 flex items-center gap-3">
          {detail &&
            (detail.icon_url ? (
              // Steam icons are small remote images, so a plain <img> is enough.
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={detail.icon_url}
                alt=""
                width={40}
                height={40}
                className="size-10 shrink-0 rounded"
              />
            ) : (
              <span
                aria-hidden="true"
                className="flex size-10 shrink-0 items-center justify-center rounded bg-background text-sm text-muted"
              >
                {detail.name.charAt(0).toUpperCase()}
              </span>
            ))}
          <h2 id={titleId} className="min-w-0 flex-1 text-xl font-semibold tracking-tight">
            {detail ? detail.name : "Game details"}
          </h2>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex size-8 shrink-0 items-center justify-center rounded-full text-muted ring-1 ring-white/10 transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
              <path d="M3 3l10 10M13 3L3 13" />
            </svg>
          </button>
        </div>
        {content}
      </div>
    </div>
  );
}
