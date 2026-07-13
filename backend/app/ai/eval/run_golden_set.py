"""T10 golden-set runner: generates a real project summary for every
bundle in golden_set.GOLDEN_SET and writes a markdown report with a blank
rubric-scoring table for Gregory to fill in (see docs/eval/RUBRIC.md).

Usage (from backend/, DB migrated, IDC_AI_PROVIDER configured):

    python -m app.ai.eval.run_golden_set

This makes one real AI provider call per golden bundle (8 by default) -
if using a free-tier OpenRouter model, expect some to fail/retry due to
upstream congestion (see docs/HERMES_UPDATE_PACK.md's T8/T9 entries);
failures are recorded in the report like any other AIInteraction, not
hidden. Each run is a normal AIInteraction, kept in the audit history -
this is real evaluation activity, not scratch data to clean up after.
"""

from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.eval.golden_set import GOLDEN_SET, GoldenBundleSpec
from app.ai.models import AIInteraction
from app.ai.summary_service import generate_summary
from app.db import SessionLocal
from app.registry.models import Project

_REPORT_DIR = Path(__file__).parent.parent.parent.parent.parent / "docs" / "eval"

_RUBRIC_TABLE = (
    "| Dimension | Score (1-5) | Notes |\n"
    "|---|---|---|\n"
    "| Grounded | | |\n"
    "| Accurate | | |\n"
    "| Complete | | |\n"
    "| Safe | | |\n"
    "| Useful | | |\n"
    "| **Overall pass (Y/N)** | | |\n"
)


def _render_bundle_result(spec: GoldenBundleSpec, project: Project | None, interaction: AIInteraction | None) -> str:
    header = f"## {spec.label}\n\n"
    if project is None:
        return header + f"**Project slug `{spec.project_slug}` not found - skipped.**\n\n"

    lines = [
        header,
        f"- Project: {project.name} (`{project.slug}`)\n",
        f"- Audience: {spec.audience.value}\n",
    ]
    if interaction is None:
        lines.append("- **No interaction recorded (unexpected internal error).**\n")
        return "".join(lines)

    lines.append(f"- Prompt: `{interaction.prompt_id}` v{interaction.prompt_version}\n")
    lines.append(f"- Model: {interaction.model_provider}/{interaction.model_name}\n")
    lines.append(f"- Validation status: `{interaction.validation_status.value}`\n")
    if interaction.error_category:
        lines.append(f"- Error category: `{interaction.error_category.value}`\n")
    lines.append("\n")

    if interaction.output_json:
        out = interaction.output_json
        lines.append(f"**Summary:** {out['summary']}\n\n")
        if out.get("assumptions"):
            lines.append("**Assumptions:** " + "; ".join(out["assumptions"]) + "\n\n")
        if out.get("gaps"):
            lines.append("**Gaps:** " + "; ".join(out["gaps"]) + "\n\n")
        if out.get("recommended_next_actions"):
            lines.append(
                "**Recommended next actions:** " + "; ".join(out["recommended_next_actions"]) + "\n\n"
            )
        lines.append(f"**Model's own confidence:** {out.get('confidence')}\n\n")
    else:
        lines.append("**No usable output - this attempt failed validation or the provider call.**\n\n")

    lines.append("### Rubric score\n\n")
    lines.append(_RUBRIC_TABLE)
    lines.append("\n")
    return "".join(lines)


def run(db: Session | None = None) -> Path:
    """db is injectable for tests (isolated transaction); the CLI entrypoint
    below opens its own real session."""
    owns_session = db is None
    db = db or SessionLocal()
    sections = []
    prompt_versions: set[int] = set()
    try:
        for spec in GOLDEN_SET:
            project = db.scalar(select(Project).where(Project.slug == spec.project_slug))
            interaction = None
            if project is not None:
                result = generate_summary(db, project, spec.audience)
                db.commit()
                interaction = result.interaction
                prompt_versions.add(interaction.prompt_version)
            sections.append(_render_bundle_result(spec, project, interaction))
    finally:
        if owns_session:
            db.close()

    version_label = "-".join(str(v) for v in sorted(prompt_versions)) or "unknown"
    run_date = date.today().isoformat()
    report_path = _REPORT_DIR / f"golden_set_report_v{version_label}_{run_date}.md"

    report = (
        f"# T10 golden-set report - prompt v{version_label} - {run_date}\n\n"
        f"Generated {datetime.now(timezone.utc).isoformat()} by "
        "`python -m app.ai.eval.run_golden_set`. See `docs/eval/RUBRIC.md` "
        "for scoring instructions. Gregory fills in the rubric tables below.\n\n"
        "---\n\n" + "\n---\n\n".join(sections)
    )
    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report_path


if __name__ == "__main__":
    path = run()
    print(f"Golden-set report written to {path}")
