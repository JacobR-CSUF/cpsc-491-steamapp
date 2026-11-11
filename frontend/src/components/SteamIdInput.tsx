"use client";

import { useId } from "react";
import { isValidSteamId } from "@/lib/steamId";

interface SteamIdInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

export default function SteamIdInput({
  label,
  value,
  onChange,
  error,
}: SteamIdInputProps) {
  const id = useId();
  const invalid = value.trim() !== "" && !isValidSteamId(value.trim());
  const message = error || (invalid ? "Enter a 17-digit SteamID64." : "");

  return (
    <div className="w-full">
      <label htmlFor={id} className="mb-2 block text-sm text-muted">
        {label}
      </label>
      <input
        id={id}
        type="text"
        inputMode="numeric"
        autoComplete="off"
        spellCheck={false}
        placeholder="76561198000000000"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        aria-invalid={Boolean(message) || undefined}
        aria-describedby={message ? `${id}-error` : undefined}
        className="w-full rounded-xl border border-white/10 bg-panel px-4 py-3 text-base text-foreground outline-none transition-colors placeholder:text-muted/60 focus:border-accent/60 focus:ring-2 focus:ring-accent/30 aria-invalid:border-red-400/60"
      />
      {message && (
        <p
          id={`${id}-error`}
          role="alert"
          className="mt-2 text-sm text-red-400"
        >
          {message}
        </p>
      )}
    </div>
  );
}