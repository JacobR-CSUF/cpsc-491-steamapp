"use client";

import { useId } from "react";
import { isValidSteamId } from "@/lib/steamId";

interface SteamIdInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export default function SteamIdInput({ label, value, onChange }: SteamIdInputProps) {
  const id = useId();
  const invalid = value.trim() !== "" && !isValidSteamId(value);

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
        aria-invalid={invalid || undefined}
        aria-describedby={invalid ? `${id}-error` : undefined}
        className="w-full rounded-xl border border-white/10 bg-panel px-4 py-3 text-base text-foreground outline-none transition-colors placeholder:text-muted/60 focus:border-accent/60 focus:ring-2 focus:ring-accent/30 aria-invalid:border-red-400/60"
      />
      {invalid && (
        <p id={`${id}-error`} className="mt-2 text-sm text-red-400">
          Enter a 17-digit SteamID64.
        </p>
      )}
    </div>
  );
}
