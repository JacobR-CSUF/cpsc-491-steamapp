import HistoryList from "@/components/history/HistoryList";

export default function HistoryPage() {
  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold tracking-tight">Comparison History</h1>
      <HistoryList />
    </div>
  );
}
