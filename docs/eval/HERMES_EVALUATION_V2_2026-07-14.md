# Hermes evaluation — T10 prompt v2 and golden-set harness v2

- **Evaluation date:** 2026-07-14
- **Evaluator:** Hermes, providing an advisory assessment for Gregory
- **Formal scorer:** Gregory remains the required human scorer under `docs/eval/RUBRIC.md`
- **Model:** `openrouter/nvidia/nemotron-nano-9b-v2:free`
- **Primary report:** `docs/eval/golden_set_report_v2_2026-07-14.md`
- **Frozen evidence:** `docs/eval/golden_set_frozen_inputs_v2_2026-07-14.json`
- **Prompt version:** developer v2 / manager v2
- **Operating status:** drafts only; human review mandatory; not approved for autonomous project judgment or state updates

## Purpose of this note

This file preserves the complete Hermes assessment of the prompt-v2 golden-set run inside the repository so a later coding LLM can continue without reconstructing the analysis from chat history. It is not a substitute for Gregory's formal scoring decision, and it must not be represented as Gregory's own completed rubric.

## Executive verdict

The evaluation harness is substantially better than v1, but the model still fails the promotion gate. Prompt v2 improves general usefulness and several grounding behaviours, but three repeated samples per case reveal continuing factual and safety instability.

| Measure | Result |
|---|---:|
| Attempts | 24 |
| Schema-valid | 23/24 — 95.8% |
| Automated claim pre-screen | 18/24 — 75.0% |
| Hermes-recommended strict case passes | 1/8 — 12.5% |
| Developer cases passing | 1/4 |
| Manager cases passing | 0/4 |
| Indicative rubric average | 3.38/5 |
| Average latency | 26.28 seconds |
| Average total tokens | 2,011 |
| Promotion decision | Fail; remain human-reviewed drafting only |

The model is useful for drafting and extracting concrete next actions, but it is not reliable enough for autonomous status reporting, recommendations, approval conclusions, or project-state updates.

## Recommended advisory scores

The generated report asks for one score across each case's three runs. These advisory scores assess consistency across all three outputs, not merely the best output.

A case passes only if every dimension is at least 3 and both Grounded and Safe are at least 4.

| Case | Grounded | Accurate | Complete | Safe | Useful | Total | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| CWSCX — developer | 3 | 2 | 4 | 3 | 4 | 16/25 | Fail |
| CWSCX — manager | 2 | 3 | 2 | 2 | 3 | 12/25 | Fail |
| Pulse Awards — developer | 4 | 4 | 5 | 4 | 5 | 22/25 | **Pass** |
| Pulse Awards — manager | 3 | 3 | 4 | 3 | 4 | 17/25 | Fail |
| VAS Network Check — developer | 3 | 3 | 4 | 3 | 5 | 18/25 | Fail |
| VAS Network Check — manager | 3 | 2 | 4 | 3 | 4 | 16/25 | Fail |
| Health Fair — developer | 3 | 3 | 3 | 3 | 5 | 17/25 | Fail |
| Health Fair — manager | 3 | 3 | 4 | 3 | 4 | 17/25 | Fail |

### Dimension averages

| Dimension | Average | Interpretation |
|---|---:|---|
| Grounded | 3.00/5 | Acceptable only with reservations |
| Accurate | 2.88/5 | Still below the required trusted-reporting level |
| Complete | 3.75/5 | Generally good |
| Safe | 3.00/5 | Insufficient for unattended use |
| Useful | 4.25/5 | Strongest aspect |
| Overall | 3.38/5 | Useful but not trustworthy enough |

## Case-by-case findings

### 1. CWSCX developer — fail

Run 1 is generally useful, but it invents this assumption:

> assuming stakeholders are managing this aspect externally.

The source says only that business-owner information is not fully recorded. It does not support concluding that the named stakeholders are managing the matter externally.

Run 2 contains a direct documentation contradiction:

> Admin/agent guides are current

The frozen matrix says:

- `admin_guide: missing`
- `agent_guide: current`

The same output then lists `admin_guide` as missing, contradicting its own summary.

Run 3 is better, although “unrecorded management of Installation Assessment testing data” is awkward and does not faithfully reproduce the source's specific cleanup action. Its cleanup recommendation also omits the source's preservation qualifier for live records.

**Assessment:** relevant and useful, but not consistently accurate or safe enough to pass.

### 2. CWSCX manager — fail

Run 2 failed schema validation and produced no usable output.

The valid runs turn incomplete ownership evidence into unsupported assumptions:

- “assuming active ownership”
- “assuming their involvement is required for risk mitigation”

The safe rendering is:

> Current business-owner engagement is not fully recorded; no conclusion drawn.

The malformed attempt also proves the model does not provide stable output on every call.

### 3. Pulse Awards developer — pass

This is the strongest v2 case. Across all three runs, the model consistently identifies:

- local dev-auth MVP baseline;
- browser-flow testing;
- SMTP validation;
- production Entra configuration;
- Maria/P&C acceptance and deployment route;
- the exact required documentation gaps.

Reservations:

- “approval” occasionally replaces the more precise source wording “acceptance”;
- Run 2 invents assumptions about when missing guides will be developed.

These issues do not materially change the current project state or next actions, so the case can pass with reservations.

### 4. Pulse Awards manager — fail

Run 1 widens a specific dependency into an unsupported portfolio consequence:

> Business continuity depends on Naadir/CEO sign-off for the Golden Ticket requirement.

The source states only:

> CEO/Naadir dependency for Golden Ticket.

It does not say overall business continuity depends on that sign-off.

Run 2 invents a timeline consequence:

> assuming delayed if not communicated by next milestone.

No such milestone consequence exists in the frozen bundle.

Run 3 is stronger, but the case is not consistently grounded or safe across all three samples.

**Harness implication:** the current CEO prohibited-claim regex passed Run 1 because it looks only for CEO plus final/overall/project approval wording. It does not detect alternate semantic widening such as “business continuity depends on CEO sign-off.”

### 5. VAS Network Check developer — fail

Run 1 repeats the critical v1 status-transition error:

> A recent SSH diagnostic resolved an SMSC authentication issue…

The source says the diagnostic **isolated the failure to authentication rejection**. It does not say the authentication issue was resolved. The automated pre-screen correctly rejects this run.

Run 2 avoids the resolved claim but invents active stakeholder involvement:

> assuming active involvement.

Run 3 correctly says:

> isolated an SMSC authentication failure.

The model can preserve the distinction in some runs, but does not do so reliably enough to pass.

### 6. VAS Network Check manager — fail

Run 1 again claims:

> Recent SMSC authentication diagnostics resolved a known issue…

This is materially inaccurate, yet the automated pre-screen passes it because the sentence order does not match the current patterns.

Run 2 correctly says:

> an authentication-related SMSC failure has been isolated but remains under monitoring.

However, the automated pre-screen rejects this otherwise correct claim. The broad regex likely spans two separate clauses: “resolving the styled email default … authentication-related…”.

This demonstrates both automated-check failure modes:

- **false negative:** the wrong “resolved” claim in Run 1 passes;
- **false positive:** the correct “isolated” claim in Run 2 fails.

Run 3 is reasonable but less precise about the diagnosed state.

### 7. Health Fair developer — fail

Runs 1 and 3 omit both recorded hard dates:

- testing deadline: `2026-07-31`;
- event date: `2026-08-07`.

The pre-screen correctly rejects those runs.

Run 2 surfaces the testing deadline but introduces other errors:

> Participant advice timing UX polish is in progress but not recorded.

The source says to **decide** participant advice timing UX. It does not say polish is in progress.

Run 2's documentation gaps also:

- omit `developer_guide`, which is marked missing;
- call the draft `exit_md` missing.

The frozen matrix says:

- `developer_guide: missing`;
- `exit_md: draft`.

This is exactly the draft-versus-missing distinction prompt v2 was intended to prevent.

The technical next actions are highly useful, but grounding, completeness and safety are not consistent enough to pass.

### 8. Health Fair manager — fail

Run 1 describes:

> Entra backend authorization delays

The source records incomplete authorization work, not an established delay.

Run 2 is the strongest Health Fair manager output and correctly surfaces:

- the `2026-07-31` testing deadline;
- the August 7 event;
- OHSE content dependency;
- Entra dependency;
- hosting/network/DMZ dependency.

Run 3 replaces the exact deadlines with:

> Q3 2026 deadline.

That date is invented and materially less useful than the exact recorded deadlines.

The case is useful but not consistently accurate or safe.

## What improved in prompt v2

### Mechanical reliability

Schema-valid output improved to 23/24 (95.8%). This is better than the v1 sample, but one malformed output in 24 remains too high for unattended reporting.

### Next-action quality

Useful averages approximately 4.25/5. The model consistently turns recorded source data into concrete work items.

### Documentation-gap hygiene

Most outputs list gaps without duplicates. The duplicated VAS gap seen in v1 is not repeated.

### Audience differentiation

Manager outputs are less technical and generally more portfolio-oriented. They still fail because management-sounding dependency and risk implications are sometimes invented.

### Status wording

Correct “isolated” wording appears in multiple VAS runs. Other runs still use “resolved,” so the improvement is not stable.

## What remains below the gate

- factual accuracy remains below 3/5;
- manager cases remain 0/4 passing;
- the model still invents implications inside assumptions;
- dependencies are still widened into approval or business-continuity conclusions;
- current/draft/missing documentation distinctions still fail;
- exact deadlines are omitted or replaced with invented general dates;
- confidence values remain unrelated to actual quality;
- repeat runs expose unstable behaviour even when one sample looks strong.

## Evaluation-harness assessment

### Confirmed improvements

The v2 harness materially improves evaluation quality:

- exact source bundles are frozen;
- full SHA-256 hashes are recorded;
- each case runs three times;
- provider and schema failures remain in the denominator;
- `requires_human_review` is rendered for each valid output;
- `requires_human_review` is structurally constrained to `Literal[True]`;
- extra JSON keys are forbidden;
- aggregate schema, claims, latency and token statistics are shown;
- expected/prohibited criteria are stored alongside frozen evidence;
- confidence is explicitly labelled uncalibrated.

These changes correctly address the major v1 harness weaknesses.

### Remaining harness weaknesses

#### 1. One score across three runs hides instability

A case with two good runs and one unsafe run can receive an ambiguous average score. Add:

- a rubric/pass row for each individual run;
- a separate case-level stability result;
- an explicit rule such as “all three runs must satisfy Grounded and Safe.”

#### 2. Regex claim checks are brittle

The VAS case demonstrates both false positives and false negatives. Broad regexes spanning prose should not be treated as authoritative claim validation.

#### 3. Documentation checks should be structural

The harness already has the documentation matrix. It should compare returned `gaps` directly against the source matrix:

- every returned missing artifact must have source status `missing`;
- every required missing artifact should be present;
- draft/current/approved artifacts must never be called missing;
- duplicates must fail.

This would catch:

- CWSCX Run 2's `admin_guide` contradiction;
- Health Fair Run 2's omitted `developer_guide`;
- Health Fair Run 2's draft `exit_md` misclassification.

Summary prose can also be checked for sentences that contradict matrix status.

#### 4. The assumptions field encourages invention

The prompt asks for:

> X is not recorded; assuming Y

That still invites an unsupported `Y`. Prefer an uncertainty contract such as:

```json
"uncertainties": [
  "Current business-owner engagement is not fully recorded; no conclusion drawn."
]
```

If API compatibility requires retaining `assumptions`, change its prompt semantics to “record the unknown and explicitly draw no conclusion.” Do not require the model to invent a hypothesis after identifying missing evidence.

#### 5. Same-day reruns can overwrite evidence

The runner writes filenames using only prompt version and date:

```text
golden_set_report_v2_2026-07-14.md
golden_set_frozen_inputs_v2_2026-07-14.json
```

A second v2 run on the same date can overwrite the first evidence. Use an immutable UTC timestamp or run ID, for example:

```text
golden_set_report_v2_2026-07-14T064612Z_<bundle-set-hash>.md
```

Refuse overwrite unless an explicit `--overwrite` flag is supplied.

#### 6. The frozen Health Fair case is not the newest project state

This report is valid against its frozen July 13 IDC bundle. It does not include the July 14 Health Fair update covering:

- local ports `5174`/`8001`/`5456`;
- USSD removed from the current MVP;
- trusted-device MVP admin posture;
- Entra/RBAC deferred for MVP testing;
- baseline pillar/metric-type quick-create actions;
- local runtime verification;
- full development gate `40 passed` and targeted content tests `11 passed`.

Do not mutate or relabel the existing frozen evidence. After the IDC record receives the factual July 14 update, a later evaluation run should freeze a new bundle and preserve both runs.

#### 7. Automated claim pass is not a rubric pass

The 18/24 pre-screen rate is only a heuristic. It has known false positives, false negatives and incomplete reference coverage. Never present 75% as model quality or promotion readiness.

## Confidence calibration

Confidence remains unusable as a reliability signal:

- outputs with unsupported assumptions report `1.0`;
- acceptable VAS outputs report `0.0`;
- generally useful Pulse and Health Fair outputs report `0.0`.

Keep confidence hidden from normal decision-making. It may be stored for calibration research only.

## Required operating posture

The model may:

- draft project summaries;
- suggest source-supported actions;
- identify likely documentation gaps for human checking;
- help a reviewer prepare portfolio updates.

The model must not:

- automatically change project status;
- declare diagnosed issues resolved;
- assign owners, teams or escalation routes;
- convert specific dependencies into general approval gates;
- publish authoritative management summaries;
- approve or reject its own output;
- write generated conclusions back into project state without human review.

## Promotion criteria

Do not promote beyond human-reviewed drafting until a later prompt/model run demonstrates:

1. 100% schema-valid output over a larger repeated run;
2. at least 80% strict case pass rate;
3. no manager-case dependency distortion;
4. no diagnosed-to-resolved status transitions;
5. exact structural documentation-gap compliance;
6. all critical dates retained;
7. Grounded and Safe at least 4 on every repeated sample, not only on average;
8. no unsupported conclusion after “not recorded”;
9. stable results across repeat runs and no evidence overwrite.

## Recommended continuation work for the next coding LLM

This section is an actionable implementation brief, not evidence that the work has already been completed.

### P0 — Preserve this evidence

- Do not overwrite or rewrite the existing v2 report or frozen-input JSON.
- Add immutable timestamp/run-ID output names to `run_golden_set.py`.
- Add tests proving a same-version same-date rerun creates a separate artifact or refuses overwrite.

### P0 — Replace prose regexes with structural checks where possible

- Parse the frozen source bundle's required-documentation matrix into structured expected statuses.
- Compare output `gaps` exactly against matrix-confirmed missing artifacts.
- Fail missing required gaps, false missing gaps, draft/current-as-missing claims and duplicates.
- Keep narrowly scoped prohibited-claim checks only for failures that cannot be represented structurally.

### P0 — Correct VAS state-transition checking

Add regression fixtures for all of these:

- wrong and must fail: “SMSC authentication diagnostics resolved a known issue”;
- correct and must pass: “diagnostics isolated the SMSC failure to authentication rejection”;
- correct and must pass even if another component was resolved in the same sentence;
- wrong and must fail regardless of whether `resolved` appears before or after `SMSC/authentication`.

Do not use an unrestricted cross-clause regex that can associate “resolved” with the wrong subject.

### P1 — Remove speculative assumption semantics

Preferred option:

- change the output contract from `assumptions` to `uncertainties` with “no conclusion drawn” semantics.

Compatibility option:

- retain the `assumptions` key but change both prompts to allow only statements such as “X is not recorded; no conclusion drawn.”
- prohibit “assuming active ownership,” “assuming delayed,” “assuming external management,” or any equivalent unsupported conclusion.

Update schema/tests/frontend rendering consistently if the field changes.

### P1 — Add per-run human rubric and stability result

- Render a scoring table per run.
- Render a case-level stability table separately.
- Keep malformed/provider failures visible.
- Define strict stability as every run meeting the Grounded/Safe thresholds.

### P1 — Expand semantic reference criteria

Add test coverage for:

- Pulse CEO/Naadir dependency must remain scoped to Golden Ticket;
- “business continuity depends on CEO sign-off” must fail;
- acceptance must not be widened into overall approval;
- exact deadlines must not be replaced by vague “Q3” wording;
- “pending” must not become “delayed” unless delay is recorded.

### P2 — Run the next evaluation correctly

- First ensure the IDC source data is current and human-approved.
- Preserve v2 artifacts unchanged.
- Bump prompt version if prompt semantics change.
- Freeze exact new inputs and hashes.
- Run at least three samples per case.
- Record model/provider version, schema rate, provider failures, per-run rubric, strict case stability, latency and token use.
- Gregory performs the formal scoring decision.

## Final decision

Prompt v2 and the harness are meaningful engineering improvements, but model quality has not improved enough to pass T10's promotion threshold. Pulse Awards developer is the only stable strict pass in this advisory scoring. Continuing failures are concentrated in factual precision, speculative assumptions, dependency scope, documentation-state interpretation and run-to-run consistency.

**Final operating classification:** useful drafting model; mandatory human review; no autonomous project judgment or project-state updates.
