"""Golden-set runner, harness v3 (2026-07-14).

v3 changes, per docs/eval/HERMES_EVALUATION_V2_2026-07-14.md (advisory
evaluation by Hermes; Gregory remains the formal scorer):

- P0 evidence immutability: artifact filenames carry a UTC run timestamp;
  an existing artifact is never overwritten (refuse unless --overwrite);
- P0 structural documentation-gap checking: output `gaps` are compared
  directly against the project's documentation matrix (false-missing,
  omitted-required-gap, draft/current-called-missing, duplicates) instead
  of prose regexes;
- P0 clause-scoped state-transition check: replaces the broad v2 regexes
  that produced both false positives and false negatives on the VAS
  resolved-vs-diagnosed distinction;
- P1 per-run human scoring rows + a case-level stability verdict (strict
  stability = every run must meet Grounded/Safe thresholds);
- P1 uncertainty contract check: 'assuming <conclusion>' in the
  assumptions field is flagged (prompt v3 requires 'no conclusion drawn').

The automated pre-screen is a heuristic for the human scorer - it is
NEVER a rubric pass and its rate must not be presented as model quality.

Usage (from backend/, DB migrated, AI provider configured in-app or env):

    python -m app.ai.eval.run_golden_set [--runs 3] [--overwrite]

Every attempt is a normal AIInteraction kept in the audit history.
"""

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.eval.golden_set import GOLDEN_SET, GoldenBundleSpec
from app.ai.models import AIInteraction
from app.ai.source_bundle import build as build_source_bundle
from app.ai.summary_service import generate_summary
from app.db import SessionLocal
from app.docs_matrix.service import get_matrix
from app.registry.models import Project

_REPORT_DIR = Path(__file__).parent.parent.parent.parent.parent / "docs" / "eval"

_RUN_SCORE_ROW = (
    "| Run {i} human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___ |\n"
)

_RESOLVE_VERBS = re.compile(r"\b(resolv\w*|fixed|fixes)\b", re.IGNORECASE)
_ACCEPTABLE_STATE_VERBS = re.compile(r"\b(isolat\w*|diagnos\w*|identif\w*)\b", re.IGNORECASE)


def _clauses(text: str) -> list[str]:
    """Split prose into clauses so a 'resolved' in one clause cannot be
    attributed to a subject in another. Deliberately does NOT split on
    'and' (Hermes v3 P0): 'the SMSC issue was isolated and resolved' must
    stay one clause so the resolved-claim is still attached to its subject."""
    return [c.strip() for c in re.split(r"[.;,]", text) if c.strip()]


def check_state_transitions(text: str, subjects: tuple) -> list[str]:
    """A clause that mentions a protected subject must not claim it was
    resolved/fixed. 'Isolated/diagnosed/identified' wording is correct and
    passes - unless the same clause ALSO claims resolution ('diagnostics
    resolved a known issue' must fail)."""
    violations = []
    for clause in _clauses(text):
        lowered = clause.lower()
        if not any(s in lowered for s in subjects):
            continue
        if _RESOLVE_VERBS.search(clause):
            violations.append(clause[:120])
    return violations


# artifact_type -> phrases a model output might use for it.
_ARTIFACT_PHRASES = {
    "user_guide": ("user_guide", "user guide"),
    "admin_guide": ("admin_guide", "admin guide"),
    "developer_guide": ("developer_guide", "developer guide"),
    "agent_guide": ("agent_guide", "agent guide"),
    "support_runbook": ("support_runbook", "support runbook", "runbook"),
    "deployment_guide": ("deployment_guide", "deployment guide"),
    "verification_matrix": ("verification_matrix", "verification matrix"),
    "exit_md": ("exit_md", "exit.md", "exit md", "exit guide", "exit doc"),
}


def _artifacts_mentioned(text: str) -> set[str]:
    lowered = text.lower()
    return {a for a, phrases in _ARTIFACT_PHRASES.items() if any(p in lowered for p in phrases)}


def check_doc_gaps_structurally(matrix_state: dict, output_json: dict) -> dict:
    """Compare the output against the documentation matrix (Hermes P0):
    - false_missing: artifact claimed as a gap but matrix says it exists
      (current/draft/approved - draft is NOT missing);
    - omitted_required: matrix-confirmed required gap absent from output;
    - summary_contradictions: summary prose calls an existing artifact
      current when the matrix says missing, or missing when it exists;
    - duplicates in the gaps list.
    matrix_state: {artifact_type: {"required": bool, "is_gap": bool}}.
    """
    gaps = output_json.get("gaps") or []
    gap_text = " ".join(gaps)
    claimed = _artifacts_mentioned(gap_text)

    false_missing = sorted(
        a for a in claimed if a in matrix_state and not matrix_state[a]["is_gap"]
    )
    required_gaps = {a for a, st in matrix_state.items() if st["required"] and st["is_gap"]}
    omitted_required = sorted(required_gaps - claimed)

    lowered_gaps = [g.strip().lower() for g in gaps]
    duplicates = len(lowered_gaps) != len(set(lowered_gaps))

    # Summary prose contradiction: "<artifact> ... current/complete" while
    # the matrix marks it a gap. A window that talks about GAPS existing
    # ("documentation gaps exist for ... verification matrix") is a
    # missing-claim, not a presence-claim - Hermes v3 P0 false positive.
    summary = (output_json.get("summary") or "").lower()
    summary_contradictions = []
    for artifact, state in matrix_state.items():
        for phrase in _ARTIFACT_PHRASES[artifact]:
            if phrase in summary:
                window_start = summary.index(phrase)
                window = summary[max(0, window_start - 60): window_start + len(phrase) + 60]
                gap_context = re.search(r"\b(gap\w*|missing|absent|lack\w*)\b", window) is not None
                presence_claim = (
                    re.search(r"\b(current|complete|approved|exists?)\b", window) is not None
                    and not gap_context
                )
                if state["is_gap"] and presence_claim:
                    summary_contradictions.append(f"{artifact} called present but matrix says gap")
                if not state["is_gap"] and gap_context:
                    summary_contradictions.append(f"{artifact} called missing but matrix says it exists")
                break

    ok = not (false_missing or omitted_required or duplicates or summary_contradictions)
    return {
        "ok": ok,
        "false_missing": false_missing,
        "omitted_required": omitted_required,
        "duplicates": duplicates,
        "summary_contradictions": summary_contradictions,
    }


_ASSUMING_CONCLUSION = re.compile(r"\bassum\w+\b", re.IGNORECASE)
_NO_CONCLUSION = re.compile(r"no\s+conclusion", re.IGNORECASE)


def check_uncertainty_contract(output_json: dict) -> list[str]:
    """Prompt v3 contract: an assumptions/uncertainties item records what is
    not recorded and draws no conclusion. 'Assuming <hypothesis>' without an
    explicit 'no conclusion drawn' is flagged (Hermes P1)."""
    violations = []
    for item in output_json.get("assumptions") or []:
        if _ASSUMING_CONCLUSION.search(item) and not _NO_CONCLUSION.search(item):
            violations.append(item[:120])
    return violations


def _output_text(interaction: AIInteraction) -> str:
    if not interaction.output_json:
        return ""
    out = interaction.output_json
    parts = [out.get("summary", "")]
    for key in ("assumptions", "gaps", "recommended_next_actions"):
        parts.extend(out.get(key) or [])
    return " ".join(parts)


def check_claims(spec: GoldenBundleSpec, interaction: AIInteraction, matrix_state: dict | None = None) -> dict:
    """Automated pre-screen (heuristic; human rubric decides)."""
    text = _output_text(interaction)
    lowered = text.lower()
    results: dict = {
        "expected": [], "prohibited": [], "state_transitions": [],
        "doc_structural": None, "uncertainty_violations": [], "ok": True,
    }
    if not text:
        results["ok"] = False
        return results
    for group in spec.expected_facts:
        hit = any(phrase.lower() in lowered for phrase in group)
        results["expected"].append({"any_of": list(group), "found": hit})
        if not hit:
            results["ok"] = False
    for pattern in spec.prohibited_patterns:
        matched = re.search(pattern, lowered, re.IGNORECASE) is not None
        results["prohibited"].append({"pattern": pattern, "violated": matched})
        if matched:
            results["ok"] = False
    if spec.no_resolved_subjects:
        violations = check_state_transitions(text, spec.no_resolved_subjects)
        results["state_transitions"] = violations
        if violations:
            results["ok"] = False
    if matrix_state is not None and interaction.output_json:
        doc = check_doc_gaps_structurally(matrix_state, interaction.output_json)
        results["doc_structural"] = doc
        if not doc["ok"]:
            results["ok"] = False
    if interaction.output_json:
        uv = check_uncertainty_contract(interaction.output_json)
        results["uncertainty_violations"] = uv
        if uv:
            results["ok"] = False
    return results


def _claims_detail(claims: dict) -> list[str]:
    details = []
    for e in claims["expected"]:
        if not e["found"]:
            details.append(f"missing expected fact (any of: {', '.join(e['any_of'])})")
    for pr in claims["prohibited"]:
        if pr["violated"]:
            details.append(f"prohibited claim matched: `{pr['pattern']}`")
    for v in claims["state_transitions"]:
        details.append(f'state-transition violation (subject claimed resolved): "{v}"')
    doc = claims.get("doc_structural")
    if doc and not doc["ok"]:
        if doc["false_missing"]:
            details.append(f"false-missing artifacts (matrix says they exist): {', '.join(doc['false_missing'])}")
        if doc["omitted_required"]:
            details.append(f"omitted required gaps: {', '.join(doc['omitted_required'])}")
        if doc["duplicates"]:
            details.append("duplicate entries in gaps")
        for c in doc["summary_contradictions"]:
            details.append(f"summary contradicts matrix: {c}")
    for v in claims["uncertainty_violations"]:
        details.append(f'speculative assumption (no-conclusion contract): "{v}"')
    return details


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
            details = _claims_detail(claims)
            lines.append(
                f"- Automated claim pre-screen (heuristic, not a rubric pass): **{verdict}**"
                + (f" - {'; '.join(details)}" if details else "")
                + "\n"
            )
        lines.append(f"\n**Summary:** {out['summary']}\n\n")
        if out.get("assumptions"):
            lines.append("**Uncertainties/assumptions:** " + "; ".join(out["assumptions"]) + "\n\n")
        if out.get("gaps"):
            lines.append("**Gaps:** " + "; ".join(out["gaps"]) + "\n\n")
        if out.get("recommended_next_actions"):
            lines.append(
                "**Recommended next actions:** " + "; ".join(out["recommended_next_actions"]) + "\n\n"
            )
        lines.append(_RUN_SCORE_ROW.format(i=index).replace("| Run", "Run").replace(" |\n", "\n"))
        lines.append("\n")
    else:
        lines.append("\n**No usable output - this attempt failed validation or the provider call.**\n\n")
        lines.append(f"Run {index} human score: hard fail (no output)\n\n")
    return "".join(lines)


_STABILITY_TABLE = (
    "### Case verdict (human)\n\n"
    "| Question | Answer |\n"
    "|---|---|\n"
    "| Every run Grounded >= 4? | |\n"
    "| Every run Safe >= 4? | |\n"
    "| All runs schema-valid? | {schema} |\n"
    "| Strict stable pass (all of the above + rubric pass on every run)? | |\n"
)


def run(db: Session | None = None, runs: int = 1, overwrite: bool = False) -> Path:
    """db injectable for tests; CLI opens its own session. runs = attempts
    per case. Artifacts are timestamped and never silently overwritten."""
    owns_session = db is None
    db = db or SessionLocal()
    started_at = datetime.now(timezone.utc)
    sections: list[str] = []
    frozen_inputs: dict[str, dict] = {}
    prompt_versions: set[int] = set()
    stats = {"attempts": 0, "schema_ok": 0, "claims_ok": 0, "latency_ms": [], "tokens": []}

    try:
        # Snapshot the full evaluation input boundary BEFORE the first
        # provider call (Hermes v3 P2): a live API write during the run can
        # no longer change a later case's bundle relative to this freeze.
        snapshots: dict[str, dict] = {}
        for spec in GOLDEN_SET:
            project = db.scalar(select(Project).where(Project.slug == spec.project_slug))
            if project is None:
                continue
            bundle = build_source_bundle(db, project)
            snapshots[spec.label] = {
                "project_id": project.id,
                "bundle_text": bundle.text,
                "bundle_hash": hashlib.sha256(bundle.text.encode("utf-8")).hexdigest(),
                "matrix_state": {
                    e.artifact_type.value: {"required": e.required, "is_gap": e.is_gap}
                    for e in get_matrix(db, project)
                },
            }

        for spec in GOLDEN_SET:
            project = db.scalar(select(Project).where(Project.slug == spec.project_slug))
            header = f"## {spec.label}\n\n"
            if project is None or spec.label not in snapshots:
                sections.append(header + f"**Project slug `{spec.project_slug}` not found - skipped.**\n\n")
                continue

            snap = snapshots[spec.label]
            bundle_hash = snap["bundle_hash"]
            matrix_state = snap["matrix_state"]
            frozen_inputs[spec.label] = {
                "project_slug": spec.project_slug,
                "audience": spec.audience.value,
                "bundle_sha256": bundle_hash,
                "bundle_text": snap["bundle_text"],
                "documentation_matrix": matrix_state,
                "expected_facts": [list(g) for g in spec.expected_facts],
                "prohibited_patterns": list(spec.prohibited_patterns),
                "no_resolved_subjects": list(spec.no_resolved_subjects),
                "fact_checklist": list(spec.fact_checklist),
                "frozen_at": started_at.isoformat(),
            }

            case_lines = [
                header,
                f"- Project: {project.name} (`{project.slug}`)\n",
                f"- Audience: {spec.audience.value}\n",
                f"- Source-bundle SHA-256: `{bundle_hash}`\n",
            ]
            run_bodies = []
            case_schema_ok = 0
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
                    case_schema_ok += 1
                    claims = check_claims(spec, interaction, matrix_state)
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
            case_lines.append("\n")
            case_lines.extend(run_bodies)
            if spec.fact_checklist:
                case_lines.append("### Human fact checklist (verify against the frozen bundle)\n\n")
                for item in spec.fact_checklist:
                    case_lines.append(f"- [ ] {item}\n")
                case_lines.append("\n")
            case_lines.append(_STABILITY_TABLE.format(schema=f"{case_schema_ok}/{runs}"))
            case_lines.append("\n")
            sections.append("".join(case_lines))
    finally:
        if owns_session:
            db.close()

    version_label = "-".join(str(v) for v in sorted(prompt_versions)) or "unknown"
    run_stamp = started_at.strftime("%Y-%m-%dT%H%M%SZ")
    report_path = _REPORT_DIR / f"golden_set_report_v{version_label}_{run_stamp}.md"
    frozen_path = _REPORT_DIR / f"golden_set_frozen_inputs_v{version_label}_{run_stamp}.json"
    for path in (report_path, frozen_path):
        if path.exists() and not overwrite:
            raise FileExistsError(
                f"{path} already exists - evaluation artifacts are immutable. "
                "Pass --overwrite only if you are certain."
            )

    schema_rate = f"{stats['schema_ok']}/{stats['attempts']}"
    claims_rate = f"{stats['claims_ok']}/{stats['attempts']}"
    avg_latency = int(sum(stats["latency_ms"]) / len(stats["latency_ms"])) if stats["latency_ms"] else 0
    avg_tokens = int(sum(stats["tokens"]) / len(stats["tokens"])) if stats["tokens"] else 0

    report = (
        f"# T10 golden-set report - prompt v{version_label} - {run_stamp}\n\n"
        f"Generated {started_at.isoformat()} by "
        f"`python -m app.ai.eval.run_golden_set --runs {runs}`. See `docs/eval/RUBRIC.md`.\n"
        "Automated pre-screens are heuristics for the human scorer - never a rubric pass\n"
        "and never a model-quality metric. Exact source bundles, hashes and the\n"
        f"documentation-matrix state are frozen in `{frozen_path.name}`.\n\n"
        "## Aggregate stats\n\n"
        f"- Attempts: {stats['attempts']} ({runs} run(s) x {len(frozen_inputs)} cases)\n"
        f"- Schema-valid outputs: {schema_rate}\n"
        f"- Automated claim pre-screen passed (heuristic): {claims_rate}\n"
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
    parser.add_argument("--overwrite", action="store_true", help="allow overwriting an existing artifact")
    args = parser.parse_args()
    path = run(runs=args.runs, overwrite=args.overwrite)
    print(f"Golden-set report written to {path}")
