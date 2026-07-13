import { Fragment, useEffect, useState } from "react";
import { ApiError, getDocumentationMatrix, upsertDocumentationArtifact } from "../lib/api";
import type { DocMatrixEntry } from "../lib/types";
import {
  ARTIFACT_STATUSES,
  ARTIFACT_STATUS_LABELS,
  ARTIFACT_STATUS_TONE,
  ARTIFACT_TYPE_LABELS,
  type ArtifactType,
} from "../lib/vocab";
import { StatusChip } from "./StatusChip";

interface EditState {
  title: string;
  status: string;
  source_path: string;
  notes: string;
}

function toEditState(entry: DocMatrixEntry): EditState {
  return {
    title: entry.title ?? "",
    status: entry.status,
    source_path: entry.source_path ?? "",
    notes: entry.notes ?? "",
  };
}

export function DocumentationMatrix({
  projectId,
  userEmail,
}: {
  projectId: number;
  userEmail: string;
}) {
  const [entries, setEntries] = useState<DocMatrixEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [editingType, setEditingType] = useState<ArtifactType | null>(null);
  const [editState, setEditState] = useState<EditState | null>(null);
  const [saving, setSaving] = useState(false);

  function load() {
    setError(null);
    getDocumentationMatrix(userEmail, projectId)
      .then(setEntries)
      .catch((e: ApiError) => setError(e.message));
  }

  useEffect(() => {
    setEntries(null);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userEmail, projectId]);

  function startEdit(entry: DocMatrixEntry) {
    setEditingType(entry.artifact_type);
    setEditState(toEditState(entry));
  }

  async function save(artifactType: ArtifactType) {
    if (!editState) return;
    setSaving(true);
    try {
      await upsertDocumentationArtifact(userEmail, projectId, artifactType, {
        title: editState.title || null,
        status: editState.status as DocMatrixEntry["status"],
        source_path: editState.source_path || null,
        owner_id: null,
        last_reviewed_at: null,
        notes: editState.notes || null,
      });
      setEditingType(null);
      setEditState(null);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not save this documentation artifact.");
    } finally {
      setSaving(false);
    }
  }

  if (error) {
    return (
      <div className="rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
        {error}
      </div>
    );
  }

  if (entries === null) {
    return <p className="text-sm text-muted-text">Loading documentation matrix…</p>;
  }

  const gapCount = entries.filter((e) => e.is_gap).length;

  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text">Documentation matrix</h2>
        {gapCount > 0 ? (
          <StatusChip label={`${gapCount} required doc${gapCount === 1 ? "" : "s"} missing`} tone="warning" />
        ) : (
          <StatusChip label="All required docs registered" tone="success" />
        )}
      </div>
      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full min-w-[640px] table-fixed text-left text-sm">
          <colgroup>
            <col className="w-40" />
            <col className="w-20" />
            <col className="w-28" />
            <col className="w-40" />
            <col className="w-24" />
          </colgroup>
          <thead className="bg-surface-muted text-xs uppercase tracking-wide text-muted-text">
            <tr>
              <th className="px-3 py-2 font-medium">Artifact</th>
              <th className="px-3 py-2 font-medium">Required</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium">Source</th>
              <th className="px-3 py-2 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {entries.map((entry) => (
              <Fragment key={entry.artifact_type}>
                <tr className="hover:bg-surface-muted/60">
                  <td className="truncate px-3 py-2 text-text">
                    {ARTIFACT_TYPE_LABELS[entry.artifact_type]}
                  </td>
                  <td className="px-3 py-2 text-muted-text">{entry.required ? "Required" : "Optional"}</td>
                  <td className="px-3 py-2">
                    <StatusChip
                      label={entry.is_gap ? "Gap" : ARTIFACT_STATUS_LABELS[entry.status]}
                      tone={entry.is_gap ? "danger" : ARTIFACT_STATUS_TONE[entry.status]}
                    />
                  </td>
                  <td className="truncate px-3 py-2">
                    {entry.source_path ? (
                      <span className="text-muted-text" title={entry.source_path}>
                        {entry.source_path}
                      </span>
                    ) : (
                      <span className="text-muted-text">not set</span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      onClick={() => startEdit(entry)}
                      className="rounded-md border border-border bg-surface px-2 py-1 text-xs font-medium text-text hover:bg-surface-muted"
                    >
                      {entry.status === "missing" ? "Register" : "Edit"}
                    </button>
                  </td>
                </tr>
                {editingType === entry.artifact_type && editState && (
                  <tr>
                    <td colSpan={5} className="bg-surface-muted px-3 py-4">
                      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <label className="flex flex-col gap-1 text-xs font-medium text-text">
                          Title
                          <input
                            value={editState.title}
                            onChange={(e) => setEditState({ ...editState, title: e.target.value })}
                            className="rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary"
                          />
                        </label>
                        <label className="flex flex-col gap-1 text-xs font-medium text-text">
                          Status
                          <select
                            value={editState.status}
                            onChange={(e) => setEditState({ ...editState, status: e.target.value })}
                            className="rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary"
                          >
                            {ARTIFACT_STATUSES.map((s) => (
                              <option key={s} value={s}>
                                {ARTIFACT_STATUS_LABELS[s]}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label className="flex flex-col gap-1 text-xs font-medium text-text sm:col-span-2">
                          Source path or link
                          <input
                            value={editState.source_path}
                            onChange={(e) => setEditState({ ...editState, source_path: e.target.value })}
                            placeholder="e.g. docs/AGENT_GUIDE.md"
                            className="rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary"
                          />
                        </label>
                        <label className="flex flex-col gap-1 text-xs font-medium text-text sm:col-span-2">
                          Notes
                          <textarea
                            value={editState.notes}
                            onChange={(e) => setEditState({ ...editState, notes: e.target.value })}
                            rows={2}
                            className="rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary"
                          />
                        </label>
                      </div>
                      <div className="mt-3 flex gap-2">
                        <button
                          type="button"
                          disabled={saving}
                          onClick={() => save(entry.artifact_type)}
                          className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
                        >
                          {saving ? "Saving…" : "Save"}
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setEditingType(null);
                            setEditState(null);
                          }}
                          className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-text hover:bg-surface-muted"
                        >
                          Cancel
                        </button>
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
