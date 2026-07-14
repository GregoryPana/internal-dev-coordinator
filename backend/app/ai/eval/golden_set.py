"""T10 golden set: real pilot projects x audience, with per-case claim
checks (added 2026-07-14 from Gregory's v1 evaluation findings).

Each case now carries machine-checkable reference criteria:
- expected_facts: any-of groups - at least one phrase from each group must
  appear somewhere in the output (case-insensitive);
- prohibited_patterns: regexes that must NOT match the output - each one
  encodes a specific failure observed in the v1 evaluation (e.g. VAS
  "diagnosed" being upgraded to "resolved").

These are an automated pre-screen to make human scoring more consistent;
they do not replace the human rubric.
"""

from dataclasses import dataclass, field

from app.vocab import AIAudience

# Encodes the v1 failure: SMSC auth was DIAGNOSED (isolated to auth
# rejection), never confirmed resolved.
_VAS_NOT_RESOLVED = (
    r"resolv\w*[^.]{0,60}(smsc|auth)",
    r"(smsc|auth\w*)[^.]{0,60}(was|were|been|are|is)\s+(resolved|fixed)",
    r"fix\w*\s+(have\s+)?resolved[^.]{0,40}auth",
)

# Encodes the v1 failure: EXIT.md is recorded as current - claiming an
# exit guide/doc is missing is a matrix contradiction.
_CWSCX_EXIT_EXISTS = (
    r"(exit[\s_]*(guide|doc\w*|md)|exit\.md)[^.]{0,40}(missing|absent|lack)",
    r"(missing|lack\w*|absent)[^.]{0,50}exit[\s_]*(guide|doc\w*|md)",
)

# Invented organisational actions observed in v1 manager outputs.
_NO_INVENTED_ORGS = (r"\bdevops\b", r"escalat\w*[^.]{0,40}accountability")


@dataclass(frozen=True)
class GoldenBundleSpec:
    label: str
    project_slug: str
    audience: AIAudience
    # any-of groups: each inner list is satisfied by any one phrase.
    expected_facts: tuple = ()
    prohibited_patterns: tuple = ()


def _spec(slug: str, audience: AIAudience, expected=(), prohibited=()) -> GoldenBundleSpec:
    return GoldenBundleSpec(
        label=f"{slug} - {audience.value}",
        project_slug=slug,
        audience=audience,
        expected_facts=tuple(tuple(g) for g in expected),
        prohibited_patterns=tuple(prohibited),
    )


GOLDEN_SET: list[GoldenBundleSpec] = [
    _spec(
        "cwscx-platform", AIAudience.DEVELOPER,
        expected=[["mystery shopper", "dmz", "smoke"]],
        prohibited=_CWSCX_EXIT_EXISTS,
    ),
    _spec(
        "cwscx-platform", AIAudience.MANAGER,
        prohibited=_CWSCX_EXIT_EXISTS + _NO_INVENTED_ORGS,
    ),
    _spec(
        "cws-pulse-awards", AIAudience.DEVELOPER,
        expected=[["smtp", "entra"], ["maria", "p&c", "acceptance"]],
        prohibited=_NO_INVENTED_ORGS,
    ),
    _spec(
        "cws-pulse-awards", AIAudience.MANAGER,
        prohibited=_NO_INVENTED_ORGS
        + (r"ceo[^.]{0,60}(final|overall|project)\s*(approval|acceptance)",),
    ),
    _spec(
        "vas-network-check", AIAudience.DEVELOPER,
        expected=[["diagnos", "isolat", "identif"], ["handover", "ownership"]],
        prohibited=_VAS_NOT_RESOLVED,
    ),
    _spec(
        "vas-network-check", AIAudience.MANAGER,
        expected=[["handover", "ownership"]],
        prohibited=_VAS_NOT_RESOLVED,
    ),
    _spec(
        "health-fair-2026", AIAudience.DEVELOPER,
        # The hard deadlines must be surfaced (v1 omitted them).
        expected=[["2026-07-31", "2026-08-07", "july 31", "august 7"], ["ohse"]],
        prohibited=(r"(likely|probably)[^.]{0,60}(implemented|part of the backend)",),
    ),
    _spec(
        "health-fair-2026", AIAudience.MANAGER,
        expected=[["2026-07-31", "2026-08-07", "july 31", "august 7"]],
        prohibited=_NO_INVENTED_ORGS,
    ),
]
