import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "../components/EmptyState";
import { FreshnessBadge } from "../components/FreshnessBadge";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import { ApiError, listProjects } from "../lib/api";
import type { Project } from "../lib/types";
import {
  PRIORITY_LABELS,
  PROJECT_PHASE_LABELS,
  PROJECT_STATUS_LABELS,
  PROJECT_STATUS_TONE,
} from "../lib/vocab";
import { useCurrentUser } from "../state/currentUser";

export function PortfolioDashboard() {
  const { email } = useCurrentUser();
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setProjects(null);
    setError(null);
    listProjects(email)
      .then(setProjects)
      .catch((e: ApiError) => setError(e.message));
  }, [email]);

  const blockedCount = projects?.filter((p) => p.status === "blocked").length ?? 0;
  const staleCount = projects?.filter((p) => p.is_stale).length ?? 0;

  return (
    <div>
      <PageHeader
        title="Portfolio"
        subtitle="Internal development projects: phase, status, freshness and next actions."
        actions={
          <Link
            to="/projects/new"
            className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-fg hover:bg-primary-hover"
          >
            New project
          </Link>
        }
      />

      {error && (
        <div className="mb-6 rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <SummaryCard label="Total projects" value={projects.length} />
          <SummaryCard label="Blocked" value={blockedCount} tone={blockedCount > 0 ? "danger" : undefined} />
          <SummaryCard label="Stale data" value={staleCount} tone={staleCount > 0 ? "warning" : undefined} />
        </div>
      )}

      {projects === null && !error && (
        <div className="rounded-lg border border-border bg-surface px-6 py-12 text-center text-sm text-muted-text">
          Loading projects…
        </div>
      )}

      {projects && projects.length === 0 && (
        <EmptyState
          title="No projects visible yet"
          message="Create the first project, or check that you're signed in as a user with portfolio read access."
        />
      )}

      {projects && projects.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-border bg-surface">
          <table className="w-full min-w-[720px] table-fixed text-left text-sm">
            <colgroup>
              <col className="w-48" />
              <col className="w-24" />
              <col className="w-28" />
              <col className="w-20" />
              <col className="w-32" />
              <col className="w-56" />
              <col className="w-44" />
            </colgroup>
            <thead className="bg-surface-muted text-xs uppercase tracking-wide text-muted-text">
              <tr>
                <th className="px-4 py-2 font-medium">Project</th>
                <th className="px-4 py-2 font-medium">Phase</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Priority</th>
                <th className="px-4 py-2 font-medium">Owner</th>
                <th className="px-4 py-2 font-medium">Next action</th>
                <th className="px-4 py-2 font-medium">Freshness</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {projects.map((p) => (
                <tr key={p.id} className="hover:bg-surface-muted/60">
                  <td className="truncate px-4 py-3">
                    <Link to={`/projects/${p.id}`} className="font-medium text-primary hover:underline">
                      {p.name}
                    </Link>
                  </td>
                  <td className="truncate px-4 py-3 text-text">{PROJECT_PHASE_LABELS[p.phase]}</td>
                  <td className="px-4 py-3">
                    <StatusChip label={PROJECT_STATUS_LABELS[p.status]} tone={PROJECT_STATUS_TONE[p.status]} />
                  </td>
                  <td className="truncate px-4 py-3 text-text">{PRIORITY_LABELS[p.priority]}</td>
                  <td className="truncate px-4 py-3 text-muted-text">{p.owner?.name ?? "Unassigned"}</td>
                  <td className="truncate px-4 py-3 text-muted-text" title={p.current_next_action ?? ""}>
                    {p.current_next_action || "—"}
                  </td>
                  <td className="px-4 py-3">
                    <FreshnessBadge dataAsOf={p.data_as_of} isStale={p.is_stale} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone?: "danger" | "warning";
}) {
  const toneClass =
    tone === "danger"
      ? "text-danger"
      : tone === "warning"
        ? "text-warning"
        : "text-text";
  return (
    <div className="rounded-lg border border-border bg-surface px-4 py-3">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-text">{label}</p>
      <p className={`mt-1 text-2xl font-semibold tabular-nums ${toneClass}`}>{value}</p>
    </div>
  );
}
