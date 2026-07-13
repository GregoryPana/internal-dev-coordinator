import { useEffect, useState } from "react";

// Portfolio dashboard and project profile land in T3 (docs/MVP_TASK_PLAN.md).
export default function App() {
  const [health, setHealth] = useState<string>("checking...");

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => setHealth(`${d.status} (${d.app}, ${d.env})`))
      .catch(() => setHealth("backend unreachable"));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", margin: "3rem auto", maxWidth: 720 }}>
      <h1>CWS Internal Development Coordinator</h1>
      <p>Internal development control plane — Phase 1 foundation.</p>
      <p>
        API health: <strong>{health}</strong>
      </p>
    </main>
  );
}
