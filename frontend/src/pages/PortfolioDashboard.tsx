import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "../components/EmptyState";
import { FreshnessBadge } from "../components/FreshnessBadge";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import { ApiError, listProjects } from "../lib/api";
import type { Project } from "../lib/types";
import {
  PRIORITIES,
  PRIORITY_LABELS,
  PROJECT_PHASES,
  PROJECT_PHASE_LABELS,
  PROJECT_STATUSES,
  PROJECT_STATUS_LABELS,
  PROJECT_STATUS_TONE,
  type Priority,
  type ProjectPhase,
  type ProjectStatus,
} from "../lib/vocab";
import { useCurrentUser } from "../state/currentUser";

const SORT_OPTIONS = [
  { value: "priority", label: "Priority" },
  { value: "name", label: "Name" },
  { value: "freshness", label: "Oldest data first" },
] as const;
type SortKey = (typeof SORT_OPTIONS)[number]["value"];

const PRIORITY_RANK: Record<Priority, number> = { high: 0, medium: 1, low: 2 };

export function PortfolioDashboard() {
  const { email } = useCurrentUser();
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | "">("");
  const [phaseFilter, setPhaseFilter] = useState<ProjectPhase | "">("");
  const [priorityFilter, setPriorityFilter] = useState<Priority | "">("");
  const [staleOnly, setStaleOnly] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("priority");

  useEffect(() => {
    setProjects(null);
    setError(null);
    listProjects(email)
      .then(setProjects)
      .catch((e: ApiError) => setError(e.message));
  }, [email]);

  const blockedCount = projects?.filter((p) => p.status === "blocked").length ?? 0;
  const staleCount = projects?.filter((p) => p.is_stale).length ?? 0;

  const visible = useMemo(() => {
    if (!projects) return null;
    const needle = search.trim().toLowerCase();
    const filtered = projects.filter((p) => {
      if (statusFilter && p.status !== statusFilter) return false;
      if (phaseFilter && p.phase !== phaseFilter) return false;
      if (priorityFilter && p.priority !== priorityFilter) return false;
      if (staleOnly && !p.is_stale) return false;
      if (
        needle &&
        !p.name.toLowerCase().includes(needle) &&
        !p.slug.toLowerCase().includes(needle) &&
        !(p.current_next_action ?? "").toLowerCase().includes(needle)
      ) {
        return false;
      }
      return true;
    });
    return filtered.sort((a, b) => {
      if (sortKey === "name") return a.name.localeCompare(b.name);
      if (sortKey === "freshness") {
        // Never-updated projects are the most urgent, then oldest data first.
        if (a.data_as_of === b.data_as_of) return a.name.localeCompare(b.name);
        if (a.data_as_of === null) return -1;
        if (b.data_as_of === null) return 1;
        return a.data_as_of.localeCompare(b.data_as_of);
      }
      const rank = PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority];
      return rank !== 0 ? rank : a.name.localeCompare(b.name);
    });
  }, [projects, search, statusFilter, phaseFilter, priorityFilter, staleOnly, sortKey]);

  const filtersActive =
    search.trim() !== "" || statusFilter !== "" || phaseFilter !== "" || priorityFilter !== "" || staleOnly;

  function clearFilters() {
    setSearch("");
    setStatusFilter("");
    setPhaseFilter("");
    setPriorityFilter("");
    setStaleOnly(false);
  }

  const selectClass =
    "rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary";

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
          <SummaryCard label="Total projects" value={projects.length} onClick={clearFilters} />
          <SummaryCard
            label="Blocked"
            value={blockedCount}
            tone={blockedCount > 0 ? "danger" : undefined}
            active={statusFilter === "blocked"}
            onClick={() => {
              clearFilters();
              setStatusFilter(statusFilter === "blocked" ? "" : "blocked");
            }}
          />
          <SummaryCard
            label="Stale data"
            value={staleCount}
            tone={staleCount > 0 ? "warning" : undefined}
            active={staleOnly}
            onClick={() => {
              clearFilters();
              setStaleOnly(!staleOnly);
            }}
          />
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search name, slug or next action…"
            className="w-64 rounded-md border border-border bg-surface px-3 py-1.5 text-sm text-text placeholder:text-muted-text focus-visible:ring-2 focus-visible:ring-primary"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as ProjectStatus | "")}
            className={selectClass}
            aria-label="Filter by status"
          >
            <option value="">All statuses</option>
            {PROJECT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {PROJECT_STATUS_LABELS[s]}
              </option>
            ))}
          </select>
          <select
            value={phaseFilter}
            onChange={(e) => setPhaseFilter(e.target.value as ProjectPhase | "")}
            className={selectClass}
            aria-label="Filter by phase"
          >
            <option value="">All phases</option>
            {PROJECT_PHASES.map((p) => (
              <option key={p} value={p}>
                {PROJECT_PHASE_LABELS[p]}
              </option>
            ))}
          </select>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value as Priority | "")}
            className={selectClass}
            aria-label="Filter by priority"
          >
            <option value="">All priorities</option>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {PRIORITY_LABELS[p]}
              </option>
            ))}
          </select>
          <label className="flex items-center gap-1.5 text-sm text-text">
            <input
              type="checkbox"
              checked={staleOnly}
              onChange={(e) => setStaleOnly(e.target.checked)}
              className="rounded border-border text-primary focus-visible:ring-2 focus-visible:ring-primary"
            />
            Stale only
          </label>
          <label className="ml-auto flex items-center gap-2 text-xs font-medium text-muted-text">
            Sort by
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
              className={selectClass}
            >
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          {filtersActive && (
            <button
              type="button"
              onClick={clearFilters}
              className="rounded-md border border-border bg-surface px-2.5 py-1.5 text-xs font-medium text-text hover:bg-surface-muted"
            >
              Clear filters
            </button>
          )}
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

      {visible && projects && projects.length > 0 && visible.length === 0 && (
        <EmptyState
          title="No projects match these filters"
          message="Adjust or clear the filters above to see the rest of the portfolio."
        />
      )}

      {visible && visible.length > 0 && (
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
              {visible.map((p) => (
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
  active,
  onClick,
}: {
  label: string;
  value: number;
  tone?: "danger" | "warning";
  active?: boolean;
  onClick?: () => void;
}) {
  const toneClass =
    tone === "danger"
      ? "text-danger"
      : tone === "warning"
        ? "text-warning"
        : "text-text";
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg border bg-surface px-4 py-3 text-left transition-colors hover:bg-surface-muted/60 focus-visible:ring-2 focus-visible:ring-primary ${
        active ? "border-primary" : "border-border"
      }`}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-muted-text">{label}</p>
      <p className={`mt-1 text-2xl font-semibold tabular-nums ${toneClass}`}>{value}</p>
    </button>
  );
}
