"""AI project-summary API (T9): audience-parameterised, source-cited,
human-reviewed. app.authz gates every project before app.ai.source_bundle
ever sees it, so AI can never see data the requesting user could not."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.models import AIInteraction
from app.ai.schemas import AIInteractionRead, GenerateSummaryRequest, ReviewDecision
from app.ai.summary_service import generate_summary
from app.audit import service as audit_service
from app.authz import service as authz
from app.db import get_db
from app.registry import service as registry_service
from app.registry.models import Person
from app.vocab import AITaskType, AuditActionType, AuditObjectType, HumanReviewStatus

router = APIRouter(prefix="/api/projects/{project_id}/ai", tags=["ai-summary"])


def _get_project_or_404(db: Session, project_id: int):
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


def _get_interaction_or_404(db: Session, project_id: int, interaction_id: int) -> AIInteraction:
    interaction = db.get(AIInteraction, interaction_id)
    if (
        interaction is None
        or interaction.project_id != project_id
        or interaction.task_type != AITaskType.PROJECT_SUMMARY
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found.")
    return interaction


@router.post("/summary", response_model=AIInteractionRead, status_code=status.HTTP_201_CREATED)
def generate(
    project_id: int,
    data: GenerateSummaryRequest,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> AIInteractionRead:
    project = _get_project_or_404(db, project_id)
    authz.require_read(db, user, project)

    result = generate_summary(db, project, data.audience)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.AI_RUN_CREATED,
        object_type=AuditObjectType.AI_INTERACTION,
        object_id=result.interaction.id,
        project_id=project.id,
        metadata={
            "audience": data.audience.value,
            "validation_status": result.interaction.validation_status.value,
        },
    )
    db.commit()
    db.refresh(result.interaction)
    return AIInteractionRead.model_validate(result.interaction)


@router.get("/summaries", response_model=list[AIInteractionRead])
def list_summaries(
    project_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> list[AIInteractionRead]:
    project = _get_project_or_404(db, project_id)
    authz.require_read(db, user, project)

    stmt = (
        select(AIInteraction)
        .where(AIInteraction.project_id == project_id, AIInteraction.task_type == AITaskType.PROJECT_SUMMARY)
        .order_by(AIInteraction.created_at.desc())
    )
    return [AIInteractionRead.model_validate(i) for i in db.scalars(stmt)]


@router.get("/interactions", response_model=list[AIInteractionRead])
def list_interactions(
    project_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> list[AIInteractionRead]:
    """Every AI run against this project, all task types (FR-022: every AI
    interaction is logged and visible, not just project summaries)."""
    project = _get_project_or_404(db, project_id)
    authz.require_read(db, user, project)

    stmt = (
        select(AIInteraction)
        .where(AIInteraction.project_id == project_id)
        .order_by(AIInteraction.created_at.desc())
    )
    return [AIInteractionRead.model_validate(i) for i in db.scalars(stmt)]


@router.post("/summaries/{interaction_id}/review", response_model=AIInteractionRead)
def review(
    project_id: int,
    interaction_id: int,
    data: ReviewDecision,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> AIInteractionRead:
    project = _get_project_or_404(db, project_id)
    authz.require_update(db, user, project)
    interaction = _get_interaction_or_404(db, project_id, interaction_id)
    if interaction.human_review_status != HumanReviewStatus.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Summary is '{interaction.human_review_status.value}', not awaiting review.",
        )

    interaction.human_review_status = HumanReviewStatus(data.decision)
    db.flush()
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.AI_OUTPUT_REVIEWED,
        object_type=AuditObjectType.AI_INTERACTION,
        object_id=interaction.id,
        project_id=project.id,
        metadata={"decision": data.decision.value},
    )
    db.commit()
    db.refresh(interaction)
    return AIInteractionRead.model_validate(interaction)
