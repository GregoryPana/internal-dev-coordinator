import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { ApiError, createProject, getAppConfig, getProject, updateProject } from "../lib/api";
import type { ProjectFormValues } from "../lib/types";
import {
  CLASSIFICATIONS,
  CLASSIFICATION_LABELS,
  PRIORITIES,
  PRIORITY_LABELS,
  PROJECT_PHASES,
  PROJECT_PHASE_LABELS,
  PROJECT_STATUSES,
  PROJECT_STATUS_LABELS,
  PROJECT_TYPES,
  PROJECT_TYPE_LABELS,
} from "../lib/vocab";
import { useCurrentUser } from "../state/currentUser";

const EMPTY_FORM: ProjectFormValues = {
  name: "",
  description: "",
  business_purpose: "",
  project_type: "internal-web-app",
  classification: "one-off",
  phase: "concept",
  status: "active",
  priority: "medium",
  business_owner: "",
  current_next_action: "",
  repo_url: "",
  environment_url: "",
  docs_url: "",
  tech_stack_summary: "",
  date_commenced: null,
  expected_finish_date: null,
  percent_complete: null,
  uses_process_automation: false,
  uses_ai: false,
};

function Field({
  label,
  htmlFor,
  children,
  optional = true,
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

export function ProjectFormPage({ mode }: { mode: "create" | "edit" }) {
  const { id } = useParams();
  const { email } = useCurrentUser();
  const navigate = useNavigate();
  const [form, setForm] = useState<ProjectFormValues>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(mode === "edit");
  const [edition, setEdition] = useState<"custom" | "product">("product");

  useEffect(() => {
    getAppConfig().then((c) => setEdition(c.edition)).catch(() => {});
  }, []);

  useEffect(() => {
    if (mode !== "edit" || !id) return;
    getProject(email, Number(id))
      .then((p) =>
        setForm({
          name: p.name,
          description: p.description ?? "",
          business_purpose: p.business_purpose ?? "",
          project_type: p.project_type,
          classification: p.classification,
          phase: p.phase,
          status: p.status,
          priority: p.priority,
          business_owner: p.business_owner ?? "",
          current_next_action: p.current_next_action ?? "",
          repo_url: p.repo_url ?? "",
          environment_url: p.environment_url ?? "",
          docs_url: p.docs_url ?? "",
          tech_stack_summary: p.tech_stack_summary ?? "",
          date_commenced: p.date_commenced,
          expected_finish_date: p.expected_finish_date,
          percent_complete: p.percent_complete,
          uses_process_automation: p.uses_process_automation,
          uses_ai: p.uses_ai,
        })
      )
      .catch((e: ApiError) => setError(e.message))
      .finally(() => setLoading(false));
  }, [mode, id, email]);

  function set<K extends keyof ProjectFormValues>(key: K, value: ProjectFormValues[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const project =
        mode === "create" ? await createProject(email, form) : await updateProject(email, Number(id), form);
      navigate(`/projects/${project.id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <div className="text-sm text-muted-text">Loading project…</div>;
  }

  return (
    <div className="max-w-3xl">
      <PageHeader
        title={mode === "create" ? "New project" : "Edit project"}
        subtitle={
          mode === "create"
            ? "Add a project to the registry. A URL slug is generated from the name."
            : "Update project registry fields. Changes are recorded in the audit trail."
        }
      />

      {error && (
        <div className="mb-4 rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-6 rounded-lg border border-border bg-surface p-6">
        <Field label="Name" htmlFor="name" optional={false}>
          <input
            id="name"
            required
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
            placeholder="e.g. Health Fair Portal"
            className={inputClass}
          />
        </Field>

        <Field label="Business purpose" htmlFor="business_purpose">
          <textarea
            id="business_purpose"
            value={form.business_purpose ?? ""}
            onChange={(e) => set("business_purpose", e.target.value)}
            placeholder="Why this project exists, in one or two sentences."
            rows={2}
            className={inputClass}
          />
        </Field>

        <Field label="Description" htmlFor="description">
          <textarea
            id="description"
            value={form.description ?? ""}
            onChange={(e) => set("description", e.target.value)}
            rows={3}
            className={inputClass}
          />
        </Field>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Project type" htmlFor="project_type" optional={false}>
            <select
              id="project_type"
              value={form.project_type}
              onChange={(e) => set("project_type", e.target.value as ProjectFormValues["project_type"])}
              className={inputClass}
            >
              {PROJECT_TYPES.map((v) => (
                <option key={v} value={v}>
                  {PROJECT_TYPE_LABELS[v]}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Classification" htmlFor="classification" optional={false}>
            <select
              id="classification"
              value={form.classification}
              onChange={(e) => set("classification", e.target.value as ProjectFormValues["classification"])}
              className={inputClass}
            >
              {CLASSIFICATIONS.map((v) => (
                <option key={v} value={v}>
                  {CLASSIFICATION_LABELS[v]}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Phase" htmlFor="phase" optional={false}>
            <select
              id="phase"
              value={form.phase}
              onChange={(e) => set("phase", e.target.value as ProjectFormValues["phase"])}
              className={inputClass}
            >
              {PROJECT_PHASES.map((v) => (
                <option key={v} value={v}>
                  {PROJECT_PHASE_LABELS[v]}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Status" htmlFor="status" optional={false}>
            <select
              id="status"
              value={form.status}
              onChange={(e) => set("status", e.target.value as ProjectFormValues["status"])}
              className={inputClass}
            >
              {PROJECT_STATUSES.map((v) => (
                <option key={v} value={v}>
                  {PROJECT_STATUS_LABELS[v]}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Priority" htmlFor="priority" optional={false}>
            <select
              id="priority"
              value={form.priority}
              onChange={(e) => set("priority", e.target.value as ProjectFormValues["priority"])}
              className={inputClass}
            >
              {PRIORITIES.map((v) => (
                <option key={v} value={v}>
                  {PRIORITY_LABELS[v]}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Business owner" htmlFor="business_owner">
            <input
              id="business_owner"
              value={form.business_owner ?? ""}
              onChange={(e) => set("business_owner", e.target.value)}
              placeholder="Name of the accountable business stakeholder"
              className={inputClass}
            />
          </Field>
        </div>

        <Field label="Current next action" htmlFor="current_next_action">
          <textarea
            id="current_next_action"
            value={form.current_next_action ?? ""}
            onChange={(e) => set("current_next_action", e.target.value)}
            rows={2}
            placeholder="What happens next, and who owns it."
            className={inputClass}
          />
        </Field>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Field label="Repository link" htmlFor="repo_url">
            <input
              id="repo_url"
              value={form.repo_url ?? ""}
              onChange={(e) => set("repo_url", e.target.value)}
              placeholder="https://github.com/…"
              className={inputClass}
            />
          </Field>
          <Field label="Environment link" htmlFor="environment_url">
            <input
              id="environment_url"
              value={form.environment_url ?? ""}
              onChange={(e) => set("environment_url", e.target.value)}
              placeholder="https://…"
              className={inputClass}
            />
          </Field>
          <Field label="Docs link" htmlFor="docs_url">
            <input
              id="docs_url"
              value={form.docs_url ?? ""}
              onChange={(e) => set("docs_url", e.target.value)}
              placeholder="https://…"
              className={inputClass}
            />
          </Field>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Field label="Date commenced" htmlFor="date_commenced">
            <input
              id="date_commenced"
              type="date"
              value={form.date_commenced ?? ""}
              onChange={(e) => set("date_commenced", e.target.value || null)}
              className={inputClass}
            />
          </Field>
          <Field label="Expected finish date" htmlFor="expected_finish_date">
            <input
              id="expected_finish_date"
              type="date"
              value={form.expected_finish_date ?? ""}
              onChange={(e) => set("expected_finish_date", e.target.value || null)}
              className={inputClass}
            />
          </Field>
          <Field label="Completion (%)" htmlFor="percent_complete">
            <input
              id="percent_complete"
              type="number"
              min={0}
              max={100}
              value={form.percent_complete ?? ""}
              onChange={(e) =>
                set("percent_complete", e.target.value === "" ? null : Number(e.target.value))
              }
              placeholder="0–100"
              className={inputClass}
            />
          </Field>
        </div>

        {edition === "custom" && (
          <div className="rounded-md border border-border bg-surface-muted p-4">
            <p className="mb-3 text-xs font-medium uppercase tracking-wide text-muted-text">
              Portfolio metrics
            </p>
            <div className="flex flex-wrap gap-6">
              <label className="flex items-center gap-2 text-sm text-text">
                <input
                  type="checkbox"
                  checked={form.uses_process_automation}
                  onChange={(e) => set("uses_process_automation", e.target.checked)}
                  className="rounded border-border text-primary focus-visible:ring-2 focus-visible:ring-primary"
                />
                Enables process automation
              </label>
              <label className="flex items-center gap-2 text-sm text-text">
                <input
                  type="checkbox"
                  checked={form.uses_ai}
                  onChange={(e) => set("uses_ai", e.target.checked)}
                  className="rounded border-border text-primary focus-visible:ring-2 focus-visible:ring-primary"
                />
                Implements or uses AI
              </label>
            </div>
          </div>
        )}

        <Field label="Tech stack summary" htmlFor="tech_stack_summary">
          <textarea
            id="tech_stack_summary"
            value={form.tech_stack_summary ?? ""}
            onChange={(e) => set("tech_stack_summary", e.target.value)}
            rows={2}
            placeholder="e.g. FastAPI + PostgreSQL + React/Vite"
            className={inputClass}
          />
        </Field>

        <div className="flex items-center gap-3 border-t border-border pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
          >
            {submitting ? "Saving…" : mode === "create" ? "Create project" : "Save changes"}
          </button>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-text hover:bg-surface-muted"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
