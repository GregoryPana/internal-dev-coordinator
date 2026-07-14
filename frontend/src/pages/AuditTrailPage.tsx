import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import { ApiError, getProject, listAuditEvents, listProjectAuditEvents } from "../lib/api";
import type { AuditEventPage, Project } from "../lib/types";
import {
  AUDIT_ACTION_TYPES,
  AUDIT_ACTION_TYPE_LABELS,
  AUDIT_OBJECT_TYPE_LABELS,
  type AuditActionType,
} from "../lib/vocab";
import { useCurrentUser } from "../state/currentUser";

const PAGE_SIZE = 25;

function metadataSummary(metadata: Record<string, unknown> | null): string {
  if (!metadata) return "";
  return Object.entries(metadata)
    .map(([k, v]) => `${k}: ${typeof v === "object" ? JSON.stringify(v) : String(v)}`)
    .join(" · ");
}

export function AuditTrailPage() {
  const { id } = useParams();
  const projectId = id ? Number(id) : null;
  const { email } = useCurrentUser();
  const [page, setPage] = useState<AuditEventPage | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<{ status: number; message: string } | null>(null);
  const [actionType, setActionType] = useState<AuditActionType | "">("");
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    setOffset(0);
  }, [email, projectId, actionType]);

  useEffect(() => {
    setError(null);
    setPage(null);
    const query = { actionType, limit: PAGE_SIZE, offset };
    const load = projectId
      ? listProjectAuditEvents(email, projectId, query)
      : listAuditEvents(email, query);
    load
      .then(setPage)
      .catch((e: ApiError) => setError({ status: e.status, message: e.message }));
    if (projectId) {
      getProject(email, projectId)
        .then(setProject)
        .catch(() => setProject(null));
    } else {
      setProject(null);
    }
  }, [email, projectId, actionType, offset]);

  const title = projectId ? `Audit trail — ${project?.name ?? `project #${projectId}`}` : "Audit trail";
  const subtitle = projectId
    ? "Every recorded action on this project, newest first. Append-only — nothing here can be edited or deleted."
    : "Portfolio-wide audit feed (admin and auditor roles). Append-only — nothing here can be edited or deleted.";

  return (
    <div>
      <PageHeader
        title={title}
        subtitle={subtitle}
        actions={
          projectId ? (
            <Link
              to={`/projects/${projectId}`}
              className="rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-text hover:bg-surface-muted"
            >
              Back to project
            </Link>
          ) : undefined
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 text-xs font-medium text-text">
          Action
          <select
            value={actionType}
            onChange={(e) => setActionType(e.target.value as AuditActionType | "")}
            className="rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary"
          >
            <option value="">All actions</option>
            {AUDIT_ACTION_TYPES.map((a) => (
              <option key={a} value={a}>
                {AUDIT_ACTION_TYPE_LABELS[a]}
              </option>
            ))}
          </select>
        </label>
        {page && (
          <span className="text-xs text-muted-text">
            {page.total} event{page.total === 1 ? "" : "s"}
          </span>
        )}
      </div>

      {error ? (
        <div className="rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          {error.status === 403
            ? "You do not have access to this audit view. The portfolio-wide feed requires an admin or auditor role."
            : error.message}
        </div>
      ) : page === null ? (
        <p className="text-sm text-muted-text">Loading audit events…</p>
      ) : page.items.length === 0 ? (
        <EmptyState title="No audit events" message="Nothing recorded yet for this filter." />
      ) : (
        <>
          <div className="hidden overflow-x-auto rounded-md border border-border md:block">
            <table className="w-full min-w-[760px] table-fixed text-left text-sm">
              <colgroup>
                <col className="w-40" />
                <col className="w-44" />
                <col className="w-40" />
                <col className="w-28" />
                {!projectId && <col className="w-24" />}
                <col />
              </colgroup>
              <thead className="bg-surface-muted text-xs uppercase tracking-wide text-muted-text">
                <tr>
                  <th className="px-3 py-2 font-medium">When</th>
                  <th className="px-3 py-2 font-medium">Actor</th>
                  <th className="px-3 py-2 font-medium">Action</th>
                  <th className="px-3 py-2 font-medium">Object</th>
                  {!projectId && <th className="px-3 py-2 font-medium">Project</th>}
                  <th className="px-3 py-2 font-medium">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-surface">
                {page.items.map((event) => (
                  <tr key={event.id} className="hover:bg-surface-muted/60">
                    <td className="truncate px-3 py-2 text-muted-text" title={event.created_at}>
                      {new Date(event.created_at).toLocaleString()}
                    </td>
                    <td className="truncate px-3 py-2 text-text" title={event.actor_email ?? undefined}>
                      {event.actor_name ?? event.actor_email ?? "system"}
                    </td>
                    <td className="px-3 py-2">
                      <StatusChip label={AUDIT_ACTION_TYPE_LABELS[event.action_type]} tone="neutral" />
                    </td>
                    <td className="truncate px-3 py-2 text-muted-text">
                      {AUDIT_OBJECT_TYPE_LABELS[event.object_type]}
                      {event.object_id != null ? ` #${event.object_id}` : ""}
                    </td>
                    {!projectId && (
                      <td className="truncate px-3 py-2">
                        {event.project_id != null ? (
                          <Link
                            to={`/projects/${event.project_id}`}
                            className="text-primary hover:underline"
                          >
                            #{event.project_id}
                          </Link>
                        ) : (
                          <span className="text-muted-text">—</span>
                        )}
                      </td>
                    )}
                    <td
                      className="truncate px-3 py-2 text-muted-text"
                      title={metadataSummary(event.metadata_json)}
                    >
                      {metadataSummary(event.metadata_json) || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-3 md:hidden">
            {page.items.map((event) => (
              <div key={event.id} className="rounded-md border border-border p-3">
                <div className="mb-2 flex items-start justify-between gap-2">
                  <StatusChip label={AUDIT_ACTION_TYPE_LABELS[event.action_type]} tone="neutral" />
                  <span className="text-xs text-muted-text" title={event.created_at}>
                    {new Date(event.created_at).toLocaleString()}
                  </span>
                </div>
                <dl className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Actor</dt>
                    <dd className="truncate text-text" title={event.actor_email ?? undefined}>
                      {event.actor_name ?? event.actor_email ?? "system"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Object</dt>
                    <dd className="truncate text-muted-text">
                      {AUDIT_OBJECT_TYPE_LABELS[event.object_type]}
                      {event.object_id != null ? ` #${event.object_id}` : ""}
                    </dd>
                  </div>
                  {!projectId && (
                    <div>
                      <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Project</dt>
                      <dd>
                        {event.project_id != null ? (
                          <Link to={`/projects/${event.project_id}`} className="text-primary hover:underline">
                            #{event.project_id}
                          </Link>
                        ) : (
                          <span className="text-muted-text">—</span>
                        )}
                      </dd>
                    </div>
                  )}
                  {metadataSummary(event.metadata_json) && (
                    <div className="col-span-2">
                      <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Details</dt>
                      <dd className="text-muted-text">{metadataSummary(event.metadata_json)}</dd>
                    </div>
                  )}
                </dl>
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-xs text-muted-text">
              Showing {page.offset + 1}–{page.offset + page.items.length} of {page.total}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-text hover:bg-surface-muted disabled:opacity-50"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={page.offset + page.items.length >= page.total}
                onClick={() => setOffset(offset + PAGE_SIZE)}
                className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-text hover:bg-surface-muted disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
