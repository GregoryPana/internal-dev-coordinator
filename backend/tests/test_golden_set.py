"""Tests for the golden-set harness (v2, 2026-07-14): coverage, automated
claim pre-screens, frozen inputs, multi-run reporting. No real network
calls - the AI summary logic itself is covered by test_ai_summary.py."""

import json

from app.ai.eval.golden_set import GOLDEN_SET, GoldenBundleSpec
from app.ai.eval.run_golden_set import check_claims, run
from app.ai.models import AIInteraction
from app.vocab import AIAudience, AITaskType, HumanReviewStatus, ValidationStatus


def _interaction(output_json) -> AIInteraction:
    return AIInteraction(
        project_id=1,
        task_type=AITaskType.PROJECT_SUMMARY,
        audience=AIAudience.DEVELOPER,
        prompt_id="project_summary__developer",
        prompt_version=2,
        source_ids_json={},
        input_bundle_hash="abc",
        model_provider="openrouter",
        model_name="fake-model",
        output_json=output_json,
        validation_status=ValidationStatus.PASSED,
        human_review_status=HumanReviewStatus.GENERATED,
    )


def test_golden_set_covers_all_four_pilots_and_both_audiences() -> None:
    assert len(GOLDEN_SET) == 8
    slugs = {spec.project_slug for spec in GOLDEN_SET}
    assert slugs == {"cwscx-platform", "cws-pulse-awards", "vas-network-check", "health-fair-2026"}
    for slug in slugs:
        audiences = {spec.audience for spec in GOLDEN_SET if spec.project_slug == slug}
        assert audiences == {AIAudience.DEVELOPER, AIAudience.MANAGER}


def test_check_claims_catches_the_vas_resolved_upgrade() -> None:
    """The exact v1 failure: 'diagnosed' upgraded to 'resolved'."""
    vas_dev = next(
        s for s in GOLDEN_SET
        if s.project_slug == "vas-network-check" and s.audience == AIAudience.DEVELOPER
    )
    bad = _interaction({
        "summary": "Recent fixes resolved SMSC authentication issues. Handover pending.",
        "assumptions": [], "gaps": [], "recommended_next_actions": [],
        "requires_human_review": True, "confidence": 0.5,
    })
    result = check_claims(vas_dev, bad)
    assert result["ok"] is False
    assert any(p["violated"] for p in result["prohibited"])

    good = _interaction({
        "summary": "SSH diagnostic isolated the SMSC failure to authentication rejection; "
        "monitoring required if failures recur. Handover pending ownership confirmation.",
        "assumptions": [], "gaps": [], "recommended_next_actions": [],
        "requires_human_review": True, "confidence": 0.5,
    })
    result = check_claims(vas_dev, good)
    assert result["ok"] is True


def test_check_claims_catches_duplicate_gaps_and_missing_facts() -> None:
    spec = GoldenBundleSpec(
        "x - developer", "x", AIAudience.DEVELOPER,
        expected_facts=(("deadline",),),
    )
    dup = _interaction({
        "summary": "Something about the deadline.",
        "assumptions": [], "gaps": ["missing developer_guide", "Missing developer_guide"],
        "recommended_next_actions": [], "requires_human_review": True, "confidence": 0.5,
    })
    result = check_claims(spec, dup)
    assert result["duplicate_gaps"] is True and result["ok"] is False

    missing_fact = _interaction({
        "summary": "No mention of the required fact.",
        "assumptions": [], "gaps": [], "recommended_next_actions": [],
        "requires_human_review": True, "confidence": 0.5,
    })
    result = check_claims(spec, missing_fact)
    assert result["ok"] is False and result["expected"][0]["found"] is False


def test_check_claims_catches_invented_devops() -> None:
    pulse_mgr = next(
        s for s in GOLDEN_SET
        if s.project_slug == "cws-pulse-awards" and s.audience == AIAudience.MANAGER
    )
    bad = _interaction({
        "summary": "Prioritize SMTP relay configuration with DevOps.",
        "assumptions": [], "gaps": [], "recommended_next_actions": [],
        "requires_human_review": True, "confidence": 0.5,
    })
    assert check_claims(pulse_mgr, bad)["ok"] is False


def test_run_with_disabled_provider_reports_all_and_freezes_inputs(
    db, tmp_path, monkeypatch
) -> None:
    """Against the real dev DB (SAVEPOINT fixture sees committed pilots)
    with the autouse disabled provider: run() must produce a complete
    report (every bundle accounted for), plus a frozen-inputs JSON with a
    bundle hash + text per found case. Never raises."""
    import app.ai.eval.run_golden_set as run_module

    monkeypatch.setattr(run_module, "_REPORT_DIR", tmp_path)
    report_path = run(db, runs=1)
    content = report_path.read_text(encoding="utf-8")
    accounted_for = content.count("No usable output") + content.count("not found - skipped")
    assert accounted_for == len(GOLDEN_SET)
    assert "## Aggregate stats" in content
    assert "Schema-valid outputs: 0/" in content  # disabled provider fails every attempt

    frozen_files = list(tmp_path.glob("golden_set_frozen_inputs_*.json"))
    assert len(frozen_files) == 1
    frozen = json.loads(frozen_files[0].read_text(encoding="utf-8"))
    for label, case in frozen.items():
        assert case["bundle_sha256"] and case["bundle_text"]
        assert case["project_slug"] in label
