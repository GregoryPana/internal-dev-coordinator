"""T10 golden set: real pilot projects x audience, frozen so results are
comparable across prompt versions. No fabricated entries - each bundle is
a real project imported in T6. There are 8 (4 real pilots x 2 audiences),
not exactly the vault plan's "~10" - a 5th/6th pilot would need another
one-shot seed import (out of scope here) rather than padding with
meaningless duplicate entries against the same 4 projects.
"""

from dataclasses import dataclass

from app.vocab import AIAudience

_PILOT_SLUGS = ["cwscx-platform", "cws-pulse-awards", "vas-network-check", "health-fair-2026"]


@dataclass(frozen=True)
class GoldenBundleSpec:
    label: str
    project_slug: str
    audience: AIAudience


GOLDEN_SET: list[GoldenBundleSpec] = [
    GoldenBundleSpec(f"{slug} - {audience.value}", slug, audience)
    for slug in _PILOT_SLUGS
    for audience in (AIAudience.DEVELOPER, AIAudience.MANAGER)
]
