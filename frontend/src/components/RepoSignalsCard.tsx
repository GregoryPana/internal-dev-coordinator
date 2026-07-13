import { useEffect, useState } from "react";
import { ApiError, getRepoSignals } from "../lib/api";
import type { RepoSignals } from "../lib/types";

/** Read-only GitHub signals (Phase 4). Renders nothing when the project has
 * no GitHub repo URL or the integration is disabled; shows a soft warning
 * when GitHub itself could not be reached. */
export function RepoSignalsCard({
  projectId,
  userEmail,
}: {
  projectId: number;
  userEmail: string;
}) {
  const [signals, setSignals] = useState<RepoSignals | "none" | "disabled" | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSignals(null);
    setError(null);
    getRepoSignals(userEmail, projectId)
      .then(setSignals)
      .catch((e: ApiError) => setError(e.message));
  }, [userEmail, projectId]);

  if (signals === "none" || signals === "disabled") return null;

  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <h2 className="mb-1 text-sm font-semibold text-text">Repository activity</h2>
      {error ? (
        <p className="text-sm text-warning">Could not reach GitHub: {error}</p>
      ) : signals === null ? (
        <p className="text-sm text-muted-text">Checking GitHub…</p>
      ) : (
        <>
          <p className="mb-3 text-xs text-muted-text">
            {signals.repo_full_name} · {signals.default_branch} · read-only
          </p>
          <dl className="divide-y divide-border">
            <div className="flex flex-col gap-0.5 py-2">
              <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">
                Last push
              </dt>
              <dd className="text-sm text-text">
                {signals.pushed_at ? new Date(signals.pushed_at).toLocaleString() : "—"}
              </dd>
            </div>
            {signals.last_commit && (
              <div className="flex flex-col gap-0.5 py-2">
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">
                  Last commit
                </dt>
                <dd className="text-sm text-text">
                  <span className="font-mono text-xs text-muted-text">{signals.last_commit.sha}</span>{" "}
                  {signals.last_commit.message}
                </dd>
                <dd className="text-xs text-muted-text">
                  {signals.last_commit.author ?? "unknown author"}
                  {signals.last_commit.committed_at
                    ? ` · ${new Date(signals.last_commit.committed_at).toLocaleString()}`
                    : ""}
                </dd>
              </div>
            )}
            <div className="flex gap-6 py-2">
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">
                  Open PRs
                </dt>
                <dd className="text-sm tabular-nums text-text">{signals.open_pr_count}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">
                  Open issues
                </dt>
                <dd className="text-sm tabular-nums text-text">{signals.open_issue_count}</dd>
              </div>
            </div>
          </dl>
        </>
      )}
    </div>
  );
}
