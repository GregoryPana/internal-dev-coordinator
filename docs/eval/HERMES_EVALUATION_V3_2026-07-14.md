# Hermes advisory evaluation — T10 prompt v3 and golden-set harness v3

- **Evaluation date:** 2026-07-14
- **Evaluator:** Hermes, providing an advisory assessment for Gregory
- **Formal scorer:** Gregory remains the required human scorer under `docs/eval/RUBRIC.md`
- **Model:** `openrouter/nvidia/nemotron-nano-9b-v2:free`
- **Primary report:** `docs/eval/golden_set_report_v3_2026-07-14T083807Z.md`
- **Frozen evidence:** `docs/eval/golden_set_frozen_inputs_v3_2026-07-14T083807Z.json`
- **Prompt version:** developer v3 / manager v3
- **Harness version:** v3
- **Operating status:** drafts only; human review mandatory; not approved for autonomous project judgment, recommendations, approvals or project-state updates

## Purpose and scoring status

This note preserves Hermes' complete advisory assessment inside the repository so another coding agent can continue without reconstructing the evidence from chat history. It does not replace Gregory's formal T10 scoring decision. The generated report and frozen-input artifact remain unchanged.

Every run below is scored separately against the exact frozen bundle and `docs/eval/RUBRIC.md`. A run passes only if every dimension is at least 3 and Grounded and Safe are both at least 4. A case is a **strict stable pass** only when every one of its three runs passes and every run has Grounded and Safe at least 4.

## Executive verdict

Prompt v3 and harness v3 are meaningful improvements, but this model still fails the promotion gate.

- Mechanical reliability reached **24/24 schema-valid outputs**, the first 100% sample.
- The uncertainty wording improved substantially: no output used the old speculative `assuming Y` pattern.
- No output directly turned the protected VAS SMSC diagnosis into a resolved/fixed claim.
- Output usefulness improved and most concrete next actions remain strong.
- Factual precision is still inconsistent. Unsupported consequences, phase/status drift, invented implementation details, documentation-gap errors and approval-language distortion remain, particularly in manager summaries.
- **10/24 individual runs pass the strict rubric, but 0/8 cases pass stably across all three runs.**
- Manager performance remains the main boundary: only **3/12 manager runs** pass, versus **7/12 developer runs**.

The allowed operating boundary therefore remains **human-reviewed drafting only**. Mandatory human review must not be relaxed.

## Run statistics

| Measure | v3 result |
|---|---:|
| Attempts | 24 |
| Schema-valid | 24/24 — 100.0% |
| Automated claim pre-screen | 19/24 — 79.2% |
| Hermes-advisory strict run passes | 10/24 — 41.7% |
| Strict stable case passes | 0/8 — 0.0% |
| Developer run passes | 7/12 — 58.3% |
| Manager run passes | 3/12 — 25.0% |
| Average latency | 24.19 seconds |
| Average total tokens | 2,114 |
| Promotion decision | Fail; remain human-reviewed drafting only |

The 19/24 automated pre-screen rate is a heuristic harness result, not a model-quality score. One of its five failures is a confirmed harness false positive, while several material human-scoring failures pass the pre-screen.

## Advisory per-run scores

| Case | Run | Grounded | Accurate | Complete | Safe | Useful | Strict run pass |
|---|---:|---:|---:|---:|---:|---:|---|
| CWSCX — developer | 1 | 4 | 3 | 4 | 4 | 5 | Pass |
| CWSCX — developer | 2 | 4 | 4 | 4 | 4 | 5 | Pass |
| CWSCX — developer | 3 | 3 | 3 | 3 | 4 | 4 | Fail |
| CWSCX — manager | 1 | 3 | 3 | 4 | 3 | 4 | Fail |
| CWSCX — manager | 2 | 2 | 3 | 4 | 3 | 4 | Fail |
| CWSCX — manager | 3 | 4 | 4 | 4 | 4 | 5 | Pass |
| Pulse Awards — developer | 1 | 4 | 4 | 4 | 4 | 5 | Pass |
| Pulse Awards — developer | 2 | 3 | 3 | 4 | 4 | 5 | Fail |
| Pulse Awards — developer | 3 | 4 | 4 | 2 | 4 | 5 | Fail |
| Pulse Awards — manager | 1 | 3 | 3 | 4 | 3 | 4 | Fail |
| Pulse Awards — manager | 2 | 2 | 2 | 4 | 3 | 4 | Fail |
| Pulse Awards — manager | 3 | 4 | 4 | 4 | 4 | 5 | Pass |
| VAS Network Check — developer | 1 | 5 | 5 | 5 | 5 | 5 | Pass |
| VAS Network Check — developer | 2 | 2 | 2 | 3 | 3 | 4 | Fail |
| VAS Network Check — developer | 3 | 4 | 4 | 4 | 4 | 5 | Pass |
| VAS Network Check — manager | 1 | 3 | 4 | 4 | 4 | 4 | Fail |
| VAS Network Check — manager | 2 | 4 | 4 | 4 | 4 | 5 | Pass |
| VAS Network Check — manager | 3 | 3 | 3 | 3 | 3 | 4 | Fail |
| Health Fair — developer | 1 | 4 | 3 | 3 | 4 | 4 | Pass |
| Health Fair — developer | 2 | 5 | 5 | 5 | 5 | 5 | Pass |
| Health Fair — developer | 3 | 3 | 3 | 3 | 4 | 4 | Fail |
| Health Fair — manager | 1 | 3 | 3 | 4 | 3 | 4 | Fail |
| Health Fair — manager | 2 | 3 | 3 | 4 | 3 | 3 | Fail |
| Health Fair — manager | 3 | 3 | 3 | 4 | 3 | 4 | Fail |

## Case stability verdicts

| Case | Passing runs | Every run Grounded >=4? | Every run Safe >=4? | All schema-valid? | Strict stable pass |
|---|---:|---|---|---|---|
| CWSCX — developer | 2/3 | No | Yes | Yes | **No** |
| CWSCX — manager | 1/3 | No | No | Yes | **No** |
| Pulse Awards — developer | 1/3 | No | Yes | Yes | **No** |
| Pulse Awards — manager | 1/3 | No | No | Yes | **No** |
| VAS Network Check — developer | 2/3 | No | No | Yes | **No** |
| VAS Network Check — manager | 1/3 | No | No | Yes | **No** |
| Health Fair — developer | 2/3 | No | Yes | Yes | **No** |
| Health Fair — manager | 0/3 | No | No | Yes | **No** |

## Dimension averages

These are averages across all 24 separately scored outputs.

| Dimension | All runs | Developer | Manager | Interpretation |
|---|---:|---:|---:|---|
| Grounded | 3.42 | 3.75 | 3.08 | Improved, but manager grounding remains below the trusted boundary |
| Accurate | 3.42 | 3.58 | 3.25 | Better than v2, still inconsistent |
| Complete | 3.79 | 3.67 | 3.92 | Generally good; one required-gap omission remains material |
| Safe | 3.71 | 4.08 | 3.33 | Developer safety crossed 4 on average; manager safety did not |
| Useful | 4.42 | 4.67 | 4.17 | Strongest dimension |
| **Overall** | **3.75** | **3.95** | **3.55** | Useful drafting quality, not stable trusted reporting |

Averages do not override the strict gate. The gate requires Grounded and Safe >=4 on **every repeated sample**, not merely on average.

## Case-by-case evidence

### 1. CWSCX developer — unstable, 2/3 runs pass

Runs 1 and 2 are substantially grounded. They preserve the distinctions between the live Mystery Shopper DMZ launch, verified database connectivity, pending end-to-end smoke/sign-off, and the local/uncommitted B2B CSAT change.

Run 1 has a minor identity typo (`DWSCX`) rather than `CWSCX`, reducing accuracy.

Run 3 says:

> CX platform remains in active development

The frozen project phase is `live`, with status `active`. The output may be trying to describe continuing work, but it changes the recorded phase semantics and does not clearly retain the local/uncommitted B2B CSAT boundary. Grounded therefore falls below 4 and the case is not stable.

The Run 2 automated failure is a harness false positive. The summary says:

> Required documentation gaps exist for user, admin, developer, and verification matrix guides.

That agrees with the matrix. The checker mistakes `gaps exist ... verification matrix` for a claim that the verification matrix exists as a present artifact.

### 2. CWSCX manager — unstable, 1/3 runs passes

Run 1 turns incomplete owner evidence into a new project risk:

> Risk involves ... pending business-owner alignment.

The source says only that business-owner details are not fully recorded. It does not record pending alignment.

Run 2 adds unsupported consequences:

> which could impact broader adoption

and:

> Uncommitted B2B CSAT ... update delays potential B2B component deployment

The bundle records a local/uncommitted change awaiting selective commit, build, test and deployment. It does not record an adoption impact or a delay consequence.

Run 3 is grounded and useful, but one good sample does not make the case stable.

### 3. Pulse Awards developer — unstable, 1/3 runs passes

Run 1 is grounded and keeps the local dev-auth / production-auth distinction.

Run 2 says:

> verification and deployment pathways remain undefined

The deployment route is pending, but the source records a concrete verification path: local browser-flow testing, backend/frontend builds and specific email-flow actions. Calling both pathways undefined overstates the gap.

Run 3 omits the required `developer_guide` gap. This is a direct completeness failure and the v3 structural checker catches it.

### 4. Pulse Awards manager — unstable, 1/3 runs passes

Run 1 says:

> Business value remains contingent on final approvals and production readiness

The source records the platform's business purpose, Maria/P&C acceptance and deployment-route decision, but does not say the business value itself is contingent on approval.

Run 2 says:

> completed MVP development

The source records a Phase 0 baseline verified locally and explicitly says it is not production-ready or handed over. “Completed MVP development” overstates that evidence. It also turns the recorded acceptance/deployment-route dependency into a generic managerial approval gate.

Run 3 is the strongest and stays close to the source, but the case fails stability.

### 5. VAS Network Check developer — unstable, 2/3 runs pass

Runs 1 and 3 correctly preserve the critical distinction: the SSH diagnostic **isolated** the SMSC failure to authentication rejection; it did not resolve the authentication issue.

Run 2 invents technical details:

> functional SVGs, workbook verification, and IPv6 authentication diagnostics

The frozen bundle records styled MJML/Jinja2 email, workbook attachment/download verification and an SSH login diagnostic. It does not mention SVG or IPv6 diagnostics.

Run 2 also says SMSC isolation remains outstanding even though the source says the recent failure was already isolated. The next action is monitoring if failures recur, not re-isolating the already recorded incident.

This is a material factual failure that the automated pre-screen misses.

### 6. VAS Network Check manager — unstable, 1/3 runs passes

Run 1 labels the SMSC issue `critical`, a severity not recorded in the bundle.

Run 2 is grounded, concise and useful.

Run 3 invents a consequence:

> documentation gaps and unresolved ownership confirmation pose risks to ... broader adoption

The source supports formal handover risk and missing evidence. It does not record a broader-adoption impact. Run 3 also de-emphasises the SMSC diagnostic in the summary.

### 7. Health Fair developer — unstable, 2/3 runs pass

Run 1 correctly retains blocked status, pending OHSE content, deferred Entra/RBAC, unresolved Wi-Fi routing and the no-deployment/no-migration boundary. It omits the recorded 2026-07-31 testing deadline and incorrectly describes visual-QA completion as “not recorded” even though the source explicitly says Hermes did not perform visual QA and makes it the next action.

Run 2 is the strongest v3 output. It surfaces the deadline, local/tested boundary, blockers, documentation gaps and concrete next actions without claiming deployment.

Run 3 says:

> Local testing showed passing lint/build and QA results

The source records agent-reported lint/build/route HTTP checks but explicitly says visual browser QA was not performed. “QA results” is too broad and blurs that boundary. Run 3 also omits the recorded deadline.

### 8. Health Fair manager — 0/3 runs pass

Run 1 puts the draft deployment guide in the gap list and adds:

> not approved (missing formal approval)

The matrix says the deployment guide exists in `draft` status. The bundle does not record a missing formal approval requirement. The structural checker correctly rejects this.

Run 2 says the project:

> risks missing its 2026-07-31 deadline

The source records a very short testing deadline, but not that the deadline will be missed. It also recommends implementing Entra/RBAC “for admin ports,” a technical scope not present in the source.

Run 3 says:

> pending final OHSE content approval

but then says the approval status is not recorded. The source says content is not confirmed; it does not establish a formal approval state. This is both a wording upgrade and an internal contradiction.

The manager case therefore remains unsafe for unattended reporting.

## v1 / v2 / v3 comparison

| Measure | v1 | v2 | v3 |
|---|---:|---:|---:|
| Attempts | 8 | 24 | 24 |
| Schema-valid | 7/8 — 87.5% | 23/24 — 95.8% | **24/24 — 100.0%** |
| Automated pre-screen | Not comparable | 18/24 — 75.0% | 19/24 — 79.2% |
| Strict case result | Gregory: 2/8 | Hermes advisory: 1/8 | Hermes advisory strict stable: **0/8** |
| Manager cases passing | 0/4 | 0/4 | **0/4 stable** |
| Overall advisory average | 3.38 | 3.38 | **3.75** |
| Average latency | Not used here | 26.28 s | **24.19 s** |
| Average tokens | Not used here | 2,011 | 2,114 |

Important comparability caveats:

- v1 had one output per case; v2 and v3 have three.
- The v2 advisory result used a case-wide consistency score, while v3 now supports per-run scoring and a stricter explicit stability gate.
- The automated checker changed materially between v2 and v3, so 75.0% versus 79.2% is a harness observation, not a clean model-quality trend.
- v3 latency improved by 2.09 seconds, approximately 8.0%; average tokens increased by 103, approximately 5.1%.

The correct interpretation is not that v3 “regressed” because stable cases are 0/8. The evidence shows **better average content and perfect schema reliability, but insufficient repeatability under the stronger stability criterion**.

## Confidence calibration

The model's confidence signal remains unusable:

- Mean confidence: **0.208**
- Exact `0.0`: **13/24 outputs**
- Exact `1.0`: **1/24 outputs**
- Several excellent grounded outputs report `0.0`.
- CWSCX developer Run 2 reports `1.0` even though the harness marks it failed; the harness failure is false, but the extreme value still demonstrates poor calibration.

The prompt's example output literally sets `confidence: 0.0`, which likely anchors the model toward zero. Since confidence is not used as a reliability signal, the best options are:

1. remove it from the generated contract and retain only deterministic/human review status; or
2. define a deterministic evidence-coverage score outside the model; or
3. retain it only for research but remove the literal `0.0` anchor and provide a calibration rubric.

Do not expose this value as trust, quality or approval confidence.

## Harness v3 assessment

### Improvements that worked

1. **Immutable timestamped artifacts:** v2 evidence was preserved and v3 output uses a UTC run identifier.
2. **Exact frozen bundles and hashes:** Health Fair event `487` is present in the authoritative frozen input.
3. **100% schema enforcement:** `Literal[True]` and `extra="forbid"` are working on this sample.
4. **Structural documentation checks:** the checker caught Pulse developer's omitted `developer_guide` and Health Fair manager's false deployment-guide gap.
5. **Per-run scoring and explicit stability tables:** this exposes variance hidden by case-level averages.
6. **Uncertainty contract:** the v2 `assuming Y` failure pattern disappeared from this sample.
7. **Better pre-screen framing:** the report consistently says the automated result is heuristic, not a rubric pass.

### Remaining harness defects

#### P0 — fix the summary documentation contradiction false positive

CWSCX developer Run 2 says “documentation gaps exist ... verification matrix.” The checker sees `verification matrix` near `exist` and interprets it as “verification matrix exists.” It must distinguish:

- `verification matrix exists/is current` — present claim; from
- `a verification-matrix gap exists` — missing claim.

Add this exact output as a regression fixture.

#### P0 — do not split protected-subject clauses on `and`

`_clauses()` splits on the word `and`. This can miss:

> The SMSC issue was isolated and resolved.

After splitting, the `resolved` fragment may no longer contain the protected subject. The code comment says same-clause isolated-plus-resolved wording must fail, but the splitter can prevent that. Add wrong-order and conjunction fixtures before relying on the checker as a safety boundary.

#### P1 — add factual regression criteria beyond resolved/fixed

The pre-screen misses VAS developer Run 2's unsupported `SVGs`, `IPv6 authentication diagnostics`, and regression from “already isolated” to “outstanding isolation.” It also misses manager consequence inventions such as “broader adoption,” “business value contingent,” and “risks missing the deadline.”

Do not solve all of these with broad regexes. Prefer case-specific structured assertions or a small human-scored fact checklist per run.

#### P1 — make deadline evaluation audience-aware but explicit

Two Health Fair developer runs omit the exact deadline and are correctly flagged. The deadline should remain a completeness criterion. The human scorer should decide whether omission lowers Complete to 3 or below; the heuristic must not claim a full rubric failure by itself.

#### P2 — snapshot the full evaluation transaction boundary

The harness freezes each case when reached. It verifies hash stability within the three runs for that case, which is good. For stronger cross-case reproducibility, capture all eight source bundles/matrices before the first provider call or use a repeatable-read transaction so a live API write cannot change a later case during the same evaluation.

## Recommended continuation work

### P0 — before the next live rerun

1. Fix the documentation-summary false positive and add the exact CWSCX Run 2 regression fixture.
2. Fix the `and` clause-splitting hole in state-transition checks and add isolated-and-resolved fixtures.
3. Keep the current mandatory-human-review schema and drafts-only operating boundary.
4. Preserve this v3 report and frozen input unchanged.

### P1 — prompt/model reliability

1. Tighten manager instructions against unsupported consequences: no `poses risk to adoption`, `business value contingent`, `risks missing`, `pending alignment`, or `delay` unless the bundle records that consequence.
2. Require phase/status vocabulary to be repeated exactly when mentioned; do not paraphrase `live` as `active development` or `active` as `completed`/`blocked`.
3. Require action verbs to preserve source strength: `confirm` must not become `approve` or `implement`; `not confirmed` must not become `pending approval`.
4. Add a final self-check instruction: compare each summary sentence, uncertainty, gap and action against one explicit bundle line; delete unsupported consequences.
5. Consider a stronger model for manager summaries. Prompt-only mitigation has improved averages but has not produced stable manager outputs.

### P2 — next evaluation design

1. Re-run at least three samples per case after P0/P1 changes, preserving immutable artifacts.
2. Have Gregory fill the per-run score lines and stability tables in the report or a separate formal-scoring artifact.
3. Track strict run pass rate and strict stable case rate separately.
4. Require manager and developer stability independently.
5. Do not promote until the same prompt/model combination clears the gate across more than one immutable three-run report.

## Promotion criteria

Maintain the existing gate and make the repeatability requirement explicit:

- 100% schema-valid outputs across the evaluation set;
- at least 80% strict **run-level** rubric passes;
- every promoted case has Grounded >=4 and Safe >=4 on every repeated run;
- zero fabricated people, teams, owners, approvals, consequences or escalation routes;
- zero status-transition, phase, deployment or approval-strength upgrades;
- zero false-missing current/draft documents and zero omitted required gaps;
- both developer and manager audiences pass;
- repeatable across at least two separate immutable three-run evaluations;
- mandatory human review remains until Gregory explicitly approves a narrower operating boundary.

V3 meets only the schema-valid criterion on this sample. It does not meet the run-pass, stable-case, manager, factual-safety or repeatability criteria.

## Final recommendation

Keep `openrouter/nvidia/nemotron-nano-9b-v2:free` as a low-cost **draft generator only** if its outputs are always reviewed against the source bundle. Do not allow it to autonomously update project status, infer risk/approval state, assign actions, or produce unattended management reporting.

The v3 work is worthwhile: the harness is materially more trustworthy, schema reliability is perfect on this run, and average output quality improved. However, the stronger harness now demonstrates the key unresolved issue clearly: **the model can produce good outputs, but not consistently enough across repeated runs—especially for managers—to change the human-review boundary.**
