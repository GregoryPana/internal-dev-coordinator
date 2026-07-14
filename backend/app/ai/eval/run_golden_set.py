"""Golden-set runner, v2 harness (2026-07-14, from Gregory's evaluation
findings on the v1 harness):

- each case runs N times (default 3 via CLI, 1 when injected in tests) so a
  single lucky/unlucky sample is never mistaken for model behaviour;
- the exact source-bundle text + SHA-256 hash per case are frozen to a
  JSON file next to the report, making prompt-version comparisons
  defensible (and hash drift between runs is flagged);
- per-case claim checks (expected facts / prohibited claims from
  golden_set.py) are auto-evaluated per run and shown in the report as a
  pre-screen for the human scorer;
- requires_human_review is shown for every output;
- an aggregate stats section reports schema-success rate, claim-check
  results, latency and token usage.

Usage (from backend/, DB migrated, AI provider configured in-app or env):

    python -m app.ai.eval.run_golden_set [--runs 3]

Every attempt is a normal AIInteraction kept in the audit history.
"""

import argparse
import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.eval.golden_set import GOLDEN_SET, GoldenBundleSpec
from app.ai.models import AIInteraction
from app.ai.source_bundle import build as build_source_bundle
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


def _output_text(interaction: AIInteraction) -> str:
    if not interaction.output_json:
        return ""
    out = interaction.output_json
    parts = [out.get("summary", "")]
    for key in ("assumptions", "gaps", "recommended_next_actions"):
        parts.extend(out.get(key) or [])
    return " ".join(parts)


def check_claims(spec: GoldenBundleSpec, interaction: AIInteraction) -> dict:
    """Automated pre-screen: expected any-of fact groups + prohibited
    patterns + duplicate-gap hygiene. Human rubric still decides."""
    text = _output_text(interaction).lower()
    results = {"expected": [], "prohibited": [], "duplicate_gaps": False, "ok": True}
    if not text:
        results["ok"] = False
        return results
    for group in spec.expected_facts:
        hit = any(phrase.lower() in text for phrase in group)
        results["expected"].append({"any_of": list(group), "found": hit})
        if not hit:
            results["ok"] = False
    for pattern in spec.prohibited_patterns:
        matched = re.search(pattern, text, re.IGNORECASE) is not None
        results["prohibited"].append({"pattern": pattern, "violated": matched})
        if matched:
            results["ok"] = False
    gaps = [g.strip().lower() for g in (interaction.output_json or {}).get("gaps", [])]
    if len(gaps) != len(set(gaps)):
        results["duplicate_gaps"] = True
        results["ok"] = False
    return results


def _render_run(index: int, interaction: AIInteraction, claims: dict | None) -> str:
    lines = [f"#### Run {index}\n\n"]
    lines.append(f"- Model: {interaction.model_provider}/{interaction.model_name}\n")
    lines.append(f"- Validation status: `{interaction.validation_status.value}`\n")
    if interaction.error_category:
        lines.append(f"- Error category: `{interaction.error_category.value}`\n")
    if interaction.output_json:
        out = interaction.output_json
        lines.append(f"- requires_human_review: `{out.get('requires_human_review')}`\n")
        lines.append(f"- Model self-reported confidence (uncalibrated): {out.get('confidence')}\n")
        if claims is not None:
            verdict = "PASS" if claims["ok"] else "FAIL"
            details = []
            for e in claims["expected"]:
                if not e["found"]:
                    details.append(f"missing expected fact (any of: {', '.join(e['any_of'])})")
            for pr in claims["prohibited"]:
                if pr["violated"]:
                    details.append(f"prohibited claim matched: `{pr['pattern']}`")
            if claims["duplicate_gaps"]:
                details.append("duplicate entries in gaps")
            lines.append(
                f"- Automated claim pre-screen: **{verdict}**"
                + (f" - {'; '.join(details)}" if details else "")
                + "\n"
            )
        lines.append(f"\n**Summary:** {out['summary']}\n\n")
        if out.get("assumptions"):
            lines.append("**Assumptions:** " + "; ".join(out["assumptions"]) + "\n\n")
        if out.get("gaps"):
            lines.append("**Gaps:** " + "; ".join(out["gaps"]) + "\n\n")
        if out.get("recommended_next_actions"):
            lines.append(
                "**Recommended next actions:** " + "; ".join(out["recommended_next_actions"]) + "\n\n"
            )
    else:
        lines.append("\n**No usable output - this attempt failed validation or the provider call.**\n\n")
    return "".join(lines)


def run(db: Session | None = None, runs: int = 1) -> Path:
    """db is injectable for tests; the CLI opens its own session. runs = N
    attempts per case (schema-success/variance need N >= 3 to mean much)."""
    owns_session = db is None
    db = db or SessionLocal()
    sections: list[str] = []
    frozen_inputs: dict[str, dict] = {}
    prompt_versions: set[int] = set()
    stats = {"attempts": 0, "schema_ok": 0, "claims_ok": 0, "latency_ms": [], "tokens": []}

    try:
        for spec in GOLDEN_SET:
            project = db.scalar(select(Project).where(Project.slug == spec.project_slug))
            header = f"## {spec.label}\n\n"
            if project is None:
                sections.append(header + f"**Project slug `{spec.project_slug}` not found - skipped.**\n\n")
                continue

            bundle = build_source_bundle(db, project)
            bundle_hash = hashlib.sha256(bundle.text.encode("utf-8")).hexdigest()
            frozen_inputs[spec.label] = {
                "project_slug": spec.project_slug,
                "audience": spec.audience.value,
                "bundle_sha256": bundle_hash,
                "bundle_text": bundle.text,
                "expected_facts": [list(g) for g in spec.expected_facts],
                "prohibited_patterns": list(spec.prohibited_patterns),
                "frozen_at": datetime.now(timezone.utc).isoformat(),
            }

            case_lines = [
                header,
                f"- Project: {project.name} (`{project.slug}`)\n",
                f"- Audience: {spec.audience.value}\n",
                f"- Source-bundle SHA-256: `{bundle_hash[:16]}…` (full text frozen alongside this report)\n",
            ]
            run_bodies = []
            hash_drift = False
            for i in range(1, runs + 1):
                current_hash = hashlib.sha256(
                    build_source_bundle(db, project).text.encode("utf-8")
                ).hexdigest()
                if current_hash != bundle_hash:
                    hash_drift = True
                result = generate_summary(db, project, spec.audience)
                db.commit()
                interaction = result.interaction
                prompt_versions.add(interaction.prompt_version)
                stats["attempts"] += 1
                claims = None
                if interaction.output_json:
                    stats["schema_ok"] += 1
                    claims = check_claims(spec, interaction)
                    if claims["ok"]:
                        stats["claims_ok"] += 1
                if interaction.latency_ms:
                    stats["latency_ms"].append(interaction.latency_ms)
                if interaction.input_tokens and interaction.output_tokens:
                    stats["tokens"].append(interaction.input_tokens + interaction.output_tokens)
                run_bodies.append(_render_run(i, interaction, claims))
            if hash_drift:
                case_lines.append(
                    "- **WARNING: source bundle changed between runs - comparisons within this case are tainted.**\n"
                )
            case_lines.append(f"- Prompt version(s): {', '.join(str(v) for v in sorted(prompt_versions))}\n\n")
            case_lines.extend(run_bodies)
            case_lines.append("### Rubric score (human, across the runs above)\n\n")
            case_lines.append(_RUBRIC_TABLE)
            case_lines.append("\n")
            sections.append("".join(case_lines))
    finally:
        if owns_session:
            db.close()

    version_label = "-".join(str(v) for v in sorted(prompt_versions)) or "unknown"
    run_date = date.today().isoformat()
    report_path = _REPORT_DIR / f"golden_set_report_v{version_label}_{run_date}.md"
    frozen_path = _REPORT_DIR / f"golden_set_frozen_inputs_v{version_label}_{run_date}.json"

    schema_rate = f"{stats['schema_ok']}/{stats['attempts']}"
    claims_rate = f"{stats['claims_ok']}/{stats['attempts']}"
    avg_latency = int(sum(stats["latency_ms"]) / len(stats["latency_ms"])) if stats["latency_ms"] else 0
    avg_tokens = int(sum(stats["tokens"]) / len(stats["tokens"])) if stats["tokens"] else 0

    report = (
        f"# T10 golden-set report - prompt v{version_label} - {run_date}\n\n"
        f"Generated {datetime.now(timezone.utc).isoformat()} by "
        f"`python -m app.ai.eval.run_golden_set --runs {runs}`. See `docs/eval/RUBRIC.md` "
        "for scoring instructions; automated claim pre-screens flag known failure "
        "modes but the human rubric decides. Exact source bundles + hashes frozen in "
        f"`{frozen_path.name}`.\n\n"
        "## Aggregate stats\n\n"
        f"- Attempts: {stats['attempts']} ({runs} run(s) x {len(frozen_inputs)} cases)\n"
        f"- Schema-valid outputs: {schema_rate}\n"
        f"- Automated claim pre-screen passed: {claims_rate}\n"
        f"- Avg latency: {avg_latency} ms; avg total tokens: {avg_tokens}\n\n"
        "---\n\n" + "\n---\n\n".join(sections)
    )
    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    frozen_path.write_text(json.dumps(frozen_inputs, indent=2), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3, help="attempts per case (default 3)")
    args = parser.parse_args()
    path = run(runs=args.runs)
    print(f"Golden-set report written to {path}")
