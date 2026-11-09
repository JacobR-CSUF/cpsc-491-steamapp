import { Suspense } from "react";
import ComparisonView from "@/components/compare/ComparisonView";
import StatusMessage from "@/components/compare/StatusMessage";

export default function ComparePage() {
  return (
    <Suspense
      fallback={
        <StatusMessage
          title="Comparing players…"
          message="The first comparison of a large library can take a minute."
        />
      }
    >
      <ComparisonView />
    </Suspense>
  );
}
