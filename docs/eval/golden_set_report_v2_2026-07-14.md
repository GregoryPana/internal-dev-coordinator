# T10 golden-set report - prompt v2 - 2026-07-14

Generated 2026-07-14T06:46:12.743725+00:00 by `python -m app.ai.eval.run_golden_set --runs 3`. See `docs/eval/RUBRIC.md` for scoring instructions; automated claim pre-screens flag known failure modes but the human rubric decides. Exact source bundles + hashes frozen in `golden_set_frozen_inputs_v2_2026-07-14.json`.

## Aggregate stats

- Attempts: 24 (3 run(s) x 8 cases)
- Schema-valid outputs: 23/24
- Automated claim pre-screen passed: 18/24
- Avg latency: 26280 ms; avg total tokens: 2011

---

## cwscx-platform - developer

- Project: CWSCX Platform / Customer Experience Platform (`cwscx-platform`)
- Audience: developer
- Source-bundle SHA-256: `6a57135e7860a358…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 1.0
- Automated claim pre-screen: **PASS**

**Summary:** The CWSCX platform is live with the Mystery Shopper DMZ production launch operational, including verified PostgreSQL connectivity. Pending items include completing the DMZ smoke/sign-off and deploying the uncommitted B2B CSAT threshold/report explanation. No blockers are recorded as of 2026-07-13.

**Assumptions:** Business owner (Maria, Dan, David Bedier) is not fully recorded in the repository; assuming stakeholders are managing this aspect externally.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off; keep production changes branch/PR-controlled; remove old Installation Assessment testing data for Bedier while preserving live records

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.8
- Automated claim pre-screen: **PASS**

**Summary:** The cwscx-platform is live with Mystery Shopper DMZ production launch verified (DB connectivity confirmed), but smoke/sign-off pending. B2B CSAT threshold updates remain uncommitted. Technical dependencies include FastAPI/React/PostgreSQL stack. Admin/agent guides are current, but user/ developer/ verification matrices are missing.

**Assumptions:** Business owner is not fully recorded; assuming Maria, Dan, David Bedier as stakeholders

**Gaps:** user_guide (GAP - missing); admin_guide (GAP - missing); developer_guide (GAP - missing); verification_matrix (GAP - missing)

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off (enroll -> TOTP/login -> DMZ survey submit -> internal review); Maintain PR-controlled production changes branch; Remove old Installation Assessment testing data for Bedier while preserving live records

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.7
- Automated claim pre-screen: **PASS**

**Summary:** The cwscx-platform is live with Mystery Shopper public DMZ production launch completed (verified DMZ-to-internal PostgreSQL connectivity), but end-to-end smoke/sign-off and B2B CSAT threshold/report update remain pending. Technical work includes React/FastAPI/PostgreSQL stack with unrecorded management of Installation Assessment testing data. Documentation gaps exist for key guides and verification matrix.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off; Maintain React/FastAPI/PostgreSQL production branch/PR-control; Remove outdated Installation Assessment testing data

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |


---

## cwscx-platform - manager

- Project: CWSCX Platform / Customer Experience Platform (`cwscx-platform`)
- Audience: manager
- Source-bundle SHA-256: `6a57135e7860a358…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen: **PASS**

**Summary:** The CWSCX Platform is live and active with high priority, providing a unified interface for customer experience data across B2B, Installation Assessment, and Mystery Shopper programs. Recent progress includes launching the Mystery Shopper public DMZ with verified connectivity, though end-to-end smoke/sign-off remains pending. The B2B CSAT threshold update is incomplete and requires selective commitment before deployment. Key risks involve unresolved documentation gaps and incomplete B2B CSAT configuration.

**Assumptions:** Business owner CX/business/product stakeholders (Maria, Dan, David Bedier) involvement is not fully recorded; assuming active ownership based on listed names but no documentation to confirm current engagement.

**Gaps:** user_guide (GAP - missing); admin_guide (GAP - missing); developer_guide (GAP - missing); verification_matrix (GAP - missing)

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off; Keep production changes branch/PR-controlled; Remove old Installation Assessment testing data for Bedier while preserving live records

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `failed_schema`
- Error category: `malformed_output`

**No usable output - this attempt failed validation or the provider call.**

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.6
- Automated claim pre-screen: **PASS**

**Summary:** The CWSCX Platform is live with core features implemented for customer experience data capture across B2B, Installation Assessment, and Mystery Shopper programmes. The Mystery Shopper public DMZ smoke/sign-off remains incomplete despite verified PostgreSQL connectivity. Key documentation gaps exist, including missing user, admin, and developer guides.

**Assumptions:** Business owner stakeholders (Maria, Dan, David Bedier) are not fully recorded in repository documentation; assuming their involvement is required for risk mitigation.

**Gaps:** user_guide (GAP - missing); admin_guide (GAP - missing); developer_guide (GAP - missing); verification_matrix (GAP - missing)

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off (as recorded in next_actions); Maintain production changes branch/PR-controlled (as recorded); Remove old Installation Assessment testing data for Bedier (as recorded)

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |


---

## cws-pulse-awards - developer

- Project: CWS Pulse Awards / Digital Recognition Platform (`cws-pulse-awards`)
- Audience: developer
- Source-bundle SHA-256: `ed17d044b4d57606…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.7
- Automated claim pre-screen: **PASS**

**Summary:** The CWS Pulse Awards project has a functional MVP admin cockpit supporting entry, preview, send, and recipient management on a local dev-auth baseline. Critical pending tasks include completing browser flow testing with dev auth, validating SMTP relay configuration, and securing production authorization from Maria/P&C. The tech stack (FastAPI/React/Vite) is validated for the MVP baseline but requires production-ready configurations.

**Assumptions:** SMTP relay not configured; assuming production email output remains untested; Maria/P&C final MVP acceptance pending; assuming deployment route requires her explicit confirmation

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete local browser flow test with dev auth; Validate SMTP relay functionality; Coordinate with Maria/P&C for MVP acceptance and deployment route

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 1.0
- Automated claim pre-screen: **PASS**

**Summary:** The MVP admin dashboard supports entry, preview, send, and recipient management locally with dev-auth, and backend/frontend builds are passing. Next steps include browser flow testing, GitHub discipline verification, SMTP relay configuration, and Maria/P&C approval for deployment. Blockers include pending Maria/P&C MVP acceptance and unconfigured SMTP/Entra production auth.

**Assumptions:** user_guide is not recorded; assuming manual creation post-delivery; admin_guide is not recorded; assuming admin documentation will be developed later; developer_guide is not recorded; assuming developer-specific docs will be prioritized; verification_matrix is not recorded; assuming test scenarios will be formalized after MVP finalization

**Gaps:** user_guide missing (GAP); admin_guide missing (GAP); developer_guide missing (GAP); verification_matrix missing (GAP)

**Recommended next actions:** Complete local browser flow test with dev-auth; Verify GitHub push/PR discipline; Validate SMTP relay and production email output; Confirm Maria/P&C final MVP acceptance and deployment route

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.5
- Automated claim pre-screen: **PASS**

**Summary:** The CWS Pulse Awards MVP admin cockpit supports local dev-auth entry, preview, send, and recipient management with passing backend/frontend builds. Pending blockers include awaiting Maria/P&C MVP acceptance and SMTP/Entra production auth configuration.

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay; Confirm Maria/P&C MVP acceptance and deployment route

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |


---

## cws-pulse-awards - manager

- Project: CWS Pulse Awards / Digital Recognition Platform (`cws-pulse-awards`)
- Audience: manager
- Source-bundle SHA-256: `ed17d044b4d57606…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen: **PASS**

**Summary:** The CWS Pulse Awards platform has a functional MVP baseline verified locally, supporting admin entry, preview/send workflows, and recipient management. Deployment is blocked pending Maria/P&C final MVP acceptance and SMTP/Entra production configuration. Business continuity depends on Naadir/CEO sign-off for the Golden Ticket requirement.

**Assumptions:** Local dev-auth bypass is a temporary measure not validated for production; assuming Maria/P&C will provide final MVP acceptance criteria; assuming SMTP relay configuration will be completed before deployment

**Gaps:** user_guide; admin_guide; developer_guide; verification_matrix

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay and production email output; Confirm Maria/P&C final MVP acceptance and deployment route

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **PASS**

**Summary:** The CWS Pulse Awards platform is in active development with an MVP admin cockpit completed for local testing, but production readiness hinges on Maria/P&C final approval and unresolved SMTP/Entra production authentication configuration. Business risks include potential delays from unresolved dependencies and documentation gaps affecting deployment.

**Assumptions:** Maria/P&C final MVP acceptance timeline is not recorded; assuming delayed if not communicated by next milestone; SMTP relay configuration status in production is not recorded; assuming incomplete until verified

**Gaps:** user_guide missing; admin_guide missing; developer_guide missing; verification_matrix missing

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay and production email output; Confirm Maria/P&C MVP acceptance and deployment route

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **PASS**

**Summary:** The CWS Pulse Awards platform has a functional MVP admin cockpit for local testing, supporting award entry and email workflows. Progress is delayed by pending Maria Pouponneau's MVP acceptance and undecided SMTP relay configuration. The platform requires production readiness approvals before deployment.

**Gaps:** user_guide missing; admin_guide missing; developer_guide missing; verification_matrix missing

**Recommended next actions:** Complete local browser flow test with dev auth; verify GitHub push/PR discipline; validate SMTP relay and production email output; confirm Maria/P&C MVP acceptance and deployment route

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |


---

## vas-network-check - developer

- Project: VAS Network Check / System Check Platform (`vas-network-check`)
- Audience: developer
- Source-bundle SHA-256: `364fd83ce1c12fbf…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.6
- Automated claim pre-screen: **FAIL** - prohibited claim matched: `resolv\w*[^.]{0,60}(smsc|auth)`

**Summary:** The vas-network-check project is fully deployed on a VM with active use. Styled MJML/Jinja2 email generation and workbook attachment functionality are operational. A recent SSH diagnostic resolved an SMSC authentication issue to diagnostics. Remaining tasks include monitoring SMSC auth behavior, evaluating UI/backend error clarity, and finalizing handover documentation once ownership is confirmed.

**Assumptions:** The business owner (IS/VAS/Network stakeholders) is unconfirmed; assuming procedural resolution will follow confirmation of ownership status.

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior for recurring failures; Evaluate UI/backend error messaging for missing styled-email assets or workbook issues; Finalize formal handover/EXIT evidence documentation

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **PASS**

**Summary:** VAS Network Check is live and actively used with VM deployment, styled email defaults, workbook verification, and SSH diagnostics functional. Pending: monitoring SMSC authentication issues if failures recur, evaluating UI/backend error improvements, and finalizing handover/EXIT documentation.

**Assumptions:** Process ownership confirmation for IS/VAS/Network stakeholders is not recorded; assuming active involvement.

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Evaluate clearer UI/backend error handling for missing styled-email assets or workbook; Complete formal handover/EXIT evidence once ownership confirmed

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **PASS**

**Summary:** The project is deployed on a VM with functional styled MJML/Jinja2 emails and verified workbook attachments. Recent diagnostics isolated an SMSC authentication failure. Next actions include monitoring SMSC behavior, evaluates UI/backend errors for missing assets, and formal handover pending ownership confirmation. Documentation gaps include developer guide, support runbook, verification matrix, and exit.md.

**Assumptions:** The named process owner for businesses stakeholders is unconfirmed

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior for recurring failures; Improve UI/backend error handling for missing styled-email assets or workbook; Complete formal handover/EXIT evidence once ownership is confirmed

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |


---

## vas-network-check - manager

- Project: VAS Network Check / System Check Platform (`vas-network-check`)
- Audience: manager
- Source-bundle SHA-256: `364fd83ce1c12fbf…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **PASS**

**Summary:** The vas-network-check project is actively deployed on VM with branding and functionality verified, but operational ownership confirmation via stakeholders remains unverified, risking potential handover delays. Self-service server checks and report generation align with business goals, though missing documentation gaps (developer guide, support runbook, verification matrix, exit MD) could hinder usability. Recent SMSC authentication diagnostics resolved a known issue but ongoing failure monitoring is pending.

**Assumptions:** Operational ownership by IS/VAS/Network stakeholders is not recorded; assuming no formal confirmation process exists; SMSC authentication issue resolution depends on unverified feedback from stakeholders

**Gaps:** developer_guide is missing; support_runbook is missing; verification_matrix is missing; exit_md is missing

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Consider clearer UI/backend errors for missing styled-email assets or workbook; Complete formal handover/EXIT evidence once ownership confirmed

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen: **FAIL** - prohibited claim matched: `resolv\w*[^.]{0,60}(smsc|auth)`

**Summary:** The VAS Network Check platform is fully deployed and in active use, providing IS/VAS/network operations with a self-service tool for server checks and branded reports. Progress includes resolving the styled email default and workbook functionality, while an authentication-related SMSC failure has been isolated but remains under monitoring. Risk persists due to unresolved SMSC authentication issues if failures recur and undocumented handover requirements pending ownership confirmation.

**Assumptions:** Process owner role is unconfirmed; assuming no formal process owner assignment; Handover/EXIT evidence completion dependent on ownership confirmation which is not recorded

**Gaps:** developer_guide missing; support_runbook missing; verification_matrix missing; exit_md missing

**Recommended next actions:** Monitor SMSC authentication/source-policy behavior if failures recur; Consider clearer UI/backend errors for missing styled-email assets or workbook; Complete formal handover/EXIT evidence once ownership confirmed

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **PASS**

**Summary:** The VAS Network Check platform is actively deployed with key components operational, including VM infrastructure, styled email reporting, and workbook functionality. Current focus is on monitoring SMSC authentication issues and completing handover documentation upon ownership confirmation, carrying medium priority risk due to unconfirmed process ownership.

**Assumptions:** Process owner not recorded; assuming IS/VAS/Network stakeholders are the process owners

**Gaps:** developer_guide; support_runbook; verification_matrix; exit_md

**Recommended next actions:** Monitor SMSC auth/source-policy behavior if failures recur; Consider clearer UI/backend errors for missing styled-email assets or workbook; Complete formal handover/EXIT evidence once ownership confirmed

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |


---

## health-fair-2026 - developer

- Project: Health Fair 2026 Digital Platform (`health-fair-2026`)
- Audience: developer
- Source-bundle SHA-256: `304a5a9b2e043fea…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **FAIL** - missing expected fact (any of: 2026-07-31, 2026-08-07, july 31, august 7)

**Summary:** The Health Fair 2026 platform has a configurable backend/frontend system implemented with passing tests, but remains blocked by unconfirmed health metrics/advice content, missing Entra auth implementation, undecided hosting/DMZ approach, and a tight testing deadline. Core APIs and admin workspace are functional but pending final content and authorization setup.

**Gaps:** user_guide; admin_guide; developer_guide; support_runbook; verification_matrix

**Recommended next actions:** Confirm final OHSE metric/result/advice content with stakeholders; Implement previous-submission idempotency checks in backend; Polish admin configuration forms; Decide participant advice timing UX; Finalize Entra app admin role definitions; Confirm hosting/network/DMZ architecture; Run event Wi-Fi route test before QR deployment

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.2
- Automated claim pre-screen: **PASS**

**Summary:** The Health Fair 2026 Digital Platform is an internal web app (FastAPI/React/Alembic) implementing configurable content/admin workflows and APIs. Core technical components like configurable metric/stall/reporting-category systems and admin configuration workspace are implemented and passed testing. Blocked by pending final OHSE metric/result/advice content confirmation, Entra backend/admin authorization implementation, hosting/DMZ approach confirmation, and a tight testing deadline (2026-07-31).

**Assumptions:** Final OHSE metric/result/advice content is not recorded; assuming confirmation will occur before deployment; Entra app/admin role details are not recorded; assuming implementation will proceed; Hosting/network/DMZ approach is not recorded; assuming it will be resolved before deployment; Participant advice timing UX polish is in progress but not recorded

**Gaps:** User guide missing (GAP - missing); Admin guide missing (GAP - missing); Support runbook missing (GAP - missing); Verification matrix missing (GAP - missing); Exit MD draft missing (GAP - missing)

**Recommended next actions:** Confirm final OHSE metric/result/advice content; Implement Entra backend/admin authorization; Confirm hosting/DMZ approach; Run event Wi-Fi route test before QR printing

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.0
- Automated claim pre-screen: **FAIL** - missing expected fact (any of: 2026-07-31, 2026-08-07, july 31, august 7)

**Summary:** The Health Fair 2026 Digital Platform has implemented configurable metric/stall/partner reporting systems and content APIs with passing tests, but is blocked on final OHSE metric/result/advice content confirmation, Entra backend authorization, and network/DMZ validation. Critical path items include final content approval and authorization implementation before deployment.

**Gaps:** user_guide; admin_guide; developer_guide; support_runbook; verification_matrix

**Recommended next actions:** Confirm final OHSE metric/result/advice content; Implement previous-submission idempotency checks; Polish admin forms; Decide participant advice timing UX; Confirm Entra app/admin roles and backend authorization; Confirm hosting/network/DMZ approach; Run event Wi-Fi route test before QR printing

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |


---

## health-fair-2026 - manager

- Project: Health Fair 2026 Digital Platform (`health-fair-2026`)
- Audience: manager
- Source-bundle SHA-256: `304a5a9b2e043fea…` (full text frozen alongside this report)
- Prompt version(s): 2

#### Run 1

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.6
- Automated claim pre-screen: **PASS**

**Summary:** The Health Fair 2026 Digital Platform project is blocked due to unresolved final OHSE metric/content confirmation and Entra backend authorization delays, risking deployment readiness ahead of the 2026-07-31 testing deadline. The platform aims to enable anonymous result tracking for OHSE and partners, but gaps in documentation and unapproved deployment planning increase risk.

**Gaps:** user_guide (missing); admin_guide (missing); developer_guide (missing); support_runbook (missing); verification_matrix (missing)

**Recommended next actions:** Confirm final OHSE metric/result/advice content; Confirm Entra app/admin roles and backend authorization; Confirm hosting/network/DMZ approach

#### Run 2

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.3
- Automated claim pre-screen: **PASS**

**Summary:** The Health Fair 2026 Digital Platform is in high-priority development with blocking issues preventing deployment ahead of the 2026-07-31 deadline. Progress includes configurable content systems and passing tests, but unresolved gaps in OHSE content confirmation, Entra authorization, and network/DMZ approvals risk missing the event date. The project requires immediate resolution of these blockers to meet the August 7 event.

**Gaps:** user_guide (GAP - missing); admin_guide (GAP - missing); developer_guide (GAP - missing); support_runbook (GAP - missing); verification_matrix (GAP - missing)

**Recommended next actions:** Confirm final OHSE metric/result/advice content; Confirm Entra app/admin roles and backend authorization; Confirm hosting/network/DMZ approach before deployment

#### Run 3

- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`
- requires_human_review: `True`
- Model self-reported confidence (uncalibrated): 0.4
- Automated claim pre-screen: **FAIL** - missing expected fact (any of: 2026-07-31, 2026-08-07, july 31, august 7)

**Summary:** The Health Fair 2026 Digital Platform is blocked due to unconfirmed OHSE metric/result/advice content, missing Entra admin roles and authorization, and undecided hosting/DMZ setup, risking the Q3 2026 deadline. Progress includes implementing configurable reporting systems and passing technical tests, but unresolved dependencies prevent deployment.

**Gaps:** user_guide; admin_guide; developer_guide; support_runbook; verification_matrix

**Recommended next actions:** Confirm final OHSE metric/result/advice content; Confirm Entra app registration/admin role details and implement backend authorization; Confirm hosting/network/DMZ approach before deployment; Implement previous-submission idempotency checks; Run event Wi-Fi route test before QR printing

### Rubric score (human, across the runs above)

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |

