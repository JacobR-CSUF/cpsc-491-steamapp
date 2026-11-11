import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
};

export default function PrivacyPage() {
  return (
    <article className="mx-auto max-w-3xl space-y-8">
      <header className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">
          Privacy Policy
        </h1>
        <p className="text-sm text-muted">
          Last updated: <time dateTime="2026-11-10">November 10, 2026</time>
        </p>
        <p className="leading-relaxed text-muted">
          Steam-User Showdown is a CPSC 491 student project at Cal State
          Fullerton. It runs on the team’s own computers. This policy explains
          what this copy of the app reads, stores, and sends.
        </p>
      </header>

      <section aria-labelledby="collect-heading" className="space-y-3">
        <h2 id="collect-heading" className="text-xl font-semibold">
          What we collect
        </h2>
        <p className="leading-relaxed text-muted">
          For each SteamID64 entered, the app can retrieve the following
          information when it is available publicly:
        </p>
        <ul className="list-disc space-y-2 pl-6 leading-relaxed text-muted">
          <li>
            Public profile: SteamID64, display name, avatar, profile link,
            and whether the profile is public.
          </li>
          <li>
            Game library: owned games, game names and icons, total playtime,
            playtime from the last two weeks, and last-played dates.
          </li>
          <li>
            Achievements: achievement names, descriptions and icons, which
            achievements are unlocked or locked, unlock dates, and public
            global unlock percentages.
          </li>
          <li>
            Screenshots: links to public screenshots for games someone opens.
          </li>
          <li>
            Comparison history: the two SteamID64s in each successful
            comparison and when the comparison happened.
          </li>
        </ul>
      </section>

      <section aria-labelledby="use-heading" className="space-y-3">
        <h2 id="use-heading" className="text-xl font-semibold">
          How we use it
        </h2>
        <ul className="list-disc space-y-2 pl-6 leading-relaxed text-muted">
          <li>Show side-by-side comparisons, statistics, and charts.</li>
          <li>Estimate account value using US Steam store prices.</li>
          <li>Show comparison history and recent opponents.</li>
          <li>Provide AI achievement tips when someone asks for them.</li>
        </ul>
      </section>

      <section aria-labelledby="source-heading" className="space-y-3">
        <h2 id="source-heading" className="text-xl font-semibold">
          Where it comes from
        </h2>
        <p className="leading-relaxed text-muted">
          We read publicly available information through the Steam Web API,
          Steam store price service, and public Steam screenshot pages. We
          also record comparisons made in this app.
        </p>
        <p className="leading-relaxed text-muted">
          You do not sign in to Steam through this app. We do not ask for
          Steam passwords or payment details. Profiles that Steam reports
          as private cannot be compared. Comparisons also require public
          game details and visible playtime.
        </p>
      </section>

      <section aria-labelledby="sharing-heading" className="space-y-3">
        <h2 id="sharing-heading" className="text-xl font-semibold">
          Who sees or receives it
        </h2>
        <ul className="list-disc space-y-2 pl-6 leading-relaxed text-muted">
          <li>
            <strong className="text-foreground">Valve:</strong> when we request
            player information from Steam, we send the SteamID64 being
            looked up. Game-specific requests can also include the game’s
            ID. Cached results can be reused without making a new request.
            Screenshot requests may use public Steam Community pages.
          </li>
          <li>
            <strong className="text-foreground">Google:</strong> when someone
            clicks Get tips and a new AI response is needed, Gemini receives
            the game’s name and up to 10 locked achievements, including their
            names, descriptions, and how common they are. We do not include
            SteamID64s or profile details in the Gemini prompt.
          </li>
          <li>
            <strong className="text-foreground">
              People using this copy of the app:
            </strong>{" "}
            comparison history and recent opponents are shared, not private
            to one person. Other users can also view the Steam information
            displayed by the app.
          </li>
          <li>
            <strong className="text-foreground">The project team:</strong>{" "}
            the team runs this copy of the app and can access its stored data.
          </li>
        </ul>
      </section>

      <section aria-labelledby="retention-heading" className="space-y-3">
        <h2 id="retention-heading" className="text-xl font-semibold">
          How long we keep it
        </h2>
        <p className="leading-relaxed text-muted">
          Profiles, game libraries, achievements, and comparisons stay in
          the app’s database until the team removes them or resets the
          database. They do not automatically expire.
        </p>
        <ul className="list-disc space-y-2 pl-6 leading-relaxed text-muted">
          <li>Steam profile and library responses are cached for one hour.</li>
          <li>Player achievement responses are cached for 30 minutes.</li>
          <li>
            Game achievement definitions, global unlock percentages, store
            prices, and AI tips are cached for up to 24 hours.
          </li>
          <li>
            Screenshot links are cached for one hour. Screenshot images
            stay on Steam; the app does not save them in its database.
          </li>
        </ul>
        <p className="leading-relaxed text-muted">
          A cache is a temporary saved response that helps avoid repeated
          requests. Cache expiration does not delete information already
          saved in the app’s database.
        </p>
      </section>

      <section aria-labelledby="dont-heading" className="space-y-3">
        <h2 id="dont-heading" className="text-xl font-semibold">
          What we don’t do
        </h2>
        <p className="leading-relaxed text-muted">
          This app has no user accounts, ads, analytics, or tracking cookies.
          We do not sell your data or share it beyond the uses described
          above.
        </p>
      </section>

      <section aria-labelledby="choices-heading" className="space-y-3">
        <h2 id="choices-heading" className="text-xl font-semibold">
          Your choices
        </h2>
        <p className="leading-relaxed text-muted">
          Making your Steam profile or game details private limits what
          Steam returns in future requests. Steam may take time to apply
          changes, and this app may continue using cached responses until
          they expire. Changing your Steam settings does not remove data
          already stored in this app.
        </p>
        <p className="leading-relaxed text-muted">
          To request removal of stored data, contact the project team and
          identify the SteamID64 involved.
        </p>
      </section>

        <section aria-labelledby="contact-heading" className="space-y-3">
        <h2 id="contact-heading" className="text-xl font-semibold">
          Contact
        </h2>
        <p className="leading-relaxed text-muted">
          For questions or requests to remove stored data, contact any member
          of the Steam-User Showdown team: Jacob Rodas, Adrian Hernandez,
          AP Calderon, Matthew Estrada, or Alex Islas.
        </p>
        <p className="leading-relaxed text-muted">
          CPSC 491 — Cal State Fullerton.
        </p>
      </section>
    </article>
  );
}