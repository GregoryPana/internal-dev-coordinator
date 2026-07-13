"""Tests for the T10 golden-set harness itself (report rendering, graceful
handling of missing projects) - not the AI summary logic, which
test_ai_summary.py already covers. No real network calls here."""

from app.ai.eval.golden_set import GOLDEN_SET, GoldenBundleSpec
from app.ai.eval.run_golden_set import _render_bundle_result, run
from app.ai.models import AIInteraction
from app.vocab import AIAudience, AITaskType, ErrorCategory, HumanReviewStatus, ValidationStatus


def test_golden_set_covers_all_four_pilots_and_both_audiences() -> None:
    assert len(GOLDEN_SET) == 8
    slugs = {spec.project_slug for spec in GOLDEN_SET}
    assert slugs == {"cwscx-platform", "cws-pulse-awards", "vas-network-check", "health-fair-2026"}
    for slug in slugs:
        audiences = {spec.audience for spec in GOLDEN_SET if spec.project_slug == slug}
        assert audiences == {AIAudience.DEVELOPER, AIAudience.MANAGER}


def test_render_bundle_result_missing_project_is_skipped_not_crashed() -> None:
    spec = GoldenBundleSpec("Nonexistent - developer", "does-not-exist", AIAudience.DEVELOPER)
    text = _render_bundle_result(spec, None, None)
    assert "not found - skipped" in text


def test_render_bundle_result_with_successful_output_includes_rubric_table(db) -> None:
    from app.registry.models import Project

    project = Project(
        slug="fake-project",
        name="Fake Project",
        project_type="prototype",
        classification="one-off",
        phase="build",
        status="active",
        priority="low",
    )
    interaction = AIInteraction(
        project_id=1,
        task_type=AITaskType.PROJECT_SUMMARY,
        audience=AIAudience.DEVELOPER,
        prompt_id="project_summary__developer",
        prompt_version=1,
        source_ids_json={},
        input_bundle_hash="abc",
        model_provider="openrouter",
        model_name="fake-model",
        output_text="{}",
        output_json={
            "summary": "Grounded summary text.",
            "assumptions": [],
            "gaps": ["Missing exit_md"],
            "recommended_next_actions": ["Do the thing."],
            "requires_human_review": True,
            "confidence": 0.9,
        },
        validation_status=ValidationStatus.PASSED,
        human_review_status=HumanReviewStatus.GENERATED,
    )
    spec = GoldenBundleSpec("Fake Project - developer", "fake-project", AIAudience.DEVELOPER)
    text = _render_bundle_result(spec, project, interaction)

    assert "Grounded summary text." in text
    assert "Missing exit_md" in text
    assert "Overall pass (Y/N)" in text
    assert "passed" in text


def test_render_bundle_result_with_failed_output_shows_failure_not_crash() -> None:
    from app.registry.models import Project

    project = Project(
        slug="fake-project",
        name="Fake Project",
        project_type="prototype",
        classification="one-off",
        phase="build",
        status="active",
        priority="low",
    )
    interaction = AIInteraction(
        project_id=1,
        task_type=AITaskType.PROJECT_SUMMARY,
        audience=AIAudience.MANAGER,
        prompt_id="project_summary__manager",
        prompt_version=1,
        source_ids_json={},
        input_bundle_hash="abc",
        model_provider="openrouter",
        model_name="fake-model",
        output_json=None,
        error_category=ErrorCategory.PROVIDER_UNAVAILABLE,
        validation_status=ValidationStatus.FAILED_SCHEMA,
        human_review_status=HumanReviewStatus.REJECTED,
    )
    spec = GoldenBundleSpec("Fake Project - manager", "fake-project", AIAudience.MANAGER)
    text = _render_bundle_result(spec, project, interaction)

    assert "No usable output" in text
    assert "provider_unavailable" in text


def test_run_against_real_dev_db_with_provider_disabled_fails_cleanly_not_crashed(
    db, tmp_path, monkeypatch
) -> None:
    """The test DB fixture wraps the *real* dev Postgres in a rolled-back
    transaction - it still sees already-committed rows, so this actually
    runs against the real T6 pilot projects if seeded. With the autouse
    ai_provider="disabled" fixture in effect, every bundle's provider call
    fails immediately (DisabledProvider) - run() must still produce a
    complete report with a recorded failure per bundle, never raise."""
    import app.ai.eval.run_golden_set as run_module

    monkeypatch.setattr(run_module, "_REPORT_DIR", tmp_path)
    report_path = run(db)
    content = report_path.read_text(encoding="utf-8")
    # every bundle is either a real pilot (found, but AI call fails since
    # disabled) or genuinely absent (skipped) - either way, no crash and
    # no bundle is silently missing from the report.
    accounted_for = content.count("No usable output") + content.count("not found - skipped")
    assert accounted_for == len(GOLDEN_SET)
