"""Tests for the golden-set harness v3 (2026-07-14, implementing the P0/P1
brief in docs/eval/HERMES_EVALUATION_V2_2026-07-14.md). No real network
calls - AI summary logic itself is covered by test_ai_summary.py."""

import json

import pytest

from app.ai.eval.golden_set import GOLDEN_SET, GoldenBundleSpec
from app.ai.eval.run_golden_set import (
    check_claims,
    check_doc_gaps_structurally,
    check_state_transitions,
    check_uncertainty_contract,
    run,
)
from app.ai.models import AIInteraction
from app.vocab import AIAudience, AITaskType, HumanReviewStatus, ValidationStatus


def _interaction(output_json) -> AIInteraction:
    return AIInteraction(
        project_id=1,
        task_type=AITaskType.PROJECT_SUMMARY,
        audience=AIAudience.DEVELOPER,
        prompt_id="project_summary__developer",
        prompt_version=3,
        source_ids_json={},
        input_bundle_hash="abc",
        model_provider="openrouter",
        model_name="fake-model",
        output_json=output_json,
        validation_status=ValidationStatus.PASSED,
        human_review_status=HumanReviewStatus.GENERATED,
    )


def _output(summary="s", assumptions=(), gaps=(), actions=()):
    return {
        "summary": summary,
        "assumptions": list(assumptions),
        "gaps": list(gaps),
        "recommended_next_actions": list(actions),
        "requires_human_review": True,
        "confidence": 0.5,
    }


def test_golden_set_covers_all_four_pilots_and_both_audiences() -> None:
    assert len(GOLDEN_SET) == 8
    slugs = {spec.project_slug for spec in GOLDEN_SET}
    assert slugs == {"cwscx-platform", "cws-pulse-awards", "vas-network-check", "health-fair-2026"}
    for slug in slugs:
        audiences = {spec.audience for spec in GOLDEN_SET if spec.project_slug == slug}
        assert audiences == {AIAudience.DEVELOPER, AIAudience.MANAGER}


# --- P0: state-transition checker - Hermes' four regression fixtures ---

_SUBJECTS = ("smsc", "authentication", "auth rejection")


def test_state_transition_wrong_resolved_claim_fails() -> None:
    # "wrong and must fail"
    violations = check_state_transitions(
        "SMSC authentication diagnostics resolved a known issue", _SUBJECTS
    )
    assert violations


def test_state_transition_correct_isolated_claim_passes() -> None:
    # "correct and must pass"
    violations = check_state_transitions(
        "Diagnostics isolated the SMSC failure to authentication rejection", _SUBJECTS
    )
    assert violations == []


def test_state_transition_other_component_resolved_in_same_sentence_passes() -> None:
    # "correct and must pass even if another component was resolved in the
    # same sentence" - the exact v2 false positive.
    violations = check_state_transitions(
        "After resolving the styled email default, an authentication-related "
        "SMSC failure has been isolated but remains under monitoring",
        _SUBJECTS,
    )
    assert violations == []


def test_state_transition_wrong_regardless_of_word_order_fails() -> None:
    # "wrong and must fail regardless of whether resolved appears before or
    # after SMSC/authentication"
    for text in (
        "the SMSC issue was resolved last week",
        "we resolved the SMSC authentication problem",
        "Recent SMSC authentication diagnostics resolved a known issue",
    ):
        assert check_state_transitions(text, _SUBJECTS), text


# --- P0: structural documentation-gap checks ---

_MATRIX = {
    "admin_guide": {"required": True, "is_gap": True},
    "developer_guide": {"required": True, "is_gap": True},
    "agent_guide": {"required": True, "is_gap": False},   # current
    "exit_md": {"required": True, "is_gap": False},       # draft - NOT missing
}


def test_doc_structural_catches_false_missing_draft_artifact() -> None:
    # Health Fair v2 failure: draft exit_md called missing.
    out = _output(gaps=["Missing exit_md", "Missing admin_guide", "Missing developer_guide"])
    result = check_doc_gaps_structurally(_MATRIX, out)
    assert result["false_missing"] == ["exit_md"]
    assert result["ok"] is False


def test_doc_structural_catches_omitted_required_gap() -> None:
    # Health Fair v2 failure: developer_guide (matrix-missing) omitted.
    out = _output(gaps=["Missing admin_guide"])
    result = check_doc_gaps_structurally(_MATRIX, out)
    assert "developer_guide" in result["omitted_required"]
    assert result["ok"] is False


def test_doc_structural_catches_summary_contradiction() -> None:
    # CWSCX v2 failure: "Admin/agent guides are current" while admin_guide
    # is a matrix gap.
    out = _output(
        summary="Admin guide is current and complete.",
        gaps=["Missing admin_guide", "Missing developer_guide"],
    )
    result = check_doc_gaps_structurally(_MATRIX, out)
    assert result["summary_contradictions"]
    assert result["ok"] is False


def test_doc_structural_passes_correct_output() -> None:
    out = _output(gaps=["Missing admin_guide", "Missing developer_guide"])
    result = check_doc_gaps_structurally(_MATRIX, out)
    assert result == {
        "ok": True, "false_missing": [], "omitted_required": [],
        "duplicates": False, "summary_contradictions": [],
    }


def test_doc_structural_catches_duplicates() -> None:
    out = _output(gaps=["Missing admin_guide", "missing admin_guide", "Missing developer_guide"])
    assert check_doc_gaps_structurally(_MATRIX, out)["duplicates"] is True


# --- P1: uncertainty contract ---

def test_uncertainty_contract_flags_speculative_assumptions() -> None:
    # The exact v2 failures.
    for bad in (
        "Business owners are unconfirmed; assuming active ownership.",
        "assuming delayed if not communicated by next milestone",
        "assuming stakeholders are managing this aspect externally",
    ):
        assert check_uncertainty_contract(_output(assumptions=[bad])), bad


def test_uncertainty_contract_accepts_no_conclusion_phrasing() -> None:
    ok = "Current business-owner engagement is not fully recorded; no conclusion drawn."
    assert check_uncertainty_contract(_output(assumptions=[ok])) == []


# --- P1: expanded semantic criteria ---

def test_pulse_manager_ceo_widening_variants_fail() -> None:
    pulse_mgr = next(
        s for s in GOLDEN_SET
        if s.project_slug == "cws-pulse-awards" and s.audience == AIAudience.MANAGER
    )
    for bad in (
        "Business continuity depends on Naadir/CEO sign-off for the Golden Ticket requirement.",
        "CEO approval is required for final project acceptance.",
    ):
        result = check_claims(pulse_mgr, _interaction(_output(summary=bad)))
        assert result["ok"] is False, bad
    scoped = "CEO/Naadir remains a dependency for the Golden Ticket requirement."
    assert check_claims(pulse_mgr, _interaction(_output(summary=scoped)))["ok"] is True


def test_health_fair_vague_quarter_and_invented_delay_fail() -> None:
    hf_mgr = next(
        s for s in GOLDEN_SET
        if s.project_slug == "health-fair-2026" and s.audience == AIAudience.MANAGER
    )
    q3 = _output(summary="Delivery targets a Q3 2026 deadline.")
    result = check_claims(hf_mgr, _interaction(q3))
    assert any(p["violated"] for p in result["prohibited"])

    delay = _output(summary="Entra backend authorization delays are impacting delivery by 2026-07-31.")
    result = check_claims(hf_mgr, _interaction(delay))
    assert any(p["violated"] for p in result["prohibited"])

    good = _output(summary="Testing is due 2026-07-31 ahead of the 2026-08-07 event; Entra authorization work is incomplete.")
    assert check_claims(hf_mgr, _interaction(good))["ok"] is True


# --- P0: evidence immutability + end-to-end run ---

def test_run_writes_timestamped_artifacts_and_refuses_overwrite(
    db, tmp_path, monkeypatch
) -> None:
    import app.ai.eval.run_golden_set as run_module

    monkeypatch.setattr(run_module, "_REPORT_DIR", tmp_path)
    report_path = run(db, runs=1)
    content = report_path.read_text(encoding="utf-8")
    accounted_for = content.count("No usable output") + content.count("not found - skipped")
    assert accounted_for == len(GOLDEN_SET)  # disabled provider fails every attempt
    assert "## Aggregate stats" in content
    # Timestamped, immutable filename (not just a date).
    assert "T" in report_path.stem and report_path.stem.endswith("Z")

    frozen_files = list(tmp_path.glob("golden_set_frozen_inputs_*.json"))
    assert len(frozen_files) == 1
    frozen = json.loads(frozen_files[0].read_text(encoding="utf-8"))
    for case in frozen.values():
        assert case["bundle_sha256"] and case["bundle_text"]
        assert "documentation_matrix" in case

    # A colliding artifact path must refuse without --overwrite: pin the
    # run timestamp to the first run's and rerun.
    import datetime as _dt

    started = _dt.datetime.strptime(
        report_path.stem.split("_")[-1], "%Y-%m-%dT%H%M%SZ"
    ).replace(tzinfo=_dt.timezone.utc)

    class _FixedDatetime(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return started

    monkeypatch.setattr(run_module, "datetime", _FixedDatetime)
    with pytest.raises(FileExistsError):
        run(db, runs=1)
