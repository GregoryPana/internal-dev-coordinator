import { useState, type FormEvent, type ReactNode } from "react";
import { useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import {
  ApiError,
  exportStarterPack,
  generateStarterPack,
  generateStarterPackPreview,
  reviewStarterPack,
} from "../lib/api";
import type { GeneratedFile, IntakeFormValues, StarterPack } from "../lib/types";
import { HUMAN_REVIEW_STATUS_LABELS, HUMAN_REVIEW_STATUS_TONE } from "../lib/vocab";
import { useCurrentUser } from "../state/currentUser";

const EMPTY_INTAKE: IntakeFormValues = {
  users: "",
  workflow: "",
  data_sensitivity: "",
  integrations: "",
  deployment_target: "",
  notes: "",
};

function Field({
  label,
  htmlFor,
  children,
  optional = false,
}: {
  label: string;
  htmlFor: string;
  children: ReactNode;
  optional?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={htmlFor} className="text-sm font-medium text-text">
        {label} {optional && <span className="font-normal text-muted-text">(optional)</span>}
      </label>
      {children}
    </div>
  );
}

const inputClass =
  "rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary";

export function StarterPackPage() {
  const { id } = useParams();
  const projectId = Number(id);
  const { email } = useCurrentUser();
  const [intake, setIntake] = useState<IntakeFormValues>(EMPTY_INTAKE);
  const [files, setFiles] = useState<GeneratedFile[] | null>(null);
  const [pack, setPack] = useState<StarterPack | null>(null);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<"preview" | "generate" | "review" | "export" | null>(null);

  function set<K extends keyof IntakeFormValues>(key: K, value: IntakeFormValues[K]) {
    setIntake((f) => ({ ...f, [key]: value }));
  }

  async function onPreview(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy("preview");
    try {
      const preview = await generateStarterPackPreview(email, projectId, intake);
      setPack(null);
      setFiles(preview.files);
      setSelectedPath(preview.files[0]?.path ?? null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not generate the starter pack preview.");
    } finally {
      setBusy(null);
    }
  }

  async function onGenerate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy("generate");
    try {
      const created = await generateStarterPack(email, projectId, intake);
      setPack(created);
      setFiles(created.files);
      setSelectedPath(created.files[0]?.path ?? null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not generate the starter pack.");
    } finally {
      setBusy(null);
    }
  }

  async function onReview(decision: "reviewed" | "rejected") {
    if (!pack) return;
    setError(null);
    setBusy("review");
    try {
      const updated = await reviewStarterPack(email, projectId, pack.id, decision);
      setPack(updated);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not record the review decision.");
    } finally {
      setBusy(null);
    }
  }

  async function onExport() {
    if (!pack) return;
    setError(null);
    setBusy("export");
    try {
      const blob = await exportStarterPack(email, projectId, pack.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "starter-pack.zip";
      a.click();
      URL.revokeObjectURL(url);
      setPack({ ...pack, status: "exported" });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not export the starter pack.");
    } finally {
      setBusy(null);
    }
  }

  const selectedFile = files?.find((f) => f.path === selectedPath) ?? null;

  return (
    <div>
      <PageHeader
        title="Starter pack"
        subtitle="Internal Dev Kit starter files (FR-016), generated from this project's fields and a short intake, optionally AI-tailored. Draft output - always reviewed before export (FR-017)."
      />

      {error && (
        <div className="mb-4 rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      <form onSubmit={onGenerate} className="mb-6 space-y-4 rounded-lg border border-border bg-surface p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Who will use this" htmlFor="users">
            <input
              id="users"
              required
              value={intake.users}
              onChange={(e) => set("users", e.target.value)}
              placeholder="e.g. Ops staff, P&C admins"
              className={inputClass}
            />
          </Field>
          <Field label="Deployment target" htmlFor="deployment_target">
            <input
              id="deployment_target"
              required
              value={intake.deployment_target}
              onChange={(e) => set("deployment_target", e.target.value)}
              placeholder="e.g. Internal VM"
              className={inputClass}
            />
          </Field>
        </div>

        <Field label="Core workflow being digitalised" htmlFor="workflow">
          <textarea
            id="workflow"
            required
            value={intake.workflow}
            onChange={(e) => set("workflow", e.target.value)}
            rows={2}
            className={inputClass}
          />
        </Field>

        <Field label="Data sensitivity" htmlFor="data_sensitivity">
          <textarea
            id="data_sensitivity"
            required
            value={intake.data_sensitivity}
            onChange={(e) => set("data_sensitivity", e.target.value)}
            rows={2}
            placeholder="What kind of data this handles, if any."
            className={inputClass}
          />
        </Field>

        <Field label="Integrations" htmlFor="integrations" optional>
          <input
            id="integrations"
            value={intake.integrations}
            onChange={(e) => set("integrations", e.target.value)}
            placeholder="Other systems this needs to talk to"
            className={inputClass}
          />
        </Field>

        <Field label="Notes" htmlFor="notes" optional>
          <textarea
            id="notes"
            value={intake.notes}
            onChange={(e) => set("notes", e.target.value)}
            rows={2}
            className={inputClass}
          />
        </Field>

        <div className="flex items-center gap-3 border-t border-border pt-4">
          <button
            type="button"
            onClick={onPreview}
            disabled={busy !== null}
            className="rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-text hover:bg-surface-muted disabled:opacity-60"
          >
            {busy === "preview" ? "Generating…" : "Quick preview"}
          </button>
          <button
            type="submit"
            disabled={busy !== null}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
          >
            {busy === "generate" ? "Generating…" : "Generate for review"}
          </button>
        </div>
      </form>

      {pack && (
        <div className="mb-6 flex flex-wrap items-center gap-3 rounded-lg border border-border bg-surface p-4">
          <span className="text-sm font-medium text-text">Starter pack #{pack.id}</span>
          <StatusChip label={HUMAN_REVIEW_STATUS_LABELS[pack.status]} tone={HUMAN_REVIEW_STATUS_TONE[pack.status]} />
          {pack.reviewer && (
            <span className="text-sm text-muted-text">Reviewed by {pack.reviewer.name}</span>
          )}
          <div className="ml-auto flex gap-2">
            {pack.status === "generated" && (
              <>
                <button
                  type="button"
                  onClick={() => onReview("reviewed")}
                  disabled={busy !== null}
                  className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
                >
                  Approve
                </button>
                <button
                  type="button"
                  onClick={() => onReview("rejected")}
                  disabled={busy !== null}
                  className="rounded-md border border-danger-border bg-surface px-3 py-1.5 text-sm font-medium text-danger hover:bg-danger-bg disabled:opacity-60"
                >
                  Reject
                </button>
              </>
            )}
            {pack.status === "reviewed" && (
              <button
                type="button"
                onClick={onExport}
                disabled={busy !== null}
                className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
              >
                {busy === "export" ? "Exporting…" : "Export as zip"}
              </button>
            )}
          </div>
        </div>
      )}

      {files && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
          <div className="rounded-lg border border-border bg-surface p-3 lg:col-span-1">
            <h2 className="mb-2 px-1 text-xs font-semibold uppercase tracking-wide text-muted-text">
              Generated files ({files.length})
            </h2>
            <ul className="space-y-0.5">
              {files.map((f) => (
                <li key={f.path}>
                  <button
                    type="button"
                    onClick={() => setSelectedPath(f.path)}
                    className={`w-full truncate rounded-md px-2 py-1.5 text-left text-sm ${
                      selectedPath === f.path
                        ? "bg-primary/10 font-medium text-primary"
                        : "text-text hover:bg-surface-muted"
                    }`}
                  >
                    {f.path}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg border border-border bg-surface p-5 lg:col-span-3">
            {selectedFile && (
              <>
                <h2 className="mb-3 text-sm font-semibold text-text">{selectedFile.path}</h2>
                <pre className="max-h-[600px] overflow-auto whitespace-pre-wrap rounded-md bg-surface-muted p-4 text-xs text-text">
                  {selectedFile.content}
                </pre>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
