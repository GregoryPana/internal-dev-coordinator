"""Starter-pack AI tailoring (T8, FR-015). Enriches exactly one field -
the README's project overview paragraph - rather than rewriting all 11
generated files; keeps forbidden-data/validation risk small and the
output easy to check. Reliability NFR: if the provider is disabled (the
MVP default) or anything goes wrong, the deterministic files from T7 are
returned unchanged and no AIInteraction row is fabricated for a run that
never happened.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

from app.ai import forbidden_data
from app.ai.provider import ProviderUnavailableError, get_provider
from app.config import settings
from app.registry.models import Project
from app.starterpack.schemas import GeneratedFile, IntakeForm
from app.vocab import AITaskType, ErrorCategory, HumanReviewStatus, ValidationStatus

_PROMPT_PATH = Path(__file__).parent / "prompts" / "starter_pack_tailoring__v1.md"
_PROMPT_ID = "starter_pack_tailoring"
_PROMPT_VERSION = 1


@dataclass
class AIInteractionInput:
    task_type: AITaskType
    prompt_id: str
    prompt_version: int
    source_ids_json: dict
    input_bundle_hash: str
    model_provider: str
    model_name: str
    validation_status: ValidationStatus
    human_review_status: HumanReviewStatus
    output_text: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    error_category: ErrorCategory | None = None
    estimated_cost: float | None = None


@dataclass
class TailoringOutcome:
    files: list[GeneratedFile]
    interaction: AIInteractionInput | None  # None = no AI run was attempted


def _load_prompt_template() -> str:
    text = _PROMPT_PATH.read_text(encoding="utf-8")
    # strip the --- frontmatter block
    parts = text.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else text


def _bundle_hash(project: Project, intake: IntakeForm) -> str:
    payload = json.dumps(
        {"project_id": project.id, "intake": intake.model_dump()}, sort_keys=True, default=str
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _build_prompt(project: Project, intake: IntakeForm) -> str:
    template = _load_prompt_template()
    return template.format(
        project_name=project.name,
        project_type=project.project_type.value,
        classification=project.classification.value,
        users=intake.users,
        workflow=intake.workflow,
        data_sensitivity=intake.data_sensitivity,
        integrations=intake.integrations or "None recorded.",
    )


def _replace_readme_overview(files: list[GeneratedFile], overview: str) -> list[GeneratedFile]:
    updated = []
    for f in files:
        if f.path == "README.md":
            # The deterministic README (app.starterpack.service._readme) is:
            # "# {name}\n\n{overview}\n\n## What this is\n...". Line index 2 is the overview.
            lines = f.content.split("\n")
            lines[2] = overview
            updated.append(GeneratedFile(path=f.path, content="\n".join(lines)))
        else:
            updated.append(f)
    return updated


def tailor_starter_pack(project: Project, intake: IntakeForm, files: list[GeneratedFile]) -> TailoringOutcome:
    if settings.ai_provider == "disabled":
        return TailoringOutcome(files=files, interaction=None)

    bundle_hash = _bundle_hash(project, intake)
    source_ids = {"project_id": project.id}

    input_texts = {"intake": json.dumps(intake.model_dump())}
    findings = forbidden_data.scan_many(input_texts)
    if findings:
        return TailoringOutcome(
            files=files,
            interaction=AIInteractionInput(
                task_type=AITaskType.STARTER_PACK_TAILORING,
                prompt_id=_PROMPT_ID,
                prompt_version=_PROMPT_VERSION,
                source_ids_json=source_ids,
                input_bundle_hash=bundle_hash,
                model_provider=settings.ai_provider,
                model_name=settings.ai_model,
                validation_status=ValidationStatus.FAILED_FORBIDDEN_DATA,
                human_review_status=HumanReviewStatus.REJECTED,
                error_category=ErrorCategory.FORBIDDEN_DATA_DETECTED,
            ),
        )

    prompt = _build_prompt(project, intake)
    start = time.monotonic()
    try:
        provider = get_provider()
        result = provider.complete(prompt)
    except ProviderUnavailableError:
        return TailoringOutcome(
            files=files,
            interaction=AIInteractionInput(
                task_type=AITaskType.STARTER_PACK_TAILORING,
                prompt_id=_PROMPT_ID,
                prompt_version=_PROMPT_VERSION,
                source_ids_json=source_ids,
                input_bundle_hash=bundle_hash,
                model_provider=settings.ai_provider,
                model_name=settings.ai_model,
                validation_status=ValidationStatus.FAILED_SCHEMA,
                human_review_status=HumanReviewStatus.REJECTED,
                error_category=ErrorCategory.PROVIDER_UNAVAILABLE,
                latency_ms=int((time.monotonic() - start) * 1000),
            ),
        )
    latency_ms = int((time.monotonic() - start) * 1000)

    if not result.text.strip():
        return TailoringOutcome(
            files=files,
            interaction=AIInteractionInput(
                task_type=AITaskType.STARTER_PACK_TAILORING,
                prompt_id=_PROMPT_ID,
                prompt_version=_PROMPT_VERSION,
                source_ids_json=source_ids,
                input_bundle_hash=bundle_hash,
                model_provider=settings.ai_provider,
                model_name=result.model_name,
                validation_status=ValidationStatus.FAILED_SCHEMA,
                human_review_status=HumanReviewStatus.REJECTED,
                error_category=ErrorCategory.MALFORMED_OUTPUT,
                latency_ms=latency_ms,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
            ),
        )

    output_findings = forbidden_data.scan(result.text)
    if output_findings:
        return TailoringOutcome(
            files=files,
            interaction=AIInteractionInput(
                task_type=AITaskType.STARTER_PACK_TAILORING,
                prompt_id=_PROMPT_ID,
                prompt_version=_PROMPT_VERSION,
                source_ids_json=source_ids,
                input_bundle_hash=bundle_hash,
                model_provider=settings.ai_provider,
                model_name=result.model_name,
                validation_status=ValidationStatus.FAILED_FORBIDDEN_DATA,
                human_review_status=HumanReviewStatus.REJECTED,
                error_category=ErrorCategory.FORBIDDEN_DATA_DETECTED,
                latency_ms=latency_ms,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
            ),
        )

    tailored_files = _replace_readme_overview(files, result.text.strip())
    return TailoringOutcome(
        files=tailored_files,
        interaction=AIInteractionInput(
            task_type=AITaskType.STARTER_PACK_TAILORING,
            prompt_id=_PROMPT_ID,
            prompt_version=_PROMPT_VERSION,
            source_ids_json=source_ids,
            input_bundle_hash=bundle_hash,
            model_provider=settings.ai_provider,
            model_name=result.model_name,
            validation_status=ValidationStatus.PASSED,
            human_review_status=HumanReviewStatus.GENERATED,
            output_text=result.text.strip(),
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=latency_ms,
        ),
    )
