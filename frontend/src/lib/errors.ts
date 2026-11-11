import { ApiError } from "@/lib/api";

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if ([400, 403, 404, 502].includes(error.status)) {
      return error.detail;
    }

    if (error.status === 422) {
      return "One of these SteamID64s is invalid.";
    }
  }

  if (error instanceof TypeError) {
    return "The app’s server isn’t responding.";
  }

  return "Something went wrong. Try again.";
}