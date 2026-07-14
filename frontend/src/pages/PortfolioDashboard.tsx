import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { EmptyState } from "../components/EmptyState";
import { FreshnessBadge } from "../components/FreshnessBadge";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import { ApiError, getAppConfig, listProjects } from "../lib/api";
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

// Dashboard segregation: delivered = live/handover phase or completed status;
// everything else is still in the delivery pipeline.
function isDelivered(p: Project): boolean {
  return p.phase === "live" || p.phase === "handover" || p.status === "complete";
}

export function PortfolioDashboard() {
  const { email } = useCurrentUser();
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | "">("");
  const [phaseFilter, setPhaseFilter] = useState<ProjectPhase | "">("");
  const [priorityFilter, setPriorityFilter] = useState<Priority | "">("");
  const [staleOnly, setStaleOnly] = useState(false);
  const [aiOnly, setAIOnly] = useState(false);
  const [automationOnly, setAutomationOnly] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("priority");
  const [edition, setEdition] = useState<"custom" | "product">("product");

  useEffect(() => {
    getAppConfig().then((c) => setEdition(c.edition)).catch(() => {});
  }, []);

  useEffect(() => {
    setProjects(null);
    setError(null);
    listProjects(email)
      .then(setProjects)
      .catch((e: ApiError) => setError(e.message));
  }, [email]);

  const blockedCount = projects?.filter((p) => p.status === "blocked").length ?? 0;
  const staleCount = projects?.filter((p) => p.is_stale).length ?? 0;
  const aiCount = projects?.filter((p) => p.uses_ai).length ?? 0;
  const automationCount = projects?.filter((p) => p.uses_process_automation).length ?? 0;

  const visible = useMemo(() => {
    if (!projects) return null;
    const needle = search.trim().toLowerCase();
    const filtered = projects.filter((p) => {
      if (statusFilter && p.status !== statusFilter) return false;
      if (phaseFilter && p.phase !== phaseFilter) return false;
      if (priorityFilter && p.priority !== priorityFilter) return false;
      if (staleOnly && !p.is_stale) return false;
      if (aiOnly && !p.uses_ai) return false;
      if (automationOnly && !p.uses_process_automation) return false;
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
  }, [
    projects,
    search,
    statusFilter,
    phaseFilter,
    priorityFilter,
    staleOnly,
    aiOnly,
    automationOnly,
    sortKey,
  ]);

  const filtersActive =
    search.trim() !== "" ||
    statusFilter !== "" ||
    phaseFilter !== "" ||
    priorityFilter !== "" ||
    staleOnly ||
    aiOnly ||
    automationOnly;

  function clearFilters() {
    setSearch("");
    setStatusFilter("");
    setPhaseFilter("");
    setPriorityFilter("");
    setStaleOnly(false);
    setAIOnly(false);
    setAutomationOnly(false);
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
        <div
          className={`mb-6 grid grid-cols-2 gap-4 sm:grid-cols-3 ${
            edition === "custom" ? "lg:grid-cols-5" : ""
          }`}
        >
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
          {edition === "custom" && (
            <>
              <SummaryCard
                label="Uses AI"
                value={aiCount}
                active={aiOnly}
                onClick={() => {
                  clearFilters();
                  setAIOnly(!aiOnly);
                }}
              />
              <SummaryCard
                label="Process automation"
                value={automationCount}
                active={automationOnly}
                onClick={() => {
                  clearFilters();
                  setAutomationOnly(!automationOnly);
                }}
              />
            </>
          )}
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
        <div className="space-y-8">
          <ProjectSection
            title="In delivery"
            subtitle="Concept, ongoing development and pilot/test projects."
            projects={visible.filter((p) => !isDelivered(p))}
          />
          <ProjectSection
            title="Live & completed"
            subtitle="Projects in production, handed over, or marked complete."
            projects={visible.filter(isDelivered)}
          />
        </div>
      )}
    </div>
  );
}

function ProjectSection({
  title,
  subtitle,
  projects,
}: {
  title: string;
  subtitle: string;
  projects: Project[];
}) {
  return (
    <section>
      <div className="mb-2 flex items-baseline gap-3">
        <h2 className="text-sm font-semibold text-text">{title}</h2>
        <span className="text-xs text-muted-text">{subtitle}</span>
        <span className="ml-auto text-xs tabular-nums text-muted-text">
          {projects.length} project{projects.length === 1 ? "" : "s"}
        </span>
      </div>
      {projects.length === 0 ? (
        <p className="rounded-lg border border-dashed border-border bg-surface-muted px-4 py-3 text-sm text-muted-text">
          Nothing here for the current filters.
        </p>
      ) : (
        <>
          <div className="hidden overflow-x-auto rounded-lg border border-border bg-surface md:block">
            <table className="w-full min-w-[820px] table-fixed text-left text-sm">
              <colgroup>
                <col className="w-48" />
                <col className="w-32" />
                <col className="w-28" />
                <col className="w-20" />
                <col className="w-24" />
                <col className="w-32" />
                <col className="w-52" />
                <col className="w-44" />
              </colgroup>
              <thead className="bg-surface-muted text-xs uppercase tracking-wide text-muted-text">
                <tr>
                  <th className="px-4 py-2 font-medium">Project</th>
                  <th className="px-4 py-2 font-medium">Phase</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Priority</th>
                  <th className="px-4 py-2 font-medium">Progress</th>
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
                    <td className="px-4 py-3 text-muted-text">
                      {p.percent_complete != null ? (
                        <span className="flex items-center gap-1.5">
                          <span className="h-1.5 w-12 rounded-full bg-surface-muted">
                            <span
                              className="block h-1.5 rounded-full bg-primary"
                              style={{ width: `${p.percent_complete}%` }}
                            />
                          </span>
                          <span className="text-xs tabular-nums">{p.percent_complete}%</span>
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="truncate px-4 py-3 text-muted-text">{p.owner?.name ?? "Unassigned"}</td>
                    <td className="truncate px-4 py-3 text-muted-text" title={p.current_next_action ?? ""}>
                      {p.current_next_action || "—"}
                    </td>
                    <td className="px-4 py-3">
                      <FreshnessBadge dataAsOf={p.data_as_of} isStale={p.is_stale} />
                      {p.repo_last_push && (
                        <p className="mt-1 text-xs text-muted-text" title="Latest tracked GitHub push">
                          pushed {new Date(p.repo_last_push).toLocaleDateString()}
                        </p>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-3 md:hidden">
            {projects.map((p) => (
              <Link
                key={p.id}
                to={`/projects/${p.id}`}
                className="rounded-lg border border-border bg-surface p-4 hover:bg-surface-muted/60"
              >
                <div className="mb-2 flex items-start justify-between gap-2">
                  <span className="font-medium text-primary">{p.name}</span>
                  <StatusChip label={PROJECT_STATUS_LABELS[p.status]} tone={PROJECT_STATUS_TONE[p.status]} />
                </div>
                <dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Phase</dt>
                    <dd className="text-text">{PROJECT_PHASE_LABELS[p.phase]}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Priority</dt>
                    <dd className="text-text">{PRIORITY_LABELS[p.priority]}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Owner</dt>
                    <dd className="truncate text-text">{p.owner?.name ?? "Unassigned"}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Progress</dt>
                    <dd className="tabular-nums text-text">
                      {p.percent_complete != null ? `${p.percent_complete}%` : "—"}
                    </dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Next action</dt>
                    <dd className="text-text">{p.current_next_action || "—"}</dd>
                  </div>
                  <div className="col-span-2">
                    <FreshnessBadge dataAsOf={p.data_as_of} isStale={p.is_stale} />
                  </div>
                </dl>
              </Link>
            ))}
          </div>
        </>
      )}
    </section>
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
     