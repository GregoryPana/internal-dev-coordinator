import { useEffect, useState, type FormEvent } from "react";
import { PageHeader } from "../components/PageHeader";
import { StatusChip } from "../components/StatusChip";
import {
  ApiError,
  getIntegrations,
  testGitHubIntegration,
  updateGitHubIntegration,
} from "../lib/api";
import type { GitHubIntegrationStatus, IntegrationTestResult } from "../lib/types";
import { useCurrentUser } from "../state/currentUser";

const inputClass =
  "rounded-md border border-border bg-surface px-3 py-2 text-sm text-text focus-visible:ring-2 focus-visible:ring-primary";

/** Guided integration setup (2026-07-14 direction): the app states exactly
 * what is needed, shows how to fetch it, and accepts/edits it in place.
 * Credentials are stored encrypted server-side and never come back out. */
export function SettingsPage() {
  const { email } = useCurrentUser();
  const [status, setStatus] = useState<GitHubIntegrationStatus | null>(null);
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
      })
      .catch((e: ApiError) => setError({ status: e.status, message: e.message }));
  }, [email]);

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
        <h2 className="mb-1 text-sm font-semibold text-text">AI provider (OpenRouter)</h2>
        <p className="text-sm text-muted-text">
          Currently configured via <code className="rounded bg-surface-muted px-1 py-0.5 text-xs">backend/.env</code>{" "}
          (IDC_AI_PROVIDER / IDC_AI_MODEL / IDC_AI_API_KEY). In-app management for the AI provider
          follows the same pattern as GitHub above and is planned next.
        </p>
      </div>
    </div>
  );
}
