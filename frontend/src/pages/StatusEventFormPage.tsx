import { useState, type FormEvent, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { ApiError, createStatusEvent } from "../lib/api";
import type { StatusEventFormValues } from "../lib/types";
import { useCurrentUser } from "../state/currentUser";

const EMPTY_FORM: StatusEventFormValues = {
  event_date: new Date().toISOString().slice(0, 10),
  summary: "",
  completed_work: "",
  next_actions: "",
  blockers: "",
  verification_notes: "",
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

export function StatusEventFormPage() {
  const { id } = useParams();
  const projectId = Number(id);
  const { email } = useCurrentUser();
  const navigate = useNavigate();
  const [form, setForm] = useState<StatusEventFormValues>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function set<K extends keyof StatusEventFormValues>(key: K, value: StatusEventFormValues[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createStatusEvent(email, projectId, {
        event_date: form.event_date,
        summary: form.summary,
        completed_work: form.completed_work || null,
        next_actions: form.next_actions || null,
        blockers: form.blockers || null,
        verification_notes: form.verification_notes || null,
      });
      navigate(`/projects/${projectId}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <PageHeader
        title="Add status update"
        subtitle="Factual, dated evidence: what happened, what's next, and what's blocking progress."
      />

      {error && (
        <div className="mb-4 rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-6 rounded-lg border border-border bg-surface p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Event date" htmlFor="event_date" optional={false}>
            <input
              id="event_date"
              type="date"
              required
              value={form.event_date}
              onChange={(e) => set("event_date", e.target.value)}
              className={inputClass}
            />
          </Field>
        </div>

        <Field label="Summary" htmlFor="summary" optional={false}>
          <textarea
            id="summary"
            required
            value={form.summary}
            onChange={(e) => set("summary", e.target.value)}
            rows={2}
            placeholder="One or two sentences describing this update."
            className={inputClass}
          />
        </Field>

        <Field label="Completed work" htmlFor="completed_work">
          <textarea
            id="completed_work"
            value={form.completed_work}
            onChange={(e) => set("completed_work", e.target.value)}
            rows={3}
            className={inputClass}
          />
        </Field>

        <Field label="Next actions" htmlFor="next_actions">
          <textarea
            id="next_actions"
            value={form.next_actions}
            onChange={(e) => set("next_actions", e.target.value)}
            rows={2}
            className={inputClass}
          />
        </Field>

        <Field label="Blockers" htmlFor="blockers">
          <textarea
            id="blockers"
            value={form.blockers}
            onChange={(e) => set("blockers", e.target.value)}
            rows={2}
            placeholder="Leave blank if nothing is blocking this project."
            className={inputClass}
          />
        </Field>

        <Field label="Verification notes" htmlFor="verification_notes">
          <textarea
            id="verification_notes"
            value={form.verification_notes}
            onChange={(e) => set("verification_notes", e.target.value)}
            rows={2}
            placeholder="How was this work verified before recording it here?"
            className={inputClass}
          />
        </Field>

        <div className="flex items-center gap-3 border-t border-border pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
          >
            {submitting ? "Saving…" : "Add update"}
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
