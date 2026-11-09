"use client";

import { useState } from "react";
import { ApiError, getSuggestions } from "@/lib/api";

interface AiSuggestionBoxProps {
  steamId: string;
  appId: number;
  name: string;
}

type Tips =
  | { status: "loading" }
  | { status: "ready"; text: string }
  | { status: "error"; message: string };

// Gemini often answers in Markdown: drop ** markers and turn "* " / "- " list
// lines into "• " bullets so the text reads cleanly as plain text.
export function cleanTips(text: string): string {
  return text
    .replace(/\*\*/g, "")
    .split("\n")
    .map((line) => line.replace(/^(\s*)[*-]\s+/, "$1• "))
    .join("\n")
    .trim();
}

export default function AiSuggestionBox({ steamId, appId, name }: AiSuggestionBoxProps) {
  const key = `${steamId}:${appId}`;
  const [tips, setTips] = useState<{ key: string; tips: Tips } | null>(null);

  // Tips belong to one game: a different appId shows nothing until clicked again.
  const current = tips?.key === key ? tips.tips : null;
  const loading = current?.status === "loading";

  // Load only on click, never automatically, so browsing games doesn't spend Gemini credits.
  function requestTips() {
    setTips({ key, tips: { status: "loading" } });
    getSuggestions(steamId, appId)
      .then((result) => {
        setTips((prev) =>
          prev?.key === key
            ? { key, tips: { status: "ready", text: cleanTips(result.suggestions) } }
            : prev,
        );
      })
      .catch((error) => {
        const message =
          error instanceof ApiError && error.status === 503
            ? "AI tips aren’t set up on this server."
            : "Couldn’t get tips right now. Try again.";
        setTips((prev) =>
          prev?.key === key ? { key, tips: { status: "error", message } } : prev,
        );
      });
  }

  return (
    <div className="space-y-4 rounded-xl bg-background/40 p-5 ring-1 ring-white/10">
      <div className="flex items-center justify-between gap-4">
        <h4 className="font-semibold tracking-tight">Tips for {name}</h4>
        <button
          type="button"
          onClick={requestTips}
          disabled={loading}
          className="rounded-full bg-accent px-4 py-1.5 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          Get tips
        </button>
      </div>

      {current?.status === "loading" && (
        <p className="text-sm text-muted" role="status">
          Generating tips…
        </p>
      )}
      {current?.status === "error" && (
        <p className="text-sm text-muted" role="alert">
          {current.message}
        </p>
      )}
      {current?.status === "ready" && (
        <p className="text-sm leading-relaxed whitespace-pre-line text-foreground">
          {current.text}
        </p>
      )}
    </div>
  );
}
