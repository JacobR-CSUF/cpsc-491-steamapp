import { useEffect, useMemo, useRef, useState } from "react";
import GameDetailModal from "@/components/library/GameDetailModal";
import GameTile from "@/components/library/GameTile";
import { ApiError, getLibrary, getPlayer } from "@/lib/api";
import type { OwnedGame } from "@/lib/types";

/*
LibrarySection component is responsible for displaying the libraries of two players.
Allows users to switch between the two players libraries, search for games, and select a game to view its details.
The component handles loading states, error states, and displays the games in a grid layout.
*/

const INITIAL_COUNT = 60;

interface LibrarySectionProps {
  steamIdA: string;
  steamIdB: string;
}

type Side = "a" | "b";

type LibraryState =
  | { status: "ready"; games: OwnedGame[] }
  | { status: "error"; message: string };

function describeError(error: unknown): string {
  if (error instanceof ApiError && (error.status === 403 || error.status === 404)) {
    return error.detail;
  }
  return "Steam could not be reached. Try again.";
}

export default function LibrarySection({ steamIdA, steamIdB }: LibrarySectionProps) {
  const [side, setSide] = useState<Side>("a");
  const [names, setNames] = useState<Record<string, string>>({});
  const [libraries, setLibraries] = useState<Record<string, LibraryState>>({});
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const [shown, setShown] = useState(INITIAL_COUNT);
  // The game the user clicked. Its details open in GameDetailModal.
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  // Libraries already requested, so switching tabs doesn't fetch them again.
  const requested = useRef(new Set<string>());

  const selectedId = side === "a" ? steamIdA : steamIdB;

  // Tab labels use the players' names.
  useEffect(() => {
    let active = true;
    for (const id of [steamIdA, steamIdB]) {
      getPlayer(id)
        .then((player) => {
          if (active) setNames((prev) => ({ ...prev, [id]: player.persona_name }));
        })
        .catch(() => {
          // The tab keeps its fallback label.
        });
    }
    return () => {
      active = false;
    };
  }, [steamIdA, steamIdB]);

  // Load the selected player's library once.
  useEffect(() => {
    if (requested.current.has(selectedId)) return;
    requested.current.add(selectedId);

    getLibrary(selectedId)
      .then((games) => {
        setLibraries((prev) => ({ ...prev, [selectedId]: { status: "ready", games } }));
      })
      .catch((error) => {
        setLibraries((prev) => ({
          ...prev,
          [selectedId]: { status: "error", message: describeError(error) },
        }));
      });
  }, [selectedId, attempt]);

  const library = libraries[selectedId];
  const games = library?.status === "ready" ? library.games : null;

  const filtered = useMemo(() => {
    if (!games) return [];
    const needle = query.trim().toLowerCase();
    return needle ? games.filter((game) => game.name.toLowerCase().includes(needle)) : games;
  }, [games, query]);

  const visible = filtered.slice(0, shown);
  const remaining = filtered.length - visible.length;

  // Close the modal and put focus back on the tile that opened it, without
  // scrolling, so the library stays exactly where the user left it.
  function closeModal() {
    const appId = selectedAppId;
    setSelectedAppId(null);
    if (appId === null) return;
    requestAnimationFrame(() => {
      panelRef.current
        ?.querySelector<HTMLElement>(`[data-app-id="${appId}"]`)
        ?.focus({ preventScroll: true });
    });
  }

  function selectSide(next: Side) {
    // The open game belongs to the player who was showing, so close it.
    setSelectedAppId(null);
    setSide(next);
    setShown(INITIAL_COUNT);
  }

  function changeQuery(value: string) {
    setQuery(value);
    setShown(INITIAL_COUNT);
  }

  function retry() {
    requested.current.delete(selectedId);
    setLibraries((prev) => {
      const next = { ...prev };
      delete next[selectedId];
      return next;
    });
    setAttempt((count) => count + 1);
  }

  const tabs = [
    { side: "a", id: steamIdA, fallback: "Player A" },
    { side: "b", id: steamIdB, fallback: "Player B" },
  ] as const;

  let body;
  if (library === undefined) {
    body = (
      <p className="text-sm text-muted">
        Loading library... The first load of a large library can take a minute.
      </p>
    );
  } else if (library.status === "error") {
    body = (
      <div className="flex flex-wrap items-center gap-4 text-sm">
        <p className="text-muted">{library.message}</p>
        <button
          type="button"
          onClick={retry}
          className="rounded-full border border-white/10 px-4 py-1.5 text-muted transition-colors hover:border-white/20 hover:text-foreground"
        >
          Try again
        </button>
      </div>
    );
  } else if (library.games.length === 0) {
    body = <p className="text-sm text-muted">This library is empty.</p>;
  } else {
    body = (
      <div className="space-y-4">
        <p className="text-sm text-muted" aria-live="polite">
          Showing {visible.length} of {filtered.length} games
        </p>
        {filtered.length === 0 ? (
          <p className="text-sm text-muted">No games match your search.</p>
        ) : (
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {visible.map((game) => (
              <li key={game.app_id}>
                <GameTile
                  game={game}
                  onSelect={setSelectedAppId}
                  selected={game.app_id === selectedAppId}
                />
              </li>
            ))}
          </ul>
        )}
        {remaining > 0 && (
          <button
            type="button"
            onClick={() => setShown(filtered.length)}
            className="rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground"
          >
            Show more ({remaining} more)
          </button>
        )}
      </div>
    );
  }

  return (
    <section aria-labelledby="library-title">
      <h2 id="library-title" className="mb-3 text-xl font-semibold tracking-tight">
        Libraries
      </h2>
      <div className="space-y-6 rounded-2xl bg-panel p-6 ring-1 ring-white/10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div role="tablist" aria-label="Player libraries" className="flex gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.side}
                type="button"
                role="tab"
                id={`library-tab-${tab.side}`}
                aria-selected={side === tab.side}
                aria-controls="library-panel"
                onClick={() => selectSide(tab.side)}
                className={`rounded-full px-4 py-1.5 text-sm ring-1 transition-colors ${
                  side === tab.side
                    ? "bg-accent/15 text-accent ring-accent/40"
                    : "text-muted ring-white/10 hover:text-foreground"
                }`}
              >
                {names[tab.id] ?? tab.fallback}
              </button>
            ))}
          </div>
          <div className="w-full sm:w-64">
            <label htmlFor="library-search" className="sr-only">
              Search games
            </label>
            <input
              id="library-search"
              type="search"
              value={query}
              onChange={(event) => changeQuery(event.target.value)}
              placeholder="Search games"
              className="w-full rounded-full bg-background px-4 py-1.5 text-sm text-foreground ring-1 ring-white/10 placeholder:text-muted focus:outline-none focus:ring-accent"
            />
          </div>
        </div>
        <div
          ref={panelRef}
          role="tabpanel"
          id="library-panel"
          aria-labelledby={`library-tab-${side}`}
        >
          {body}
        </div>
      </div>
      {selectedAppId !== null && (
        <GameDetailModal
          steamId={selectedId}
          appId={selectedAppId}
          onClose={closeModal}
        />
      )}
    </section>
  );
}
