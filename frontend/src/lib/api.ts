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