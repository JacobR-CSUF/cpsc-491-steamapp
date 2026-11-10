import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";

/*
This component is a gallery of screenshots for a game.
  It has two modes: a grid of thumbnails, and a larger view of one screenshot at a time.
  The larger view takes focus so that the arrow keys can be used to navigate between screenshots,
  and Escape closes the larger view and returns focus to the thumbnail that was open.
*/

interface ScreenshotGalleryProps {
  screenshots: string[];
}

interface ViewerProps {
  screenshots: string[];
  index: number;
  onChange: (index: number) => void;
  onClose: () => void;
}

const BUTTON_CLASS =
  "rounded-full border border-white/10 px-4 py-1.5 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:pointer-events-none disabled:opacity-40";

// The larger view. It takes focus when it opens so the arrow keys work right away.
function Viewer({ screenshots, index, onChange, onClose }: ViewerProps) {
  const ref = useRef<HTMLDivElement>(null);
  const count = screenshots.length;

  useEffect(() => {
    ref.current?.focus();
  }, []);

  function previous() {
    onChange((index - 1 + count) % count);
  }

  function next() {
    onChange((index + 1) % count);
  }

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      // Go back to the thumbnails without also closing the game modal.
      // The modal listens on document, so mark the event as handled.
      event.preventDefault();
      event.stopPropagation();
      event.nativeEvent.stopImmediatePropagation();
      onClose();
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      previous();
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      next();
    }
  }

  return (
    <div
      ref={ref}
      tabIndex={-1}
      role="group"
      aria-label="Screenshot viewer"
      onKeyDown={onKeyDown}
      className="space-y-3 outline-none"
    >
      <div className="rounded-xl bg-background ring-1 ring-white/10">
        {/* Steam screenshots are remote images, so a plain <img> is enough. */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={screenshots[index]}
          alt={`Screenshot ${index + 1} of ${count}`}
          className="max-h-[55vh] w-full rounded-xl object-contain"
        />
      </div>
      <div className="flex items-center justify-between gap-3">
        <button type="button" onClick={previous} disabled={count < 2} className={BUTTON_CLASS}>
          Previous
        </button>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-muted" aria-live="polite">
            {index + 1} of {count}
          </span>
          <button type="button" onClick={onClose} className={BUTTON_CLASS}>
            Back to thumbnails
          </button>
        </div>
        <button type="button" onClick={next} disabled={count < 2} className={BUTTON_CLASS}>
          Next
        </button>
      </div>
    </div>
  );
}

export default function ScreenshotGallery({ screenshots }: ScreenshotGalleryProps) {
  const [index, setIndex] = useState<number | null>(null);
  const thumbnails = useRef<(HTMLButtonElement | null)[]>([]);

  if (screenshots.length === 0) {
    return <p className="text-sm text-muted">No public screenshots</p>;
  }

  function closeViewer() {
    const current = index;
    setIndex(null);
    // Hand focus back to the thumbnail that was open.
    if (current !== null) {
      requestAnimationFrame(() => thumbnails.current[current]?.focus());
    }
  }

  if (index !== null && index < screenshots.length) {
    return (
      <Viewer
        screenshots={screenshots}
        index={index}
        onChange={setIndex}
        onClose={closeViewer}
      />
    );
  }

  return (
    <ul className="grid grid-cols-2 gap-2 sm:grid-cols-3">
      {screenshots.map((url, i) => (
        <li key={url}>
          <button
            type="button"
            ref={(element) => {
              thumbnails.current[i] = element;
            }}
            onClick={() => setIndex(i)}
            aria-label={`Open screenshot ${i + 1} of ${screenshots.length}`}
            className="block w-full overflow-hidden rounded-lg bg-background ring-1 ring-white/10 transition-shadow hover:ring-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={url}
              alt=""
              loading="lazy"
              className="aspect-video w-full object-cover"
            />
          </button>
        </li>
      ))}
    </ul>
  );
}
