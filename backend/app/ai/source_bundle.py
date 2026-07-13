"""Source-bundle builder (FR-018, architecture spec 11.2): structured DB
fields only, no RAG. The caller MUST have already run this project through
app.authz (require_read) before calling build() - this module does not
re-check permissions itself, it only ever sees one already-authorized
project, so AI can never see data the requesting user could not already
view directly.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.docs_matrix.service import get_matrix
from app.registry.models import Project
from app.registry.service import is_stale as project_is_stale
from app.status.service import list_status_events_for_project

_MAX_STATUS_EVENTS = 5


@dataclass
class SourceBundle:
    text: str
    source_ids: dict


def _project_section(project: Project) -> str:
    return (
        f"Project: {project.name} ({project.slug})\n"
        f"Type: {project.project_type.value} | Classification: {project.classification.value}\n"
        f"Phase: {project.phase.value} | Status: {project.status.value} | Priority: {project.priority.value}\n"
        f"Owner: {project.owner.name if project.owner else 'Unassigned'}\n"
        f"Business owner: {project.business_owner or 'Not recorded'}\n"
        f"Business purpose: {project.business_purpose or 'Not recorded'}\n"
        f"Description: {project.description or 'Not recorded'}\n"
        f"Current next action: {project.current_next_action or 'Not recorded'}\n"
        f"Tech stack summary: {project.tech_stack_summary or 'Not recorded'}\n"
        f"Data as of: {project.data_as_of.isoformat() if project.data_as_of else 'No status evidence yet'}\n"
        f"Stale (>14 days old or no evidence): {project_is_stale(project.data_as_of)}\n"
    )


def _status_events_section(db: Session, project: Project) -> tuple[str, list[int]]:
    events = list_status_events_for_project(db, project.id)[:_MAX_STATUS_EVENTS]
    if not events:
        return "No status events recorded.\n", []

    lines = []
    for e in events:
        lines.append(
            f"- [{e.id}] {e.event_date.isoformat()} by {e.author.name}: {e.summary}\n"
            f"  completed_work: {e.completed_work or 'none recorded'}\n"
            f"  next_actions: {e.next_actions or 'none recorded'}\n"
            f"  blockers: {e.blockers or 'none'}\n"
        )
    return "".join(lines), [e.id for e in events]


def _docs_matrix_section(db: Session, project: Project) -> tuple[str, list[str]]:
    entries = get_matrix(db, project)
    required = [e for e in entries if e.required]
    if not required:
        return "No documentation is required for this project type.\n", []

    lines = []
    for e in required:
        gap_marker = " (GAP - missing)" if e.is_gap else ""
        lines.append(f"- {e.artifact_type.value}: {e.status.value}{gap_marker}\n")
    return "".join(lines), [e.artifact_type.value for e in required]


def build(db: Session, project: Project) -> SourceBundle:
    status_text, status_ids = _status_events_section(db, project)
    docs_text, docs_types = _docs_matrix_section(db, project)

    text = (
        f"{_project_section(project)}\n"
        f"Recent status events (newest first, max {_MAX_STATUS_EVENTS}):\n{status_text}\n"
        f"Required documentation status:\n{docs_text}"
    )
    source_ids = {
        "project_id": project.id,
        "status_event_ids": status_ids,
        "required_artifact_types": docs_types,
    }
    return SourceBundle(text=text, source_ids=source_ids)
