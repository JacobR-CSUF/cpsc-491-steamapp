export const STEAM_ID_PATTERN = /^7656119\d{10}$/;

export function isValidSteamId(value: string): boolean {
  return STEAM_ID_PATTERN.test(value.trim());
}
