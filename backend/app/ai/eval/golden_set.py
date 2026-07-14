"""Golden set: real pilot projects x audience, with per-case reference
criteria (harness v3, 2026-07-14, per docs/eval/HERMES_EVALUATION_V2_2026-07-14.md).

Reference criteria per case:
- expected_facts: any-of groups - at least one phrase from each group must
  appear in the output (case-insensitive);
- prohibited_patterns: NARROW regexes for failures that cannot be expressed
  structurally (invented orgs, dependency widening, vague dates);
- no_resolved_subjects: subject terms for the clause-scoped state-transition
  check in run_golden_set (replaces the broad v2 cross-clause regexes that
  produced both false positives and false negatives - Hermes finding #2/#P0);
- documentation-gap correctness is checked STRUCTURALLY against the live
  matrix by the runner, not with prose regexes (Hermes finding #3).

These are an automated pre-screen to make human scoring more consistent;
they are heuristics, never a rubric pass (Hermes finding #7).
"""

from dataclasses import dataclass

from app.vocab import AIAudience

# Invented organisational actions observed in v1/v2 manager outputs.
_NO_INVENTED_ORGS = (r"\bdevops\b", r"escalat\w*[^.]{0,40}accountability")

# Exact recorded deadlines must not be replaced by vague quarter wording
# (Hermes v2 finding: "Q3 2026 deadline" is invented).
_NO_VAGUE_QUARTERS = (r"\bq[1-4][\s-]*20\d\d\b",)


@dataclass(frozen=True)
class GoldenBundleSpec:
    label: str
    project_slug: str
    audience: AIAudience
    # any-of groups: each inner list is satisfied by any one phrase.
    expected_facts: tuple = ()
    prohibited_patterns: tuple = ()
    # Clause-scoped: a clause mentioning any of these subjects must not
    # claim resolution/fixing (see check_state_transitions in the runner).
    no_resolved_subjects: tuple = ()


def _spec(slug: str, audience: AIAudience, expected=(), prohibited=(), no_resolved=()) -> GoldenBundleSpec:
    return GoldenBundleSpec(
        label=f"{slug} - {audience.value}",
        project_slug=slug,
        audience=audience,
        expected_facts=tuple(tuple(g) for g in expected),
        prohibited_patterns=tuple(prohibited),
        no_resolved_subjects=tuple(no_resolved),
    )


GOLDEN_SET: list[GoldenBundleSpec] = [
    _spec(
        "cwscx-platform", AIAudience.DEVELOPER,
        expected=[["mystery shopper", "dmz", "smoke"]],
    ),
    _spec(
        "cwscx-platform", AIAudience.MANAGER,
        prohibited=_NO_INVENTED_ORGS,
    ),
    _spec(
        "cws-pulse-awards", AIAudience.DEVELOPER,
        expected=[["smtp", "entra"], ["maria", "p&c", "acceptance"]],
        prohibited=_NO_INVENTED_ORGS,
    ),
    _spec(
        "cws-pulse-awards", AIAudience.MANAGER,
        prohibited=_NO_INVENTED_ORGS + (
            # Golden Ticket CEO/Naadir dependency must stay scoped - not
            # widened into overall approval or business continuity
            # (Hermes v2: run 1 evaded the v2 regex with exactly this).
            r"(ceo|naadir)[^.]{0,80}(final|overall|project)\s*(approval|acceptance)",
            r"business\s+continuity[^.]{0,80}(ceo|naadir|sign[\s-]*off)",
            r"(ceo|naadir)[^.]{0,80}business\s+continuity",
        ),
    ),
    _spec(
        "vas-network-check", AIAudience.DEVELOPER,
        expected=[["diagnos", "isolat", "identif"], ["handover", "ownership"]],
        no_resolved=("smsc", "authentication", "auth rejection"),
    ),
    _spec(
        "vas-network-check", AIAudience.MANAGER,
        expected=[["handover", "ownership"]],
        no_resolved=("smsc", "authentication", "auth rejection"),
    ),
    _spec(
        "health-fair-2026", AIAudience.DEVELOPER,
        expected=[["2026-07-31", "2026-08-07", "july 31", "august 7"], ["ohse"]],
        prohibited=_NO_VAGUE_QUARTERS + (
            r"(likely|probably)[^.]{0,60}(implemented|part of the backend)",
        ),
    ),
    _spec(
        "health-fair-2026", AIAudience.MANAGER,
        expected=[["2026-07-31", "2026-08-07", "july 31", "august 7"]],
        prohibited=_NO_INVENTED_ORGS + _NO_VAGUE_QUARTERS + (
            # "pending/incomplete" must not become "delayed" unless delay
            # is recorded (Hermes v2: "Entra backend authorization delays").
            r"authori[sz]ation\s+delays?",
        ),
    ),
]
