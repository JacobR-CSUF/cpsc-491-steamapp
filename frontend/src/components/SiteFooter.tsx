import Link from "next/link";
import BackendStatus from "@/components/BackendStatus";

export default function SiteFooter() {
  return (
    <footer className="border-t border-white/10">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-8 text-sm text-muted md:flex-row md:items-end md:justify-between">
        <div className="space-y-4">
          <p>CPSC 491 · Cal State Fullerton</p>
          <div className="md:w-72">
            <BackendStatus />
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          <Link
            href="/privacy"
            className="transition-colors hover:text-foreground"
          >
            Privacy
          </Link>
          <a
            href="https://store.steampowered.com"
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            Powered by Steam
          </a>
        </div>
      </div>
    </footer>
  );
}