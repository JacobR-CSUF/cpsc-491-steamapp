export interface Player {
  steam_id: string;
  persona_name: string;
  avatar_url: string | null;
  profile_url: string | null;
  visibility: number;
}

export interface OwnedGame {
  app_id: number;
  name: string;
  icon_url: string | null;
  playtime_minutes: number;
  recent_playtime_minutes: number;
  last_played_at: string | null;
}

export interface CompletedGame {
  app_id: number;
  name: string;
}

export interface PlayerStats {
  steam_id: string;
  games_owned: number;
  games_played: number;
  account_value_cents: number;
  currency: string;
  achievements_unlocked: number;
  achievements_available: number;
  completion_rate: number;
  completed_games: CompletedGame[];
}

export interface SharedGame {
  app_id: number;
  name: string;
  total: number;
  unlocked_a: number;
  unlocked_b: number;
  difference: number;
}

export interface Comparison {
  player_a: PlayerStats;
  player_b: PlayerStats;
  shared_games: SharedGame[];
  mutual_achievements: number;
  achievements_difference: number;
  completion_rate_difference: number;
}

export interface ComparisonRecord {
  id: number;
  compared_at: string;
  player_a: Player;
  player_b: Player;
}

export interface Opponent {
  player: Player;
  last_compared_at: string;
  times_compared: number;
}

export type ProfileStatus =
  | "public"
  | "not_found"
  | "profile_private"
  | "games_private"
  | "playtime_hidden";

export interface ProfileStatusInfo {
  steam_id: string;
  status: ProfileStatus;
  message: string;
}

export interface GameProgress {
  app_id: number;
  name: string;
  unlocked: number;
  total: number;
}

export interface Achievement {
  api_name: string;
  display_name: string;
  description: string | null;
  icon_url: string | null;
  hidden: boolean;
  achieved: boolean;
  unlocked_at: string | null;
}

export type TimelineDays = 30 | 60 | 90;

export interface TimelinePoint {
  date: string;
  unlocked: number;
}

export interface AchievementTimeline {
  days: TimelineDays;
  app_id: number | null;
  total: number;
  points: TimelinePoint[];
}

export interface LastAchievement {
  api_name: string;
  display_name: string;
  unlocked_at: string | null;
}

export interface GameDetail {
  steam_id: string;
  app_id: number;
  name: string;
  icon_url: string | null;
  playtime_minutes: number;
  recent_playtime_minutes: number;
  last_played_at: string | null;
  played_recently: boolean;
  achievements_unlocked: number;
  achievements_total: number;
  last_achievement: LastAchievement | null;
  screenshots: string[];
}

export interface PlaytimePoint {
  api_name: string;
  display_name: string;
  unlocked_at: string;
  estimated_hours: number;
}

export interface PlaytimeGraph {
  app_id: number;
  total_hours: number;
  estimated: boolean;
  points: PlaytimePoint[];
}

export interface MissingAchievement {
  api_name: string;
  display_name: string;
  description: string | null;
  icon_url: string | null;
  global_percent: number | null;
}

export interface AdvancedStats {
  app_id: number;
  name: string;
  unlocked: number;
  total: number;
  ratio: number;
  missing: MissingAchievement[];
}

export interface Suggestions {
  app_id: number;
  suggestions: string;
}
