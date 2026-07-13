"""Documentation matrix business logic: deterministic gap computation.

No AI involved (T5 is explicitly out of the AI boundary - see AGENTS.md).
A row is a "gap" if it is required by the project's project_type and no
documentation_artifacts row exists yet, or the existing row's status is
still 'missing'.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.docs_matrix.models import DocumentationArtifact, RequiredDocProfile
from app.docs_matrix.schemas import DocumentationArtifactUpsert, DocumentationMatrixEntry
from app.registry.models import Project
from app.vocab import ArtifactStatus, ArtifactType


def _required_map(db: Session, project_type) -> dict[ArtifactType, RequiredDocProfile]:
    stmt = select(RequiredDocProfile).where(RequiredDocProfile.project_type == project_type)
    return {p.artifact_type: p for p in db.scalars(stmt)}


def get_matrix(db: Session, project: Project) -> list[DocumentationMatrixEntry]:
    required_map = _required_map(db, project.project_type)
    artifacts = {
        a.artifact_type: a
        for a in db.scalars(
            select(DocumentationArtifact).where(DocumentationArtifact.project_id == project.id)
        )
    }

    entries = []
    for artifact_type in ArtifactType:
        profile = required_map.get(artifact_type)
        required = profile.required if profile else False
        artifact = artifacts.get(artifact_type)
        status = artifact.status if artifact else ArtifactStatus.MISSING
        entries.append(
            DocumentationMatrixEntry(
                artifact_type=artifact_type,
                required=required,
                status=status,
                is_gap=required and status == ArtifactStatus.MISSING,
                title=artifact.title if artifact else None,
                source_path=artifact.source_path if artifact else None,
                owner=artifact.owner if artifact else None,
                last_reviewed_at=artifact.last_reviewed_at if artifact else None,
                staleness_checked_at=artifact.staleness_checked_at if artifact else None,
                notes=artifact.notes if artifact else None,
            )
        )
    return entries


def upsert_artifact(
    db: Session, project: Project, artifact_type: ArtifactType, data: DocumentationArtifactUpsert
) -> tuple[DocumentationArtifact, bool]:
    required_map = _required_map(db, project.project_type)
    required = artifact_type in required_map and required_map[artifact_type].required

    artifact = db.scalar(
        select(DocumentationArtifact).where(
            DocumentationArtifact.project_id == project.id,
            DocumentationArtifact.artifact_type == artifact_type,
        )
    )
    created = artifact is None
    if artifact is None:
        artifact = DocumentationArtifact(project_id=project.id, artifact_type=artifact_type, required=required)
        db.add(artifact)

    artifact.required = required
    for field, value in data.model_dump().items():
        setattr(artifact, field, value)

    db.flush()
    return artifact, created
