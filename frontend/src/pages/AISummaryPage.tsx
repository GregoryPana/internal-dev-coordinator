import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import { ApiError, generateSummary, listAIInteractions, listSummaries, reviewSummary } from "../lib/api";
import type { AIInteraction } from "../lib/types";
import {
  AI_AUDIENCES,
  AI_AUDIENCE_LABELS,
  HUMAN_REVIEW_STATUS_LABELS,
  HUMAN_REVIEW_STATUS_TONE,
  VALIDATION_STATUS_LABELS,
  type AIAudience,
} from "../lib/vocab";
import { useCurrentUser } from "../state/currentUser";

/** T10 human evaluation (2026-07-14) found the model's confidence field
 * uncalibrated (0.0 on the strongest output) - render as a muted footnote,
 * never as a bar or reliability indicator. */
function ConfidenceNote({ confidence }: { confidence: number }) {
  return (
    <p className="mt-1 text-xs text-muted-text">
      Model self-reported confidence: {confidence} (uncalibrated — not a reliability indicator)
    </p>
  );
}

function SummaryCard({
  interaction,
  onReview,
  busy,
}: {
  interaction: AIInteraction;
  onReview: (decision: "reviewed" | "rejected") => void;
  busy: boolean;
}) {
  const output = interaction.output_json;
  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <StatusChip label={AI_AUDIENCE_LABELS[interaction.audience ?? "developer"]} tone="neutral" />
        <StatusChip
          label={HUMAN_REVIEW_STATUS_LABELS[interaction.human_review_status]}
          tone={HUMAN_REVIEW_STATUS_TONE[interaction.human_review_status]}
        />
        {interaction.validation_status !== "passed" && (
          <StatusChip label={VALIDATION_STATUS_LABELS[interaction.validation_status]} tone="danger" />
        )}
        <span className="ml-auto text-xs text-muted-text">
          {new Date(interaction.created_at).toLocaleString()} · {interaction.model_provider}/
          {interaction.model_name}
        </span>
      </div>

      {output ? (
        <>
          <p className="text-sm text-text">{output.summary}</p>
          <ConfidenceNote confidence={output.confidence} />

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {output.gaps.length > 0 && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-text">
                  Gaps
                </h3>
                <ul className="list-inside list-disc text-sm text-muted-text">
                  {output.gaps.map((g, i) => (
                    <li key={i}>{g}</li>
                  ))}
                </ul>
              </div>
            )}
            {output.recommended_next_actions.length > 0 && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-text">
                  Recommended next actions
                </h3>
                <ul className="list-inside list-disc text-sm text-muted-text">
                  {output.recommended_next_actions.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </div>
            )}
            {output.assumptions.length > 0 && (
              <div className="sm:col-span-2">
                <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-text">
                  Uncertainties (no conclusions drawn)
                </h3>
                <ul className="list-inside list-disc text-sm text-muted-text">
                  {output.assumptions.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <p className="mt-4 text-xs text-muted-text">
            Draft AI output - not official until reviewed. Source: {interaction.prompt_id} v
            {interaction.prompt_version}.
          </p>
        </>
      ) : (
        <p className="text-sm text-danger">
          This attempt did not produce usable output ({interaction.error_category ?? "unknown error"}).
          You can generate a new summary above.
        </p>
      )}

      {interaction.human_review_status === "generated" && (
        <div className="mt-4 flex gap-2 border-t border-border pt-4">
          <button
            type="button"
            disabled={busy}
            onClick={() => onReview("reviewed")}
            className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
          >
            Approve
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => onReview("rejected")}
            className="rounded-md border border-danger-border bg-surface px-3 py-1.5 text-sm font-medium text-danger hover:bg-danger-bg disabled:opacity-60"
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
}

export function AISummaryPage() {
  const { id } = useParams();
  const projectId = Number(id);
  const { email } = useCurrentUser();
  const [audience, setAudience] = useState<AIAudience>("developer");
  const [summaries, setSummaries] = useState<AIInteraction[] | null>(null);
  const [interactions, setInteractions] = useState<AIInteraction[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [reviewingId, setReviewingId] = useState<number | null>(null);

  function load() {
    listSummaries(email, projectId)
      .then(setSummaries)
      .catch((e: ApiError) => setError(e.message));
    listAIInteractions(email, projectId)
      .then(setInteractions)
      .catch(() => setInteractions(null));
  }

  useEffect(() => {
    setSummaries(null);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [email, projectId]);

  async function onGenerate() {
    setError(null);
    setGenerating(true);
    try {
      await generateSummary(email, projectId, audience);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not generate the summary.");
    } finally {
      setGenerating(false);
    }
  }

  async function onReview(interactionId: number, decision: "reviewed" | "rejected") {
    setError(null);
    setReviewingId(interactionId);
    try {
      await reviewSummary(email, projectId, interactionId, decision);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not record the review decision.");
    } finally {
      setReviewingId(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="AI summary"
        subtitle="Audience-parameterised project summary generated from structured fields, status events and the documentation matrix. Always a draft - never official until reviewed (FR-022)."
      />

      {error && (
        <div className="mb-4 rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      <div className="mb-6 flex flex-wrap items-center gap-3 rounded-lg border border-border bg-surface p-4">
        <label htmlFor="audience" className="text-sm font-medium text-text">
          Audience
        </label>
        <select
          id="audience"
          value={audience}
          onChange={(e) => setAudience(e.target.value as AIAudience)}
          className="rounded-md border border-border bg-surface px-3 py-1.5 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary"
        >
          {AI_AUDIENCES.map((a) => (
            <option key={a} value={a}>
              {AI_AUDIENCE_LABELS[a]}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={onGenerate}
          disabled={generating}
          className="ml-auto rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
        >
          {generating ? "Generating…" : "Generate summary"}
        </button>
      </div>

      {summaries === null && <p className="text-sm text-muted-text">Loading summaries…</p>}
      {summaries && summaries.length === 0 && (
        <p className="text-sm text-muted-text">No summaries generated yet.</p>
      )}
      {summaries && summaries.length > 0 && (
        <div className="space-y-4">
          {summaries.map((s) => (
            <SummaryCard
              key={s.id}
              interaction={s}
              busy={reviewingId === s.id}
              onReview={(decision) => onReview(s.id, decision)}
            />
          ))}
        </div>
      )}

      {interactions && interactions.length > 0 && (
        <div className="mt-8">
          <h2 className="mb-2 text-sm font-semibold text-text">AI activity log</h2>
          <p className="mb-3 text-xs text-muted-text">
            Every AI run against this project, all task types (FR-022). Full detail is stored in
            the AIInteraction record.
          </p>
          <div className="hidden overflow-x-auto rounded-md border border-border md:block">
            <table className="w-full min-w-[720px] table-fixed text-left text-sm">
              <colgroup>
                <col className="w-40" />
                <col className="w-40" />
                <col className="w-24" />
                <col className="w-48" />
                <col className="w-36" />
                <col className="w-32" />
                <col className="w-28" />
              </colgroup>
              <thead className="bg-surface-muted text-xs uppercase tracking-wide text-muted-text">
                <tr>
                  <th className="px-3 py-2 font-medium">When</th>
                  <th className="px-3 py-2 font-medium">Task</th>
                  <th className="px-3 py-2 font-medium">Audience</th>
                  <th className="px-3 py-2 font-medium">Model</th>
                  <th className="px-3 py-2 font-medium">Validation</th>
                  <th className="px-3 py-2 font-medium">Review</th>
                  <th className="px-3 py-2 font-medium">Tokens</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-surface">
                {interactions.map((run) => (
                  <tr key={run.id} className="hover:bg-surface-muted/60">
                    <td className="truncate px-3 py-2 text-muted-text" title={run.created_at}>
                      {new Date(run.created_at).toLocaleString()}
                    </td>
                    <td className="truncate px-3 py-2 text-text">{run.task_type.replace(/_/g, " ")}</td>
                    <td className="px-3 py-2 text-muted-text">
                      {run.audience ? AI_AUDIENCE_LABELS[run.audience] : "—"}
                    </td>
                    <td
                      className="truncate px-3 py-2 text-muted-text"
                      title={`${run.model_provider}/${run.model_name}`}
                    >
                      {run.model_provider}/{run.model_name}
                    </td>
                    <td className="px-3 py-2">
                      <StatusChip
                        label={VALIDATION_STATUS_LABELS[run.validation_status]}
                        tone={run.validation_status === "passed" ? "success" : "danger"}
                      />
                    </td>
                    <td className="px-3 py-2">
                      <StatusChip
                        label={HUMAN_REVIEW_STATUS_LABELS[run.human_review_status]}
                        tone={HUMAN_REVIEW_STATUS_TONE[run.human_review_status]}
                      />
                    </td>
                    <td className="px-3 py-2 text-muted-text">
                      {run.input_tokens != null && run.output_tokens != null
                        ? `${run.input_tokens} / ${run.output_tokens}`
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-3 md:hidden">
            {interactions.map((run) => (
              <div key={run.id} className="rounded-md border border-border p-3">
                <div className="mb-2 flex items-start justify-between gap-2">
                  <span className="text-sm font-medium text-text">{run.task_type.replace(/_/g, " ")}</span>
                  <span className="text-xs text-muted-text" title={run.created_at}>
                    {new Date(run.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="mb-2 flex flex-wrap gap-2">
                  <StatusChip
                    label={VALIDATION_STATUS_LABELS[run.validation_status]}
                    tone={run.validation_status === "passed" ? "success" : "danger"}
                  />
                  <StatusChip
                    label={HUMAN_REVIEW_STATUS_LABELS[run.human_review_status]}
                    tone={HUMAN_REVIEW_STATUS_TONE[run.human_review_status]}
                  />
                </div>
                <dl className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Audience</dt>
                    <dd className="text-muted-text">
                      {run.audience ? AI_AUDIENCE_LABELS[run.audience] : "—"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Model</dt>
                    <dd className="truncate text-muted-text" title={`${run.model_provider}/${run.model_name}`}>
                      {run.model_provider}/{run.model_name}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-text">Tokens</dt>
                    <dd className="tabular-nums text-muted-text">
                      {run.input_tokens != null && run.output_tokens != null
                        ? `${run.input_tokens} / ${run.output_tokens}`
                        : "—"}
                    </dd>
                  </div>
                </dl>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
