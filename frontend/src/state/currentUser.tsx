import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

// Dev auth is a login stub only (see AGENTS.md / app.authz): identity comes
// from the X-User-Email header. This context lets the shell surface who the
// browser is "logged in" as, and switch it while no real login flow exists.
const DEFAULT_USER_EMAIL = "gregory.panagary@cwseychelles.com";
const STORAGE_KEY = "idc.currentUserEmail";

interface CurrentUserContextValue {
  email: string;
  setEmail: (email: string) => void;
}

const CurrentUserContext = createContext<CurrentUserContextValue | null>(null);

export function CurrentUserProvider({ children }: { children: ReactNode }) {
  const [email, setEmailState] = useState<string>(
    () => localStorage.getItem(STORAGE_KEY) || DEFAULT_USER_EMAIL
  );

  const setEmail = (next: string) => {
    setEmailState(next);
    localStorage.setItem(STORAGE_KEY, next);
  };

  const value = useMemo(() => ({ email, setEmail }), [email]);

  return <CurrentUserContext.Provider value={value}>{children}</CurrentUserContext.Provider>;
}

export function useCurrentUser(): CurrentUserContextValue {
  const ctx = useContext(CurrentUserContext);
  if (!ctx) throw new Error("useCurrentUser must be used within CurrentUserProvider");
  return ctx;
}
