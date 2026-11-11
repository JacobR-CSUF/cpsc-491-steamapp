import { LoadingSkeleton } from "@/components/Skeleton";
import type { Metadata } from "next";
import { Suspense } from "react";
import ComparisonView from "@/components/compare/ComparisonView";

export const metadata: Metadata = {
  title: "Results",
};

export default function ComparePage() {
  return (
    <Suspense
      fallback={
        <LoadingSkeleton variant="overview" label="Preparing comparison…" />
      }
    >
      <ComparisonView />
    </Suspense>
  );
}
