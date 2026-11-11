"use client";

import { useState, type ImgHTMLAttributes } from "react";

type SafeImageProps = Omit<ImgHTMLAttributes<HTMLImageElement>, "src" | "alt"> & {
  src?: string | null;
  alt: string;
};

export default function SafeImage({ src, alt, className = "", width, height, onError, ...props }: SafeImageProps) {
  const [failedSource, setFailedSource] = useState<string | null>(null);

  if (!src || failedSource === src) {
    return (
      <span
        role={alt ? "img" : undefined}
        aria-label={alt || undefined}
        aria-hidden={alt ? undefined : true}
        className={"inline-flex items-center justify-center bg-background text-muted " + className}
        style={{ width, height, ...props.style }}
      >
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="h-1/2 w-1/2">
          <rect x="3" y="3" width="18" height="18" rx="4" />
          <circle cx="9" cy="9" r="2" />
          <path d="m4 18 5-5 4 4 3-3 4 4" />
        </svg>
      </span>
    );
  }

  return (
    // Remote Steam images retain their original dimensions and loading behavior.
    // eslint-disable-next-line @next/next/no-img-element
    <img
      {...props}
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      onError={(event) => {
        setFailedSource(src);
        onError?.(event);
      }}
    />
  );
}
