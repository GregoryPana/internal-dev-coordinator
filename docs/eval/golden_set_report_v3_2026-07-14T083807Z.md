# T10 golden-set report - prompt v3 - 2026-07-14T083807Z

Generated 2026-07-14T08:38:07.698667+00:00 by `python -m app.ai.eval.run_golden_set --runs 3`. See `docs/eval/RUBRIC.md`.
Automated pre-screens are heuristics for the human scorer - never a rubric pass
and never a model-quality metric. Exact source bundles, hashes and the
documentation-matrix state are frozen in `golden_set_frozen_inputs_v3_2026-07-14T083807Z.json`.

## Aggregate stats

- Attempts: 24 (3 run(s) x 8 cases)
- Schema-valid outputs: 24/24
- Automated claim pre-screen passed (heuristic): 19/24
- Avg latency: 24190 ms; avg total tokens: 2114

---

## cwscx-platform - developer

- Project: CWSCX Platform / Customer Experience Platform (`cwscx-platform`)
- Audience: developer
- Source-bundle SHA-256: `6a57135e7860a35890271a8fc57bf2e9e8c0b802f47916470865ff628ae93bde`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The DWSCX Platform for Customer Experience is in an active live phase with a FastAPI backend, React frontend, and PostgreSQL. The Mystery Shopper public DMZ production launch is live with verified DMZ-to-internal PostgreSQL connectivity, but end-to-end smoke/sign-off remains pending. The B2B CSAT threshold/report explanation update is local/uncommitted and requires selective commit, testing, and deployment.

**Uncertainties/assumptions:** Current business-owner engagement (Maria, Dan, David Bedier) is not fully recorded in repo documents; no conclusion drawn.

**Gaps:** user_guide (GAP - missing); admin_guide (GAP - missing); developer_guide (GAP - missing); verification_matrix (GAP - missing)

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off workflow (enroll -> TOTP/login -> DMZ submit -> review queue); Maintain PR-controlled production changes branch; Remove old Installation Assessment testing data while preserving live records

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 1.0
- Automated claim pre-screen (heuristic, not a rubric pass): **FAIL** - summary contradicts matrix: verification_matrix called present but matrix says gap

**Summary:** The CWSCX Platform is live with verified DMZ 2FA/DMZ PostgreSQL connectivity. Mystery Shopper public DMZ smoke/sign-off remains pending. No blockers are recorded. Technology stack includes FastAPI, React, and PostgreSQL. Required documentation gaps exist for user, admin, developer, and verification matrix guides.

**Uncertainties/assumptions:** Current business-owner engagement (Maria, Dan, David Bedier) is not fully recorded in repo docs; no conclusion drawn.

**Gaps:** user_guide (GAP - missing); admin_guide (GAP - missing); developer_guide (GAP - missing); verification_matrix (GAP - missing)

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off (enroll -> TOTP/login -> DMZ survey submit -> internal review queue); Maintain production changes branch/PR control; Remove old Installation Assessment testing data for Bedier while preserving live records

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** Mystery Shopper public DMZ production launch is live with verified DMZ-to-internal PostgreSQL connectivity. CX platform remains in active development with pending end-to-end smoke/sign-off completion for Mystery Shopper. Next actions include finalizing DMZ smoke/sign-off, maintaining PR-controlled production changes, and removing obsolete Installation Assessment testing data. No blockers currently identified.

**Uncertainties/assumptions:** Current business-owner engagement (Maria, Dan, David Bedier) is not fully recorded in repository documentation; no conclusion drawn on their involvement.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off; Maintain production changes branch/PR-controlled; Remove old Installation Assessment testing data while preserving live records

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |


---

## cwscx-platform - manager

- Project: CWSCX Platform / Customer Experience Platform (`cwscx-platform`)
- Audience: manager
- Source-bundle SHA-256: `6a57135e7860a35890271a8fc57bf2e9e8c0b802f47916470865ff628ae93bde`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The CWSCX Platform is live and active with high priority, featuring a recent successful launch of the Mystery Shopper public DMZ. Progress includes verified DMZ-to-internal connectivity and ongoing smoke/sign-off completion. Risk involves incomplete documentation and pending business-owner alignment.

**Uncertainties/assumptions:** Current business-owner engagement is not fully recorded; no conclusion drawn.; B2B CSAT threshold update implementation status is not recorded; no conclusion drawn.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off; Keep production changes branch/PR-controlled; Remove old Installation Assessment testing data for Bedier while preserving live records

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.7
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The CWSCX Platform is active with high priority, currently live for Mystery Shopper public DMZ production after connectivity verification. Business objectives require a unified platform for customer experience data across B2B and other programmes, but pending full smoke/sign-off completion for the DMZ component. Missing documentation includes user guides and verification matrix, which could impact broader adoption.

**Uncertainties/assumptions:** Current business-owner engagement (Maria, Dan, David Bedier) is not fully recorded in repository documentation; no conclusion drawn.; Status of Mystery Shopper public 2FA/DMZ production launch beyond connectivity verification leaves end-to-end smoke/sign-off status unconfirmed; no conclusion drawn.; Uncommitted B2B CSAT threshold/report explanation update delays potential B2B component deployment; no action recorded.; No records of ownership or team responsibility for specific next actions beyond Gregory Panagary; no conclusion drawn.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off; Maintain production changes branch/PR-controlled; Remove old Installation Assessment testing data for Bedier while preserving live records

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.6
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The CWSCX Platform is live and active, supporting customer experience data across B2B, Installation Assessment, and Mystery Shopper programmes. Recent progress includes launching the Mystery Shopper public DMZ with verified PostgreSQL connectivity, though smoke/sign-off completion remains pending. A pending B2B CSAT threshold update requires selective commitment, testing, and deployment before finalization.

**Uncertainties/assumptions:** Current business-owner engagement (Maria, Dan, David Bedier) is not fully recorded; no conclusion drawn.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off; keep production changes branch/PR-controlled; remove old Installation Assessment testing data for Bedier while preserving live records

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |


---

## cws-pulse-awards - developer

- Project: CWS Pulse Awards / Digital Recognition Platform (`cws-pulse-awards`)
- Audience: developer
- Source-bundle SHA-256: `ed17d044b4d576065ff7e4efc991f51bdc40a98221010c2b9c680bcac98f825f`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The CWS Pulse Awards project has a functional local dev-auth-based MVP admin cockpit supporting entry, preview, send, and recipient management. Technical next actions include completing browser flow tests, verifying GitHub practices, validating SMTP relay, and securing Maria/P&C MVP acceptance. Blockers are pending Maria/P&C final approval and SMTP/Entra production auth configuration.

**Uncertainties/assumptions:** Current business-owner engagement (Maria/P&C) status is not recorded; no conclusion drawn; Production email authentication (SMTP/Entra) configuration details are not recorded; no conclusion drawn

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay and production email output; Confirm Maria/P&C final MVP acceptance and deployment route

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The MVP admin cockpit supports entry, preview, send, and recipient management on a local dev-auth basis with passing backend/frontend builds. Production-ready status is blocked pending Maria/P&C MVP acceptance and SMTP/Entra auth configuration. Key delivered components include the dashboard UI and email workflow, but verification and deployment pathways remain undefined.

**Uncertainties/assumptions:** Current business-owner engagement (Maria/P&C approval) timeline is not recorded; no conclusion drawn.; SMTP relay and Entra admin validation configuration status is unrecorded; no conclusion drawn.

**Gaps:** user_guide (GAP - missing); admin_guide (GAP - missing); developer_guide (GAP - missing); verification_matrix (GAP - missing)

**Recommended next actions:** Complete local browser flow test with dev-auth including recipient addition, winner entry, email preview/send, and browser compatibility verification.; Implement GitHub push/PR discipline for code review and version control.; Validate SMTP relay functionality and test production email output.; Coordinate with Maria/P&C to finalize MVP acceptance and deployment route.

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **FAIL** - omitted required gaps: developer_guide

**Summary:** The CWS Pulse Awards project has a functional MVP admin cockpit supporting local developer authentication baseline workflows, including recipient management and email operations. Key pending actions include completing local browser flow testing, validating GitHub push/PR discipline, configuring SMTP relay for production email, and obtaining final approval from Maria/P&C for MVP deployment. Blockers are unconfirmed deployment routing decisions and absence of production email/Entra setup.

**Uncertainties/assumptions:** Maria/P&C final MVP acceptance and deployment route decision has not been recorded; no conclusion drawn; Production SMTP relay and Entra authentication configuration are not recorded; no conclusion drawn

**Gaps:** user_guide documentation is missing (GAP); admin_guide documentation is missing (GAP); verification_matrix is missing (GAP)

**Recommended next actions:** Complete local browser flow test with dev-auth; Verify GitHub push/PR discipline; Validate SMTP relay for production email delivery; Confirm Maria/P&C MVP acceptance and deployment route

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |


---

## cws-pulse-awards - manager

- Project: CWS Pulse Awards / Digital Recognition Platform (`cws-pulse-awards`)
- Audience: manager
- Source-bundle SHA-256: `ed17d044b4d576065ff7e4efc991f51bdc40a98221010c2b9c680bcac98f825f`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The CWS Pulse Awards platform has completed core MVP functionality on a local dev-auth base, including admin recognition entry and email workflow. Progress is blocked by pending Maria/P&C MVP acceptance and unconfigured production SMTP/Entra authentication. Business value remains contingent on final approvals and production readiness, supporting controlled award entry and recognition outcomes.

**Uncertainties/assumptions:** Current business-owner engagement with Maria/P&C and CEO/Naadir is not fully recorded; no conclusion drawn.; Production email configuration (SMTP/Entra) status is not recorded; no conclusion drawn.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay; Confirm Maria/P&C final MVP acceptance and deployment route

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The CWS Pulse Awards project has completed MVP development with local dev-auth functionality for admin entry, email workflow, and recipient management. It remains blocked on Maria/P&C final MVP acceptance and SMTP production configuration. The platform supports the recognition program’s core purpose but requires managerial approval to proceed to production.

**Uncertainties/assumptions:** Current business-owner engagement from Maria/P&C is not fully recorded; no conclusion drawn.; SMTP/Entra production auth configuration status is not recorded; no conclusion drawn.

**Gaps:** User guide is missing (GAP - missing); Admin guide is missing (GAP - missing); Developer guide is missing (GAP - missing); Verification matrix is missing (GAP - missing)

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay and production email output; Confirm Maria/P&C MVP acceptance and deployment route

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The CWS Pulse Awards platform has an MVP admin cockpit with local development validation but lacks production-ready features like Entra admin validation and SMTP configuration. Progress is blocked by pending Maria/P&C MVP acceptance and unresolved production email infrastructure. The platform supports controlled recognition entry and email workflows but requires final approvals before deployment.

**Uncertainties/assumptions:** Current business-owner engagement from Maria/P&C is not fully recorded; no conclusion drawn; Final MVP acceptance and deployment route from Maria/P&C is not confirmed; no conclusion drawn; SMTP relay and Entra production auth configuration details are not recorded; no conclusion drawn

**Gaps:** user_guide missing; admin_guide missing; developer_guide missing; verification_matrix missing

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay and production email output; Confirm Maria/P&C final MVP acceptance and deployment route

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |


---

## vas-network-check - developer

- Project: VAS Network Check / System Check Platform (`vas-network-check`)
- Audience: developer
- Source-bundle SHA-256: `364fd83ce1c12fbf0202a48b61a1b3e99efc34b7c3b364c514402ec0647929a2`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The project is live and actively deployed on a VM, with functioning styled MJML/Jinja2 email reporting and verified workbook attachments. The SMSC authentication failure was diagnosed as rejection-related but requires ongoing monitoring if failures recur. Formal handover/EXIT evidence remains pending due to unconfirmed ownership.

**Uncertainties/assumptions:** Current business-owner engagement is not recorded; no conclusion drawn.; Formal handover/EXIT evidence completion is pending confirmed ownership; no conclusion drawn.

**Gaps:** developer_guide is missing (GAP - missing); support_runbook is missing (GAP - missing); verification_matrix is missing (GAP - missing); exit_md is missing (GAP - missing)

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Implement clearer UI/backend errors for missing styled-email assets or workbook; Complete formal handover/EXIT evidence once ownership is confirmed

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The VAS Network Check system is fully deployed on a VM with functional SVGs, workbook verification, and IPv6 authentication diagnostics. Outstanding work includes isolating SMSC authentication failures and finalizing handover documentation once ownership confirmations occur. The system generates branded reports via SMTP relay using React/FastAPI/Node.js.

**Uncertainties/assumptions:** Unconfirmed business-owner engagement; ongoing SMSC authentication behavior to monitor; ownership confirmation timeline unknown

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC authentication failures and correlate with policy changes; Develop UI/backend error handling for missing email/workbook assets; Complete formal handover documentation upon ownership confirmation

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.6
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The VAS Network Check platform is fully deployed on VMs with verified workbook integrations and functional styled email reporting. A recent SSH diagnostic isolated SMSC authentication failures, requiring ongoing monitoring. Pending actions include clarifying UI/backend errors for missing assets and completing handover/EXIT evidence after ownership confirmation. The system remains operational with no current blockers.

**Uncertainties/assumptions:** Current business-owner engagement is not fully recorded; no conclusion drawn; Handover/EXIT evidence completion is contingent on ownership confirmation; no conclusion drawn

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Investigate UI/backend errors for missing styled-email assets or workbook; Finalize handover/EXIT evidence once ownership is confirmed

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |


---

## vas-network-check - manager

- Project: VAS Network Check / System Check Platform (`vas-network-check`)
- Audience: manager
- Source-bundle SHA-256: `364fd83ce1c12fbf0202a48b61a1b3e99efc34b7c3b364c514402ec0647929a2`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.5
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The VAS Network Check platform is actively deployed and in use, with branded email functionality and workbook verification confirmed. A critical SMSC authentication issue was isolated but requires ongoing monitoring. Formal handover remains pending due to unconfirmed operational ownership.

**Uncertainties/assumptions:** Current business-owner engagement is not fully recorded; no conclusion drawn.; Handover/EXIT evidence completion depends on ownership confirmation which is not yet recorded; no conclusion drawn.

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Complete formal handover/EXIT evidence once ownership confirmed

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The VAS Network Check platform is fully deployed and operational, delivering self-service server checks and branded reports. Key recent work includes deployment, email styling, workbook verification, and isolation of an SMSC authentication issue. Current priorities focus on monitoring SMSC behavior, improving error handling, and completing handover documentation upon ownership confirmation.

**Uncertainties/assumptions:** Current business-owner engagement (IS/VAS/Network stakeholders) is not fully recorded; no conclusion drawn.

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Consider clearer UI/backend errors for missing styled-email assets or workbook; Complete formal handover/EXIT evidence once ownership confirmed

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The VAS Network Check platform is actively deployed and in operational use, with key components like the styled email template and workbook export verified. However, documentation gaps and unresolved ownership confirmation pose risks to formal handover and broader adoption.

**Uncertainties/assumptions:** Current business-owner engagement (IS/VAS/Network stakeholders) is not fully recorded; no conclusion drawn.; Formal handover/EXIT evidence completion depends on ownership confirmation, which is unresolved.

**Gaps:** developer_guide missing; support_runbook missing; verification_matrix missing; exit_md missing

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Confirm formal handover/EXIT evidence once operational ownership is confirmed; Consider clearer UI/backend errors for missing styled-email assets or workbook

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |


---

## health-fair-2026 - developer

- Project: Health Fair 2026 Digital Platform (`health-fair-2026`)
- Audience: developer
- Source-bundle SHA-256: `1a1866b8b283f6848f880755db14c910b204a6b675912a313ef88c22e9b15b83`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **FAIL** - missing expected fact (any of: 2026-07-31, 2026-08-07, july 31, august 7)

**Summary:** The project is in ongoing development with blocked status due to pending OHSE content confirmation, deferred Entra/RBAC enforcement, and unresolved event Wi-Fi routing. Visible progress includes isolable runtime ports, admin baseline setup, passing backend/front-end tests, and a first-class /guide page. Deployment and schema migration have not occurred.

**Uncertainties/assumptions:** Current business-owner engagement is not fully recorded; no conclusion drawn; Visual QA completion status for /guide and unknown route is not recorded; no conclusion drawn; Entra/RBAC deployment gates implementation progress is not explicitly recorded; no conclusion drawn

**Gaps:** user_guide missing (GAP - missing); admin_guide missing (GAP - missing); developer_guide missing (GAP - missing); support_runbook missing (GAP - missing); verification_matrix missing (GAP - missing)

**Recommended next actions:** Run mobile and desktop visual QA across specified routes including /guide, /admin, and unknown route; Confirm final OHSE metric/advice content and reporting controls; Implement Entra/RBAC enforcement; Resolve event Wi-Fi routing testing before QR asset approval

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The Health Fair 2026 Digital Platform is a CWS internal web app in ongoing development but blocked. Working components include configurable content slices, local MVP runtime ports, passing frontend/backend tests, and UI progress cues. Blockers include unconfirmed OHSE metric/advice content, deferred Entra/RBAC enforcement, and unresolved hostname/TLS deployment testing. Next steps require mobile/desktop QA, final content validation, and infrastructure readiness checks before the 2026-07-31 deadline.

**Uncertainties/assumptions:** Event Wi-Fi routing test status is not recorded; no conclusion drawn; Hostname/TLS deployment status is not recorded; no conclusion drawn

**Gaps:** user_guide; admin_guide; developer_guide; support_runbook; verification_matrix

**Recommended next actions:** Run mobile/desktop visual QA on /guide, /start, /stall/wellness-check, /recover, /summary, /admin, and unknown route; Confirm final OHSE metric/result/advice content; Implement previous-submission idempotency checks; Polish admin forms; Confirm Entra app/admin roles and backend authorization; Confirm hosting/network/DMZ approach; Run event Wi-Fi route test

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.2
- Automated claim pre-screen (heuristic, not a rubric pass): **FAIL** - missing expected fact (any of: 2026-07-31, 2026-08-07, july 31, august 7)

**Summary:** The Health Fair 2026 Digital Platform has implemented core MVP features including runtime ports, admin configurations, and a /guide page. Local testing showed passing lint/build and QA results, but deployment and key content finalization remain blocked due to pending OHSE classifications, Entra/RBAC enforcement, and event Wi-Fi routing validation. QA on unknown routes and admin access gates requires resolution before progress.

**Uncertainties/assumptions:** Entra/RBAC enforcement remains deferred to Trusted-Device MVP testing; no conclusion drawn; Event Wi-Fi routing path testing is not yet recorded; no conclusion drawn; Final OHSE content approval status is unrecorded; no conclusion drawn

**Gaps:** user_guide is missing (GAP); admin_guide is missing (GAP); developer_guide is missing (GAP); support_runbook is missing (GAP); verification_matrix is missing (GAP)

**Recommended next actions:** Run mobile/desktop visual QA on /guide, participant routes, /admin, and unknown routes; Confirm final OHSE classifications, advice content, and admin controls; Implement previous-submission idempotency checks; Decide participant advice UX and Entra/RBAC roles; Confirm event Wi-Fi routing and hostname/TLS for QR assets

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |


---

## health-fair-2026 - manager

- Project: Health Fair 2026 Digital Platform (`health-fair-2026`)
- Audience: manager
- Source-bundle SHA-256: `1a1866b8b283f6848f880755db14c910b204a6b675912a313ef88c22e9b15b83`

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen (heuristic, not a rubric pass): **FAIL** - false-missing artifacts (matrix says they exist): deployment_guide

**Summary:** The Health Fair 2026 Digital Platform is in blocked status due to unresolved OHSE content finalization, Entra/RBAC deployment dependencies, and unresolved event Wi-Fi routing. Progress includes local MVP development with QA completed on some components but deployment remains deferred. Urgent deadline (2026-07-31) adds risk to on-time delivery.

**Uncertainties/assumptions:** Current business-owner engagement (OHSE / Andrya Louise) details are not fully recorded; no conclusion drawn; Exact schedule for resolving Entra/RBAC or Wi-Fi routing blocks is not recorded; no conclusion drawn

**Gaps:** User guide, admin guide, developer guide, support runbook, and verification matrix are missing (documentation gaps); Deployment guide is in draft status but not approved (missing formal approval)

**Recommended next actions:** Run mobile and desktop visual QA across remaining routes; Confirm final OHSE classifications, advice wording, and reporting controls; Validate Entra/RBAC enforcement and target-host controls

Run 1 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The Health Fair 2026 Digital Platform is blocked in development due to pending OHSE content confirmation, deferred Entra/RBAC authorization, and unresolved event Wi-Fi routing. Progress includes MVP runtime setup and localized configurable content, but critical dep blockers remain. The project risks missing its 2026-07-31 deadline with current documentation gaps and unresolved dependencies.

**Uncertainties/assumptions:** Current business-owner engagement (OHSE/Andrya Louise) is not fully recorded; no conclusion drawn; Final deployment authorization pathways are not recorded; no conclusion drawn

**Gaps:** user_guide missing (GAP); admin_guide missing (GAP); developer_guide missing (GAP); support_runbook missing (GAP); verification_matrix missing (GAP)

**Recommended next actions:** Run mobile/desktop visual QA on /guide and other routes; Confirm final OHSE content and reporting controls; Implement Entra/RBAC enforcement for admin ports; Test event Wi-Fi routing before QR printing

Run 2 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.2
- Automated claim pre-screen (heuristic, not a rubric pass): **PASS**

**Summary:** The Health Fair 2026 Digital Platform is blocked due to pending final OHSE content approval, Entra/RBAC deployment dependencies, and unresolved event Wi-Fi routing. Progress includes configurable content and admin setup, but high-priority blockers remain unresolved. Deadline (2026-07-31) pressures completion of unresolved tasks.

**Uncertainties/assumptions:** OHSE content approval status is not recorded; no conclusion drawn; Entra/RBAC enforcement implementation timeline is unknown; no conclusion drawn; Event Wi-Fi route testing details are not recorded; no conclusion drawn

**Gaps:** user_guide missing (GAP); admin_guide missing (GAP); developer_guide missing (GAP); support_runbook missing (GAP); verification_matrix missing (GAP)

**Recommended next actions:** Run mobile and desktop visual QA across specified routes; Confirm final OHSE content, reporting controls, hostname/TLS, event Wi-Fi routing, and deployment gates

Run 3 human score | Grounded: ___ | Accurate: ___ | Complete: ___ | Safe: ___ | Useful: ___ | Pass: ___

### Case verdict (human)

| Question | Answer |
|---|---|
| Every run Grounded >= 4? | |
| Every run Safe >= 4? | |
| All runs schema-valid? | 3/3 |
| Strict stable pass (all of the above + rubric pass on every run)? | |

