import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useCurrentUser } from "../state/currentUser";

export function AppShell() {
  const { email, setEmail } = useCurrentUser();
  const [environment, setEnvironment] = useState<string>("");
  const [draftEmail, setDraftEmail] = useState(email);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => setEnvironment(d.env))
      .catch(() => setEnvironment("unreachable"));
  }, []);

  useEffect(() => setDraftEmail(email), [email]);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-surface">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3">
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold tracking-tight text-text">
              Internal Dev Coordinator
            </span>
            {environment && environment !== "production" && (
              <span className="rounded-md border border-border bg-surface-muted px-2 py-0.5 text-xs font-medium capitalize text-muted-text">
                {environment}
              </span>
            )}
            <nav className="ml-4 flex gap-1">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `rounded-md px-3 py-1.5 text-sm font-medium ${
                    isActive ? "bg-primary/10 text-primary" : "text-muted-text hover:text-text"
                  }`
                }
              >
                Portfolio
              </NavLink>
              <NavLink
                to="/audit"
                className={({ isActive }) =>
                  `rounded-md px-3 py-1.5 text-sm font-medium ${
                    isActive ? "bg-primary/10 text-primary" : "text-muted-text hover:text-text"
                  }`
                }
              >
                Audit
              </NavLink>
              <NavLink
                to="/settings"
                className={({ isActive }) =>
                  `rounded-md px-3 py-1.5 text-sm font-medium ${
                    isActive ? "bg-primary/10 text-primary" : "text-muted-text hover:text-text"
                  }`
                }
              >
                Settings
              </NavLink>
            </nav>
          </div>
          <form
            className="flex items-center gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              setEmail(draftEmail.trim());
            }}
            title="Dev auth stub - sets the X-User-Email header (app.authz enforces real permissions)"
          >
            <label htmlFor="dev-user" className="text-xs text-muted-text">
              Signed in as
            </label>
            <input
              id="dev-user"
              type="email"
              value={draftEmail}
              onChange={(e) => setDraftEmail(e.target.value)}
              onBlur={() => setEmail(draftEmail.trim())}
              className="w-56 rounded-md border border-border bg-surface px-2 py-1 text-xs text-text focus-visible:ring-2 focus-visible:ring-primary"
            />
          </form>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
