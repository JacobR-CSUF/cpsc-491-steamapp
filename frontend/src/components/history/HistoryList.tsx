"use client";

import Link from "next/link";
import { useEffect, useId, useState } from "react";
import { getComparisons } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import { formatDate } from "@/lib/format";
import { isValidSteamId } from "@/lib/steamId";
import type { ComparisonRecord, Player } from "@/lib/types";

const LIMIT = 20;

type Result =
  | { status: "ready"; records: ComparisonRecord[] }
  | { status: "error"; message: string };

function Avatar({ player }: { player: Player }) {
  return (
    <span className="h-8 w-8 shrink-0 overflow-hidden rounded-full bg-white/10 ring-1 ring-white/10">
      {player.avatar_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={player.avatar_url}
          alt=""
          width={32}
          height={32}
          className="h-full w-full object-cover"
        />
      )}
    </span>
  );
}

export default function HistoryList() {
  const inputId = useId();
  const [filter, setFilter] = useState("");
  const trimmed = filter.trim();
  const steamId = isValidSteamId(trimmed) ? trimmed : undefined;
  const key = steamId ?? "";

  const [loaded, setLoaded] = useState<{ key: string; result: Result } | null>(null);

  useEffect(() => {
    let active = true;
    getComparisons(steamId, LIMIT)
      .then((records) => {
        if (active) setLoaded({ key, result: { status: "ready", records } });
      })
      .catch((error) => {
        if (active) setLoaded({ key, result: { status: "error", message: errorMessage(error) } });
      });

    return () => {
      active = false;
    };
  }, [key, steamId]);

  const result = loaded?.key === key ? loaded.result : null;

  let content;
  if (result === null) {
    content = <p className="text-sm text-muted">Loading history…</p>;
  } else if (result.status === "error") {
    content = <p role="alert" className="text-sm text-muted">{result.message}</p>;
  } else if (result.records.length === 0) {
    content = <p className="text-sm text-muted">No comparisons yet.</p>;
  } else {
    content = (
      <ul className="divide-y divide-white/10 rounded-2xl bg-panel ring-1 ring-white/10">
        {result.records.map((record) => (
          <li
            key={record.id}
            className="flex flex-wrap items-center gap-x-6 gap-y-3 px-5 py-4"
          >
            <div className="flex min-w-0 flex-1 items-center gap-3">
              <div className="flex -space-x-2">
                <Avatar player={record.player_a} />
                <Avatar player={record.player_b} />
              </div>
              <p className="truncate">
                <span className="font-medium">{record.player_a.persona_name}</span>
                <span className="text-muted"> vs </span>
                <span className="font-medium">{record.player_b.persona_name}</span>
              </p>
            </div>
            <time dateTime={record.compared_at} className="text-sm text-muted">
              {formatDate(record.compared_at)}
            </time>
            <Link
              href={`/compare?a=${record.player_a.steam_id}&b=${record.player_b.steam_id}`}
              className="rounded-full border border-white/10 px-3.5 py-1.5 text-sm text-foreground transition-colors hover:border-accent/60"
            >
              View
            </Link>
          </li>
        ))}
      </ul>
    );
  }

  return (
    <div className="space-y-6">
      <div className="max-w-sm">
        <label htmlFor={inputId} className="mb-2 block text-sm text-muted">
          Filter by SteamID64
        </label>
        <input
          id={inputId}
          type="text"
          inputMode="numeric"
          autoComplete="off"
          spellCheck={false}
          placeholder="76561198000000000"
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          className="w-full rounded-xl border border-white/10 bg-panel px-4 py-2.5 text-base text-foreground outline-none transition-colors placeholder:text-muted/60 focus:border-accent/60 focus:ring-2 focus:ring-accent/30"
        />
      </div>
      {content}
    </div>
  );
}
