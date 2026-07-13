import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { AISummaryPage } from "./pages/AISummaryPage";
import { PortfolioDashboard } from "./pages/PortfolioDashboard";
import { ProjectFormPage } from "./pages/ProjectFormPage";
import { ProjectProfile } from "./pages/ProjectProfile";
import { StarterPackPage } from "./pages/StarterPackPage";
import { StatusEventFormPage } from "./pages/StatusEventFormPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<PortfolioDashboard />} />
        <Route path="/projects/new" element={<ProjectFormPage mode="create" />} />
        <Route path="/projects/:id" element={<ProjectProfile />} />
        <Route path="/projects/:id/edit" element={<ProjectFormPage mode="edit" />} />
        <Route path="/projects/:id/status-events/new" element={<StatusEventFormPage />} />
        <Route path="/projects/:id/starter-pack" element={<StarterPackPage />} />
        <Route path="/projects/:id/ai-summary" element={<AISummaryPage />} />
      </Route>
    </Routes>
  );
}
