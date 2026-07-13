import { useEffect, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { DocumentationMatrix } from "../components/DocumentationMatrix";
import { FreshnessBadge } from "../components/FreshnessBadge";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import { ApiError, getProject, listStatusEvents } from "../lib/api";
import type { Project, StatusEvent } from "../lib/types";
import {
  CLASSIFICATION_LABELS,
  PRIORITY_LABELS,
  PROJECT_PHASE_LABELS,
  PROJECT_STATUS_LABELS,
  PROJECT_STATUS_TONE,
  PROJECT_TYPE_LABELS,
} from "../lib/vocab";
import { useCurrentUser } from "../state/currentUser";

function EvidenceLink({ label, href }: { label: string; href: string | null }) {
  if (!href) return <span className="text-sm text-muted-text">{label}: not set</span>;
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="text-sm text-primary hover:underline"
    >
      {label}
    </a>
  );
}

function MetadataRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5 py-2">
      <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">{label}</dt>
      <dd className="text-sm text-text">{value}</dd>
    </div>
  );
}

function StatusEventCard({ event }: { event: StatusEvent }) {
  const date = new Date(event.event_date + "T00:00:00").toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
  return (
    <div className="rounded-md border border-border p-4">
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="text-sm font-medium text-text">{date}</span>
        <span className="text-xs text-muted-text">{event.author.name}</span>
      </div>
      <p className="text-sm text-text">{event.summary}</p>
      {event.blockers && (
        <div className="mt-2 rounded-md border border-danger-border bg-danger-bg px-3 py-2 text-sm text-danger">
          <span className="font-medium">Blocker: </span>
          {event.blockers}
        </div>
      )}
      <dl className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {event.completed_work && (
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Completed work</dt>
            <dd className="text-sm text-muted-text">{event.completed_work}</dd>
          </div>
        )}
        {event.next_actions && (
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Next actions</dt>
            <dd className="text-sm text-muted-text">{event.next_actions}</dd>
          </div>
        )}
        {event.verification_notes && (
          <div className="sm:col-span-2">
            <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">
              Verification notes
            </dt>
            <dd className="text-sm text-muted-text">{event.verification_notes}</dd>
          </div>
        )}
      </dl>
    </div>
  );
}

export function ProjectProfile() {
  const { id } = useParams();
  const { email } = useCurrentUser();
  const [project, setProject] = useState<Project | null>(null);
  const [statusEvents, setStatusEvents] = useState<StatusEvent[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setProject(null);
    setStatusEvents(null);
    setError(null);
    getProject(email, Number(id))
      .then(setProject)
      .catch((e: ApiError) => setError(e.message));
    listStatusEvents(email, Number(id))
      .then(setStatusEvents)
      .catch(() => setStatusEvents([]));
  }, [email, id]);

  if (error) {
    return (
      <div className="rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
        {error}
      </div>
    );
  }

  if (!project) {
    return <div className="text-sm text-muted-text">Loading project…</div>;
  }

  return (
    <div>
      <PageHeader
        title={project.name}
        subtitle={project.business_purpose || project.description || "No purpose recorded yet."}
        actions={
          <>
            <Link
              to={`/projects/${project.id}/ai-summary`}
              className="rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-text hover:bg-surface-muted"
            >
              AI summary
            </Link>
            <Link
              to={`/projects/${project.id}/starter-pack`}
              className="rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-text hover:bg-surface-muted"
            >
              Starter pack
            </Link>
            <Link
              to={`/projects/${project.id}/edit`}
              className="rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-text hover:bg-surface-muted"
            >
              Edit project
            </Link>
          </>
        }
      />

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <StatusChip label={PROJECT_STATUS_LABELS[project.status]} tone={PROJECT_STATUS_TONE[project.status]} />
        <StatusChip label={PROJECT_PHASE_LABELS[project.phase]} tone="neutral" />
        <StatusChip label={`${PRIORITY_LABELS[project.priority]} priority`} tone="neutral" />
        <FreshnessBadge dataAsOf={project.data_as_of} isStale={project.is_stale} />
        {project.status === "blocked" && <StatusChip label="Blocked - needs attention" tone="danger" />}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-lg border border-border bg-surface p-5 lg:col-span-2">
          <h2 className="mb-2 text-sm font-semibold text-text">Current next action</h2>
          <p className="text-sm text-text">
            {project.current_next_action || "No next action recorded."}
          </p>

          <h2 className="mb-2 mt-6 text-sm font-semibold text-text">Description</h2>
          <p className="text-sm text-muted-text">{project.description || "No description recorded."}</p>

          <h2 className="mb-2 mt-6 text-sm font-semibold text-text">Tech stack summary</h2>
          <p className="text-sm text-muted-text">
            {project.tech_stack_summary || "No tech stack summary recorded."}
          </p>

          <div className="mb-2 mt-6 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-text">Status evidence</h2>
            <Link
              to={`/projects/${project.id}/status-events/new`}
              className="rounded-md border border-border bg-surface px-2.5 py-1 text-xs font-medium text-text hover:bg-surface-muted"
            >
              Add status update
            </Link>
          </div>
          {statusEvents === null && <p className="text-sm text-muted-text">Loading status evidence…</p>}
          {statusEvents && statusEvents.length === 0 && (
            <p className="text-sm text-muted-text">
              No status updates recorded yet. Add one to establish this project's freshness.
            </p>
          )}
          {statusEvents && statusEvents.length > 0 && (
            <div className="space-y-3">
              {statusEvents.map((e) => (
                <StatusEventCard key={e.id} event={e} />
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="rounded-lg border border-border bg-surface p-5">
            <h2 className="mb-1 text-sm font-semibold text-text">Ownership</h2>
            <dl className="divide-y divide-border">
              <MetadataRow label="Owner" value={project.owner?.name ?? "Unassigned"} />
              <MetadataRow label="Business owner" value={project.business_owner || "—"} />
              <MetadataRow label="Project type" value={PROJECT_TYPE_LABELS[project.project_type]} />
              <MetadataRow label="Classification" value={CLASSIFICATION_LABELS[project.classification]} />
            </dl>
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <h2 className="mb-2 text-sm font-semibold text-text">Links</h2>
            <div className="flex flex-col gap-2">
              <EvidenceLink label="Repository" href={project.repo_url} />
              <EvidenceLink label="Environment" href={project.environment_url} />
              <EvidenceLink label="Documentation" href={project.docs_url} />
            </div>
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <h2 className="mb-1 text-sm font-semibold text-text">Record</h2>
            <dl className="divide-y divide-border">
              <MetadataRow label="Slug" value={project.slug} />
              <MetadataRow label="Created" value={new Date(project.created_at).toLocaleString()} />
              <MetadataRow label="Updated" value={new Date(project.updated_at).toLocaleString()} />
            </dl>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <DocumentationMatrix projectId={project.id} userEmail={email} />
      </div>
    </div>
  );
}
