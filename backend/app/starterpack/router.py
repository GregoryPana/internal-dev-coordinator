"""Starter-pack API: stateless deterministic preview (T7) plus persisted
generation, review and zip export (T8).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.authz import service as authz
from app.db import get_db
from app.registry import service as registry_service
from app.registry.models import Person
from app.starterpack.schemas import (
    GeneratedFile,
    IntakeForm,
    ReviewDecision,
    StarterPackPreview,
    StarterPackRead,
)
from app.starterpack.service import build_preview, export_pack, generate_pack, get_pack, review_pack
from app.vocab import AuditActionType, AuditObjectType, HumanReviewStatus

router = APIRouter(prefix="/api/projects/{project_id}/starter-pack", tags=["starter-pack"])


def _get_project_or_404(db: Session, project_id: int):
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


def _to_read(pack) -> StarterPackRead:
    return StarterPackRead(
        id=pack.id,
        project_id=pack.project_id,
        intake=IntakeForm.model_validate(pack.intake_json),
        files=[GeneratedFile.model_validate(f) for f in pack.generated_files_json],
        status=pack.status,
        reviewer=pack.reviewer,
        export_path=pack.export_path,
        created_at=pack.created_at,
    )


@router.post("/preview", response_model=StarterPackPreview)
def generate_preview(
    project_id: int,
    intake: IntakeForm,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> StarterPackPreview:
    project = _get_project_or_404(db, project_id)
    authz.require_update(db, user, project)

    files = build_preview(project, intake)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.STARTER_PACK_GENERATED,
        object_type=AuditObjectType.STARTER_PACK,
        object_id=None,
        project_id=project.id,
        metadata={"file_count": len(files), "deployment_target": intake.deployment_target, "preview_only": True},
    )
    db.commit()
    return StarterPackPreview(project_id=project.id, files=files)


@router.post("/generate", response_model=StarterPackRead, status_code=status.HTTP_201_CREATED)
def generate(
    project_id: int,
    intake: IntakeForm,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> StarterPackRead:
    project = _get_project_or_404(db, project_id)
    authz.require_update(db, user, project)

    try:
        pack, ai_attempted = generate_pack(db, project, intake)
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e)) from e

    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.STARTER_PACK_GENERATED,
        object_type=AuditObjectType.STARTER_PACK,
        object_id=pack.id,
        project_id=project.id,
        metadata={"file_count": len(pack.generated_files_json), "ai_tailoring_attempted": ai_attempted},
    )
    db.commit()
    db.refresh(pack)
    return _to_read(pack)


@router.get("/{pack_id}", response_model=StarterPackRead)
def get_starter_pack(
    project_id: int,
    pack_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> StarterPackRead:
    project = _get_project_or_404(db, project_id)
    authz.require_read(db, user, project)
    pack = get_pack(db, project_id, pack_id)
    if pack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Starter pack not found.")
    return _to_read(pack)


@router.post("/{pack_id}/review", response_model=StarterPackRead)
def review(
    project_id: int,
    pack_id: int,
    data: ReviewDecision,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> StarterPackRead:
    project = _get_project_or_404(db, project_id)
    authz.require_update(db, user, project)
    pack = get_pack(db, project_id, pack_id)
    if pack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Starter pack not found.")
    if pack.status != HumanReviewStatus.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Starter pack is '{pack.status.value}', not awaiting review.",
        )

    pack = review_pack(db, pack, user.id, HumanReviewStatus(data.decision))
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.STARTER_PACK_REVIEWED,
        object_type=AuditObjectType.STARTER_PACK,
        object_id=pack.id,
        project_id=project.id,
        metadata={"decision": data.decision.value},
    )
    db.commit()
    db.refresh(pack)
    return _to_read(pack)


@router.get("/{pack_id}/export")
def export(
    project_id: int,
    pack_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> FileResponse:
    project = _get_project_or_404(db, project_id)
    authz.require_update(db, user, project)
    pack = get_pack(db, project_id, pack_id)
    if pack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Starter pack not found.")
    if pack.status != HumanReviewStatus.REVIEWED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Starter pack must be reviewed before export.",
        )

    zip_path = export_pack(db, pack)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.STARTER_PACK_EXPORTED,
        object_type=AuditObjectType.STARTER_PACK,
        object_id=pack.id,
        project_id=project.id,
        metadata={"export_path": str(zip_path)},
    )
    db.commit()
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{project.slug}-starter-pack.zip",
    )
