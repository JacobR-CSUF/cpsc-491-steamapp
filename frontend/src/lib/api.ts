import type {
  Achievement,
  AchievementTimeline,
  AdvancedStats,
  Comparison,
  ComparisonRecord,
  GameDetail,
  GameProgress,
  Opponent,
  OwnedGame,
  Player,
  PlayerStats,
  PlaytimeGraph,
  ProfileStatusInfo,
  Suggestions,
  TimelineDays,
} from "@/lib/types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type HealthStatus = Record<string, string>;

export async function getHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_URL}/api/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Backend unreachable");
  }

  return response.json();
}

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

type QueryParams = Record<string, string | number | undefined>;

async function readDetail(response: Response): Promise<string> {
  try {
    const body = await response.json();
    const detail = body?.detail;

    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail) && typeof detail[0]?.msg === "string") {
      return detail[0].msg;
    }
  } catch {
    // Body was not JSON.
  }

  return response.statusText || `Request failed with status ${response.status}`;
}

export async function apiGet<T>(path: string, params?: QueryParams): Promise<T> {
  const url = new URL(path, API_URL);

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new ApiError(response.status, await readDetail(response));
  }

  return response.json();
}

export function getPlayer(steamId: string) {
  return apiGet<Player>(`/api/players/${steamId}`);
}

export function getProfileStatus(steamId: string) {
  return apiGet<ProfileStatusInfo>(`/api/players/${steamId}/status`);
}

export function getPlayerStats(steamId: string) {
  return apiGet<PlayerStats>(`/api/players/${steamId}/stats`);
}

export function getLibrary(steamId: string) {
  return apiGet<OwnedGame[]>(`/api/players/${steamId}/games`);
}

export function getAchievementProgress(steamId: string) {
  return apiGet<GameProgress[]>(`/api/players/${steamId}/achievements`);
}

export function getAchievementTimeline(
  steamId: string,
  days: TimelineDays,
  appId?: number,
) {
  return apiGet<AchievementTimeline>(
    `/api/players/${steamId}/achievements/timeline`,
    { days, app_id: appId },
  );
}

export function getGameDetail(steamId: string, appId: number) {
  return apiGet<GameDetail>(`/api/players/${steamId}/games/${appId}`);
}

export function getGameAchievements(steamId: string, appId: number) {
  return apiGet<Achievement[]>(
    `/api/players/${steamId}/games/${appId}/achievements`,
  );
}

export function getPlaytimeGraph(steamId: string, appId: number) {
  return apiGet<PlaytimeGraph>(`/api/players/${steamId}/games/${appId}/playtime`);
}

export function getScreenshots(steamId: string, appId: number) {
  return apiGet<string[]>(`/api/players/${steamId}/games/${appId}/screenshots`);
}

export function getAdvancedStats(steamId: string, appId: number) {
  return apiGet<AdvancedStats>(`/api/players/${steamId}/games/${appId}/advanced`);
}

export function getSuggestions(steamId: string, appId: number) {
  return apiGet<Suggestions>(`/api/players/${steamId}/games/${appId}/suggestions`);
}

export function compare(playerA: string, playerB: string) {
  return apiGet<Comparison>("/api/compare", {
    player_a: playerA,
    player_b: playerB,
  });
}

export function getComparisons(steamId?: string, limit?: number) {
  return apiGet<ComparisonRecord[]>("/api/comparisons", {
    steam_id: steamId,
    limit,
  });
}

export function getOpponents(steamId: string, limit?: number) {
  return apiGet<Opponent[]>(`/api/players/${steamId}/opponents`, { limit });
}
