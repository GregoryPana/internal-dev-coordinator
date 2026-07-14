import { useEffect, useState, type FormEvent } from "react";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import {
  ApiError,
  getIntegrations,
  testAIIntegration,
  testGitHubIntegration,
  updateAIIntegration,
  updateGitHubIntegration,
} from "../lib/api";
import type {
  AIIntegrationStatus,
  GitHubIntegrationStatus,
  IntegrationTestResult,
} from "../lib/types";
import { useCurrentUser } from "../state/currentUser";

const inputClass =
  "rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary";

/** Guided integration setup (2026-07-14 direction): the app states exactly
 * what is needed, shows how to fetch it, and accepts/edits it in place.
 * Credentials are stored encrypted server-side and never come back out. */
export function SettingsPage() {
  const { email } = useCurrentUser();
  const [status, setStatus] = useState<GitHubIntegrationStatus | null>(null);
  const [aiStatus, setAIStatus] = useState<AIIntegrationStatus | null>(null);
  const [aiEnabled, setAIEnabled] = useState(false);
  const [aiModel, setAIModel] = useState("");
  const [aiKey, setAIKey] = useState("");
  const [aiSaving, setAISaving] = useState(false);
  const [aiSaved, setAISaved] = useState(false);
  const [aiTesting, setAITesting] = useState(false);
  const [aiTestResult, setAITestResult] = useState<IntegrationTestResult | null>(null);
  const [error, setError] = useState<{ status: number; message: string } | null>(null);
  const [enabled, setEnabled] = useState(false);
  const [token, setToken] = useState("");
  const [clearToken, setClearToken] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<IntegrationTestResult | null>(null);

  useEffect(() => {
    setStatus(null);
    setError(null);
    setTestResult(null);
    getIntegrations(email)
      .then((d) => {
        setStatus(d.github);
        setEnabled(d.github.enabled);
        setAIStatus(d.ai);
        setAIEnabled(d.ai.enabled);
        setAIModel(d.ai.model);
      })
      .catch((e: ApiError) => setError({ status: e.status, message: e.message }));
  }, [email]);

  async function onSaveAI(e: FormEvent) {
    e.preventDefault();
    setAISaving(true);
    setAISaved(false);
    setError(null);
    setAITestResult(null);
    try {
      const payload: { enabled: boolean; model?: string | null; api_key?: string | null } = {
        enabled: aiEnabled,
        model: aiModel,
      };
      if (aiKey.trim()) payload.api_key = aiKey.trim();
      const d = await updateAIIntegration(email, payload);
      setAIStatus(d.ai);
      setAIEnabled(d.ai.enabled);
      setAIModel(d.ai.model);
      setAIKey("");
      setAISaved(true);
    } catch (err) {
      setError({
        status: err instanceof ApiError ? err.status : 0,
        message: err instanceof ApiError ? err.message : "Could not save AI settings.",
      });
    } finally {
      setAISaving(false);
    }
  }

  async function onTestAI() {
    setAITesting(true);
    setAITestResult(null);
    try {
      setAITestResult(await testAIIntegration(email));
    } catch (err) {
      setAITestResult({
        ok: false,
        detail: err instanceof ApiError ? err.message : "Test failed.",
      });
    } finally {
      setAITesting(false);
    }
  }

  async function onSave(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    setError(null);
    setTestResult(null);
    try {
      const payload: { enabled: boolean; token?: string | null } = { enabled };
      if (clearToken) payload.token = "";
      else if (token.trim()) payload.token = token.trim();
      const d = await updateGitHubIntegration(email, payload);
      setStatus(d.github);
      setEnabled(d.github.enabled);
      setToken("");
      setClearToken(false);
      setSaved(true);
    } catch (err) {
      setError({
        status: err instanceof ApiError ? err.status : 0,
        message: err instanceof ApiError ? err.message : "Could not save settings.",
      });
    } finally {
      setSaving(false);
    }
  }

  async function onTest() {
    setTesting(true);
    setTestResult(null);
    setError(null);
    try {
      setTestResult(await testGitHubIntegration(email));
    } catch (err) {
      setTestResult({
        ok: false,
        detail: err instanceof ApiError ? err.message : "Test failed.",
      });
    } finally {
      setTesting(false);
    }
  }

  if (error && error.status === 403) {
    return (
      <div>
        <PageHeader title="Settings" subtitle="Integration configuration." />
        <div className="rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          Integration settings require the admin role. Switch to an admin user to manage them.
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Settings"
        subtitle="Connect and manage external integrations. Credentials are encrypted at rest and never displayed again after saving."
      />

      {error && (
        <div className="mb-4 rounded-md border border-danger-border bg-danger-bg px-4 py-3 text-sm text-danger">
          {error.message}
        </div>
      )}

      <div className="rounded-lg border border-border bg-surface p-6">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-semibold text-text">GitHub (read-only repo tracking)</h2>
          {status && (
            <>
              <StatusChip
                label={status.enabled ? "Enabled" : "Disabled"}
                tone={status.enabled ? "success" : "neutral"}
              />
              <StatusChip
                label={status.credential_set ? "Token stored" : "No token"}
                tone={status.credential_set ? "success" : "warning"}
              />
              <span className="text-xs text-muted-text">
                configured via {status.source === "app" ? "this page" : "environment file"}
              </span>
            </>
          )}
        </div>
        <p className="mb-4 text-sm text-muted-text">
          Powers the repository-activity card on project profiles and the background tracking
          poller. Strictly read-only — the platform never writes to any repository.
        </p>

        {status && !status.secret_key_configured && (
          <div className="mb-4 rounded-md border border-warning-border bg-warning-bg px-4 py-3 text-sm text-text">
            <span className="font-medium">Credential storage is locked:</span> IDC_SECRET_KEY is
            not set on the server. Generate one with{" "}
            <code className="rounded bg-surface-muted px-1 py-0.5 text-xs">
              python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
            </code>{" "}
            and add it to <code className="rounded bg-surface-muted px-1 py-0.5 text-xs">backend/.env</code>,
            then restart the backend.
          </div>
        )}

        <div className="mb-5 rounded-md border border-border bg-surface-muted p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-text">
            What you need & how to get it
          </p>
          <ol className="list-inside list-decimal space-y-1 text-sm text-text">
            <li>
              A <span className="font-medium">fine-grained personal access token</span>: GitHub →
              Settings → Developer settings →{" "}
              <a
                href="https://github.com/settings/personal-access-tokens/new"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline"
              >
                Personal access tokens (fine-grained) → Generate new token
              </a>
              .
            </li>
            <li>
              <span className="font-medium">Repository access</span>: "Only select repositories" —
              pick the repos your projects link to.
            </li>
            <li>
              <span className="font-medium">Permissions</span>: Repository permissions →{" "}
              <span className="font-medium">Contents: Read-only</span> and{" "}
              <span className="font-medium">Metadata: Read-only</span>. Nothing else.
            </li>
            <li>Set an expiry you can live with, generate, and paste the token below.</li>
          </ol>
          <p className="mt-2 text-xs text-muted-text">
            Public repositories work without a token (at a much lower rate limit); private
            repositories require one.
          </p>
        </div>

        <form onSubmit={onSave} className="space-y-4">
          <label className="flex items-center gap-2 text-sm text-text">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
              className="rounded border-border text-primary focus-visible:ring-2 focus-visible:ring-primary"
            />
            Enable GitHub repo tracking
          </label>

          <div className="flex flex-col gap-1">
            <label htmlFor="gh-token" className="text-sm font-medium text-text">
              Personal access token{" "}
              <span className="font-normal text-muted-text">
                ({status?.credential_set ? "leave blank to keep the stored token" : "paste to store"})
              </span>
            </label>
            <input
              id="gh-token"
              type="password"
              value={token}
              onChange={(e) => {
                setToken(e.target.value);
                if (e.target.value) setClearToken(false);
              }}
              placeholder="github_pat_…"
              autoComplete="off"
              disabled={clearToken}
              className={inputClass}
            />
            {status?.credential_set && (
              <label className="mt-1 flex items-center gap-2 text-xs text-muted-text">
                <input
                  type="checkbox"
                  checked={clearToken}
                  onChange={(e) => setClearToken(e.target.checked)}
                  className="rounded border-border text-primary"
                />
                Remove the stored token
              </label>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">
            <button
              type="submit"
              disabled={saving}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
            >
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              onClick={onTest}
              disabled={testing}
              className="rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-text hover:bg-surface-muted disabled:opacity-60"
            >
              {testing ? "Testing…" : "Test connection"}
            </button>
            {saved && <span className="text-sm text-success">Saved.</span>}
          </div>
        </form>

        {testResult && (
          <div
            className={`mt-4 rounded-md border px-4 py-3 text-sm ${
              testResult.ok
                ? "border-success-border bg-success-bg text-text"
                : "border-danger-border bg-danger-bg text-danger"
            }`}
          >
            {testResult.detail}
          </div>
        )}
      </div>

      <div className="mt-6 rounded-lg border border-border bg-surface p-6">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <h2 className="text-sm font-semibold text-text">AI provider (OpenRouter)</h2>
          {aiStatus && (
            <>
              <StatusChip
                label={aiStatus.enabled ? "Enabled" : "Disabled"}
                tone={aiStatus.enabled ? "success" : "neutral"}
              />
              <StatusChip
                label={aiStatus.credential_set ? "Key stored" : "No key"}
                tone={aiStatus.credential_set ? "success" : "warning"}
              />
              <span className="text-xs text-muted-text">
                configured via {aiStatus.source === "app" ? "this page" : "environment file"}
              </span>
            </>
          )}
        </div>
        <p className="mb-4 text-sm text-muted-text">
          Powers starter-pack README tailoring and project summaries. All output stays draft
          until human-reviewed (FR-022).
        </p>

        <div className="mb-5 rounded-md border border-border bg-surface-muted p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-text">
            What you need & how to get it
          </p>
          <ol className="list-inside list-decimal space-y-1 text-sm text-text">
            <li>
              An OpenRouter API key:{" "}
              <a
                href="https://openrouter.ai/keys"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline"
              >
                openrouter.ai/keys
              </a>{" "}
              → Create key, then paste it below.
            </li>
            <li>
              A model ID. Free-tier models come and go — check{" "}
              <a
                href="https://openrouter.ai/models?max_price=0"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline"
              >
                the live free-model list
              </a>{" "}
              if generations start failing, and use "Test connection" here to confirm.
            </li>
          </ol>
        </div>

        <form onSubmit={onSaveAI} className="space-y-4">
          <label className="flex items-center gap-2 text-sm text-text">
            <input
              type="checkbox"
              checked={aiEnabled}
              onChange={(e) => setAIEnabled(e.target.checked)}
              className="rounded border-border text-primary focus-visible:ring-2 focus-visible:ring-primary"
            />
            Enable AI tailoring & summaries
          </label>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-1">
              <label htmlFor="ai-model" className="text-sm font-medium text-text">
                Model
              </label>
              <input
                id="ai-model"
                value={aiModel}
                onChange={(e) => setAIModel(e.target.value)}
                placeholder="nvidia/nemotron-nano-9b-v2:free"
                className={inputClass}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label htmlFor="ai-key" className="text-sm font-medium text-text">
                API key{" "}
                <span className="font-normal text-muted-text">
                  ({aiStatus?.credential_set ? "leave blank to keep stored" : "paste to store"})
                </span>
              </label>
              <input
                id="ai-key"
                type="password"
                value={aiKey}
                onChange={(e) => setAIKey(e.target.value)}
                placeholder="sk-or-…"
                autoComplete="off"
                className={inputClass}
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">
            <button
              type="submit"
              disabled={aiSaving}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-fg hover:bg-primary-hover disabled:opacity-60"
            >
              {aiSaving ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              onClick={onTestAI}
              disabled={aiTesting}
              className="rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-text hover:bg-surface-muted disabled:opacity-60"
            >
              {aiTesting ? "Testing… (can take ~30s)" : "Test connection"}
            </button>
            {aiSaved && <span className="text-sm text-success">Saved.</span>}
          </div>
        </form>

        {aiTestResult && (
          <div
            className={`mt-4 rounded-md border px-4 py-3 text-sm ${
              aiTestResult.ok
                ? "border-success-border bg-success-bg text-text"
                : "border-danger-border bg-danger-bg text-danger"
            }`}
          >
            {aiTestResult.detail}
          </div>
        )}
      </div>
    </div>
  );
}
