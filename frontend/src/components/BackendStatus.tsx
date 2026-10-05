"use client";

import { useEffect, useState } from "react";
import { getHealth, type HealthStatus } from "@/lib/api";

export default function BackendStatus() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [unreachable, setUnreachable] = useState(false);

  useEffect(() => {
    let active = true;

    async function updateStatus() {
      try {
        const result = await getHealth();

        if (active) {
          setHealth(result);
          setUnreachable(false);
        }
      } catch {
        if (active) {
          setHealth(null);
          setUnreachable(true);
        }
      }
    }

    void updateStatus();
    const timer = setInterval(() => void updateStatus(), 10000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <section className="rounded-lg border p-6">
      <h2 className="mb-4 text-xl font-semibold">Backend status</h2>

      {unreachable ? (
        <p className="text-red-600">Backend unreachable</p>
      ) : health === null ? (
        <p>Checking backend...</p>
      ) : (
        <ul className="space-y-2">
          {Object.entries(health).map(([service, status]) => (
            <li key={service}>
              <span className="font-medium">{service.toUpperCase()}</span>
              {": "}
              {status}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}