"""Audience-parameterised AI project summary (T9, FR-018-FR-023).

Unlike starter-pack tailoring (T8), there is no deterministic fallback
here - a summary is inherently an AI output. If the provider is
unavailable or the output fails validation, no summary is returned, but
an AIInteraction row is still persisted for every attempted run (FR-024)
so failures are auditable, not silent.
"""

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai import forbidden_data
from app.ai.models import AIInteraction
from app.ai.provider import ProviderUnavailableError, get_provider
from app.ai.schemas import SummaryOutput
from app.ai.source_bundle import build as build_source_bundle
from app.config import settings
from app.registry.models import Project
from app.registry.service import is_stale as project_is_stale
from app.vocab import AIAudience, AITaskType, ErrorCategory, HumanReviewStatus, ValidationStatus

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_PROMPT_VERSION = 1
_STALE_CAVEAT = (
    "This project's data_as_of is stale (older than the 14-day freshness threshold, or no "
    "status evidence exists yet) - treat this summary as potentially outdated."
)


@dataclass
class SummaryGenerationResult:
    interaction: AIInteraction
    output: SummaryOutput | None


def _prompt_id(audience: AIAudience) -> str:
    return f"project_summary__{audience.value}"


def _load_prompt_template(audience: AIAudience) -> str:
    path = _PROMPTS_DIR / f"project_summary__{audience.value}__v{_PROMPT_VERSION}.md"
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else text


def _strip_code_fences(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else text


def _enforce_stale_caveat(output: SummaryOutput, project: Project) -> SummaryOutput:
    if project_is_stale(project.data_as_of) and not any("stale" in g.lower() for g in output.gaps):
        output.gaps = [*output.gaps, _STALE_CAVEAT]
    return output


def _record(
    db: Session,
    project: Project,
    audience: AIAudience,
    source_ids: dict,
    bundle_hash: str,
    **fields,
) -> AIInteraction:
    interaction = AIInteraction(
        project_id=project.id,
        task_type=AITaskType.PROJECT_SUMMARY,
        audience=audience,
        prompt_id=_prompt_id(audience),
        prompt_version=_PROMPT_VERSION,
        source_ids_json=source_ids,
        input_bundle_hash=bundle_hash,
        **fields,
    )
    db.add(interaction)
    db.flush()
    return interaction


def generate_summary(db: Session, project: Project, audience: AIAudience) -> SummaryGenerationResult:
    bundle = build_source_bundle(db, project)
    bundle_hash = hashlib.sha256(bundle.text.encode("utf-8")).hexdigest()

    findings = forbidden_data.scan(bundle.text)
    if findings:
        interaction = _record(
            db,
            project,
            audience,
            bundle.source_ids,
            bundle_hash,
            model_provider=settings.ai_provider,
            model_name=settings.ai_model,
            validation_status=ValidationStatus.FAILED_FORBIDDEN_DATA,
            human_review_status=HumanReviewStatus.REJECTED,
            error_category=ErrorCategory.FORBIDDEN_DATA_DETECTED,
        )
        return SummaryGenerationResult(interaction=interaction, output=None)

    prompt = _load_prompt_template(audience).format(source_bundle=bundle.text)

    start = time.monotonic()
    try:
        provider = get_provider()
        result = provider.complete(prompt)
    except ProviderUnavailableError:
        interaction = _record(
            db,
            project,
            audience,
            bundle.source_ids,
            bundle_hash,
            model_provider=settings.ai_provider,
            model_name=settings.ai_model,
            validation_status=ValidationStatus.FAILED_SCHEMA,
            human_review_status=HumanReviewStatus.REJECTED,
            error_category=ErrorCategory.PROVIDER_UNAVAILABLE,
            latency_ms=int((time.monotonic() - start) * 1000),
        )
        return SummaryGenerationResult(interaction=interaction, output=None)
    latency_ms = int((time.monotonic() - start) * 1000)

    output_findings = forbidden_data.scan(result.text)
    if output_findings:
        interaction = _record(
            db,
            project,
            audience,
            bundle.source_ids,
            bundle_hash,
            model_provider=settings.ai_provider,
            model_name=result.model_name,
            validation_status=ValidationStatus.FAILED_FORBIDDEN_DATA,
            human_review_status=HumanReviewStatus.REJECTED,
            error_category=ErrorCategory.FORBIDDEN_DATA_DETECTED,
            output_text=None,
            latency_ms=latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
        return SummaryGenerationResult(interaction=interaction, output=None)

    try:
        parsed = json.loads(_strip_code_fences(result.text))
        output = SummaryOutput.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError):
        interaction = _record(
            db,
            project,
            audience,
            bundle.source_ids,
            bundle_hash,
            model_provider=settings.ai_provider,
            model_name=result.model_name,
            validation_status=ValidationStatus.FAILED_SCHEMA,
            human_review_status=HumanReviewStatus.REJECTED,
            error_category=ErrorCategory.MALFORMED_OUTPUT,
            output_text=result.text,
            latency_ms=latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
        return SummaryGenerationResult(interaction=interaction, output=None)

    output = _enforce_stale_caveat(output, project)
    interaction = _record(
        db,
        project,
        audience,
        bundle.source_ids,
        bundle_hash,
        model_provider=settings.ai_provider,
        model_name=result.model_name,
        validation_status=ValidationStatus.PASSED,
        human_review_status=HumanReviewStatus.GENERATED,
        output_text=result.text,
        output_json=output.model_dump(),
        latency_ms=latency_ms,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )
    return SummaryGenerationResult(interaction=interaction, output=output)
