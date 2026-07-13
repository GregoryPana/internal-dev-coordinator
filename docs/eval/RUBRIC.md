# AI project-summary rubric (T10)

Scores the structured output of the T9 project-summary task
(`task_type=project_summary`) against the golden set (`docs/eval/golden_set_report_*.md`).
Per the MVP Implementation Plan: **Gregory scores this, on every prompt
version change** - it is a human judgment call, not automated. This file
defines what each dimension means so scoring is consistent across runs.

## Dimensions

Score each 1-5. 1 = clearly fails, 3 = acceptable with reservations, 5 = excellent.

| Dimension | What it means | Fails (1-2) looks like | Passes (4-5) looks like |
|---|---|---|---|
| **Grounded** | Every claim traces to something in the source bundle (project fields, status events, docs matrix) - no invented facts, integrations, dates, or people. | Mentions a system, deadline, or person not in the bundle. | Every sentence could be pointed back to a specific bundle field. |
| **Accurate** | What it says about the bundle is correct - no misreading of status/phase/priority, no flipped gap/required logic, no wrong dates. | States status="blocked" for an active project, or claims a doc exists when the matrix shows it missing. | Status, phase, gaps and dates match the bundle exactly. |
| **Complete** | Covers what a reader of this audience actually needs - doesn't omit an obvious blocker, a real documentation gap, or the current next action. | Ignores a real blocker or missing-required-doc that's clearly in the bundle. | Surfaces the material facts a developer/manager would want first. |
| **Safe** | No secrets/PII, no fabricated business/legal claims, appropriately labeled as a draft, stale caveat present when the project is stale. | Missing the stale caveat on a stale project; states something as fact that should be a caveat/assumption. | Caveats and assumptions are used correctly; `requires_human_review` is respected in tone. |
| **Useful** | The `recommended_next_actions` are concrete and actionable, not generic filler. | "Continue development" / "monitor progress" with no specifics. | Next actions a specific person could act on this week. |

## Pass threshold

A golden-bundle result **passes** if every dimension scores >= 3 **and**
Grounded/Safe both score >= 4 (a summary that invents facts or omits a
safety caveat should not pass even if generally "useful"). Adjust this
threshold here if it proves too strict or too loose after the first
scoring pass - this is a starting definition, not fixed policy.

## Process

1. Run `python -m app.ai.eval.run_golden_set` from `backend/` (real
   provider call per golden bundle - see its own docstring for cost/rate
   notes).
2. It writes `docs/eval/golden_set_report_<prompt_version>_<date>.md`
   with the real generated output for all 8 golden bundles plus a blank
   scoring table.
3. Gregory fills in the scores directly in that file.
4. Re-run whenever `project_summary__developer__v*.md` or
   `project_summary__manager__v*.md`'s version bumps, so results stay
   comparable prompt-version to prompt-version.
