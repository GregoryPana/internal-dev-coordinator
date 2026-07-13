"""Documentation matrix API: deterministic required-doc gap list per project."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.authz import service as authz
from app.db import get_db
from app.docs_matrix import service as docs_service
from app.docs_matrix.schemas import DocumentationArtifactUpsert, DocumentationMatrixEntry
from app.registry import service as registry_service
from app.registry.models import Person
from app.vocab import ArtifactType, AuditActionType, AuditObjectType

router = APIRouter(prefix="/api/projects/{project_id}/documentation", tags=["documentation-matrix"])


def _get_project_or_404(db: Session, project_id: int):
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.get("", response_model=list[DocumentationMatrixEntry])
def get_documentation_matrix(
    project_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> list[DocumentationMatrixEntry]:
    project = _get_project_or_404(db, project_id)
    authz.require_read(db, user, project)
    return docs_service.get_matrix(db, project)


@router.put("/{artifact_type}", response_model=DocumentationMatrixEntry)
def upsert_documentation_artifact(
    project_id: int,
    artifact_type: ArtifactType,
    data: DocumentationArtifactUpsert,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> DocumentationMatrixEntry:
    project = _get_project_or_404(db, project_id)
    authz.require_update(db, user, project)
    artifact, created = docs_service.upsert_artifact(db, project, artifact_type, data)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.DOC_ARTIFACT_CREATED if created else AuditActionType.DOC_ARTIFACT_UPDATED,
        object_type=AuditObjectType.DOCUMENTATION_ARTIFACT,
        object_id=artifact.id,
        project_id=project.id,
        metadata={"artifact_type": artifact_type.value, "status": data.status.value},
    )
    db.commit()
    matrix = docs_service.get_matrix(db, project)
    return next(e for e in matrix if e.artifact_type == artifact_type)
