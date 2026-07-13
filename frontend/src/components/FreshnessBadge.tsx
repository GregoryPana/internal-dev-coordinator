import { StatusChip } from "./StatusChip";

// Freshness threshold mirrors backend/app/config.py (freshness_threshold_days = 14).
function formatDataAsOf(dataAsOf: string | null): string {
  if (!dataAsOf) return "No status evidence yet";
  const date = new Date(dataAsOf);
  return `Data as of ${date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}`;
}

export function FreshnessBadge({ dataAsOf, isStale }: { dataAsOf: string | null; isStale: boolean }) {
  const label = formatDataAsOf(dataAsOf);
  if (!dataAsOf) return <StatusChip label={label} tone="neutral" />;
  return <StatusChip label={isStale ? `${label} (stale)` : label} tone={isStale ? "warning" : "success"} />;
}
