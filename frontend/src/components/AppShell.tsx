import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useCurrentUser } from "../state/currentUser";

const NAV_ITEMS = [
  { to: "/", label: "Portfolio", end: true, icon: PortfolioIcon },
  { to: "/audit", label: "Audit", end: false, icon: AuditIcon },
  { to: "/settings", label: "Settings", end: false, icon: SettingsIcon },
] as const;

function PortfolioIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M4 6a2 2 0 0 1 2-2h3l1.5 2H18a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function AuditIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M8 4h8a1 1 0 0 1 1 1v14l-4-2-4 2V5a1 1 0 0 1 1-1Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M9 9h6M9 12h6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.7" />
      <path
        d="M12 3v2m0 14v2m9-9h-2M5 12H3m14.95-6.36-1.42 1.42M7.47 16.94l-1.42 1.42m0-12.72 1.42 1.42m9.06 9.06 1.42 1.42"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  );
}

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
        <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3 sm:px-8 lg:px-10 xl:px-16">
          <div className="flex min-w-0 items-center gap-3">
            <span className="truncate text-sm font-semibold tracking-tight text-text">
              Internal Dev Coordinator
            </span>
            {environment && environment !== "production" && (
              <span className="shrink-0 rounded-md border border-border bg-surface-muted px-2 py-0.5 text-xs font-medium capitalize text-muted-text">
                {environment}
              </span>
            )}
            <nav className="ml-2 hidden gap-1 md:flex">
              {NAV_ITEMS.map(({ to, label, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    `rounded-md px-3 py-1.5 text-sm font-medium ${
                      isActive ? "bg-primary/10 text-primary" : "text-muted-text hover:text-text"
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
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
            <label htmlFor="dev-user" className="hidden text-xs text-muted-text sm:inline">
              Signed in as
            </label>
            <input
              id="dev-user"
              type="email"
              value={draftEmail}
              onChange={(e) => setDraftEmail(e.target.value)}
              onBlur={() => setEmail(draftEmail.trim())}
              className="w-40 min-w-0 rounded-md border border-border bg-surface px-2 py-1 text-xs text-text focus-visible:ring-2 focus-visible:ring-primary sm:w-56"
            />
          </form>
        </div>
      </header>

      <main className="px-5 py-6 pb-24 sm:px-8 sm:py-8 lg:px-10 xl:px-16 md:pb-8">
        <Outlet />
      </main>

      <nav
        aria-label="Primary"
        className="fixed inset-x-0 bottom-0 z-20 flex gap-1 border-t border-border bg-surface px-2 md:hidden"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        {NAV_ITEMS.map(({ to, label, end, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center gap-0.5 py-2 text-xs font-medium ${
                isActive ? "text-primary" : "text-muted-text"
              }`
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
