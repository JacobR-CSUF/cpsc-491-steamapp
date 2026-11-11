"use client";

import { useState } from "react";
import PrivCaptcha from "@/components/privacy/PrivCaptcha";

export default function PrivacyCheckButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="action-button rounded-full border border-white/10 px-4 py-2 text-sm text-accent transition-colors hover:border-accent/60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        Try the interactive version
      </button>

      {open && (
        <PrivCaptcha
          onComplete={() => setOpen(false)}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}