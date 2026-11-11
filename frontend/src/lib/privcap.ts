export type ChunkColor = "orange" | "teal" | "yellow" | "pink";

export const CHUNK_STYLES = {
  orange: {
    meaning: "Data we collect",
    classes: "bg-orange-600 text-white",
    selectedClasses: "bg-white text-orange-600",
  },
  teal: {
    meaning: "Who sees or receives it",
    classes: "bg-teal-600 text-white",
    selectedClasses: "bg-white text-teal-600",
  },
  yellow: {
    meaning: "How it’s sent or kept",
    classes: "bg-yellow-400 text-background",
    selectedClasses: "bg-white text-yellow-600",
  },
  pink: {
    meaning: "What it’s used for",
    classes: "bg-pink-300 text-background",
    selectedClasses: "bg-white text-pink-600",
  },
} satisfies Record<
  ChunkColor,
  {
    meaning: string;
    classes: string;
    selectedClasses: string;
  }
>;

export interface Chunk {
  id: string;
  text: string;
  color: ChunkColor;
}

export interface PrivCapScreen {
  category: string;
  chunks: Chunk[];
}

export const PRIVCAP_SCREENS: PrivCapScreen[] = [
  {
    category: "Steam profile",
    chunks: [
      { id: "profile-id", text: "SteamID64", color: "orange" },
      {
        id: "profile-https",
        text: "Looked up over HTTPS",
        color: "yellow",
      },
      { id: "profile-steam", text: "Steam Web API", color: "teal" },
      { id: "profile-name", text: "Display name", color: "orange" },
      { id: "profile-avatar", text: "Avatar", color: "orange" },
      { id: "profile-link", text: "Profile link", color: "orange" },
      {
        id: "profile-visibility",
        text: "Profile visibility",
        color: "orange",
      },
      {
        id: "profile-storage",
        text: "Saved in the app's database",
        color: "yellow",
      },
      {
        id: "profile-viewers",
        text: "Anyone using this app",
        color: "teal",
      },
      {
        id: "profile-purpose",
        text: "Side-by-side comparison",
        color: "pink",
      },
    ],
  },
  {
    category: "Game library",
    chunks: [
      { id: "library-games", text: "Owned games", color: "orange" },
      {
        id: "library-storage",
        text: "Library saved in the database",
        color: "yellow",
      },
      { id: "library-steam", text: "Steam Web API", color: "teal" },
      {
        id: "library-total",
        text: "Total playtime",
        color: "orange",
      },
      {
        id: "library-recent",
        text: "Recent playtime",
        color: "orange",
      },
      {
        id: "library-last-played",
        text: "Last-played dates",
        color: "orange",
      },
      {
        id: "library-screenshots",
        text: "Screenshot links",
        color: "orange",
      },
      {
        id: "library-screenshot-storage",
        text: "Screenshot links cached for 1 hour; images stay on Steam",
        color: "yellow",
      },
      {
        id: "library-viewers",
        text: "Anyone using this app",
        color: "teal",
      },
      {
        id: "library-comparison",
        text: "Library comparison",
        color: "pink",
      },
      {
        id: "library-value",
        text: "Account value estimate",
        color: "pink",
      },
    ],
  },
  {
    category: "Achievements",
    chunks: [
      {
        id: "achievements-unlocked",
        text: "Unlocked achievements",
        color: "orange",
      },
      {
        id: "achievements-dates",
        text: "Unlock dates",
        color: "orange",
      },
      {
        id: "achievements-storage",
        text: "Saved in the app's database",
        color: "yellow",
      },
      {
        id: "achievements-steam",
        text: "Steam Web API",
        color: "teal",
      },
      {
        id: "achievements-locked",
        text: "Locked achievements",
        color: "orange",
      },
      {
        id: "achievements-google",
        text: "Google Gemini",
        color: "teal",
      },
      {
        id: "achievements-click",
        text: "Gemini only when you click Get tips",
        color: "yellow",
      },
      {
        id: "achievements-no-id",
        text: "SteamID64 never sent to Gemini",
        color: "yellow",
      },
      {
        id: "achievements-viewers",
        text: "Anyone using this app",
        color: "teal",
      },
      {
        id: "achievements-charts",
        text: "Comparison charts",
        color: "pink",
      },
      {
        id: "achievements-tips",
        text: "AI tips",
        color: "pink",
      },
    ],
  },
  {
    category: "Comparison history",
    chunks: [
      {
        id: "history-players",
        text: "Who you compared",
        color: "orange",
      },
      {
        id: "history-time",
        text: "When you compared",
        color: "orange",
      },
      {
        id: "history-storage",
        text: "Saved in the app's database",
        color: "yellow",
      },
      {
        id: "history-retention",
        text: "Kept until removed or the database resets",
        color: "yellow",
      },
      {
        id: "history-viewers",
        text: "Anyone using this app",
        color: "teal",
      },
      {
        id: "history-page",
        text: "History page",
        color: "pink",
      },
      {
        id: "history-opponents",
        text: "Recent opponents",
        color: "pink",
      },
    ],
  },
];

export const PRIVCAP_VERSION = 1;

const STORAGE_KEY = "privcap-version";

export function hasCompletedPrivCap(): boolean {
  try {
    return (
      window.localStorage.getItem(STORAGE_KEY) === String(PRIVCAP_VERSION)
    );
  } catch {
    return false;
  }
}

export function markPrivCapComplete(): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, String(PRIVCAP_VERSION));
  } catch {
    // The current comparison can continue even when storage is blocked.
  }
}