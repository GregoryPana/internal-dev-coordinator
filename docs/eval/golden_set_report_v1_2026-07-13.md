# T10 golden-set report - prompt v1 - 2026-07-13

Generated 2026-07-13T18:25:28.666201+00:00 by `python -m app.ai.eval.run_golden_set`. See `docs/eval/RUBRIC.md` for scoring instructions. Gregory fills in the rubric tables below.

---

## cwscx-platform - developer

- Project: CWSCX Platform / Customer Experience Platform (`cwscx-platform`)
- Audience: developer
- Prompt: `project_summary__developer` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`

**Summary:** The CWSCX platform is live with FastAPI, React, and PostgreSQL infrastructure. Mystery Shopper DMZ production launched with verified PostgreSQL connectivity but requires final smoke/sign-off. Next actions include completing DMZ smoke/sign-off, maintaining PR-controlled branches, and cleaning legacy data. No blockers reported.

**Gaps:** Missing user_guide; Missing admin_guide; Missing developer_guide; Missing verification_matrix

**Recommended next actions:** Complete Mystery Shopper DMZ smoke/sign-off workflow; Enforce PR-controlled production changes branch; Remove old Installation Assessment testing data while preserving live records

**Model's own confidence:** 0.0

### Rubric score

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
- Prompt: `project_summary__manager` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`

**Summary:** The CWSCX platform is live and active with high priority, but progress on the Mystery Shopper DMZ smoke/sign-off remains incomplete. Key documentation gaps exist for user, admin, and developer guides, which could hinder stakeholder confidence and operational readiness despite current technical functionality.

**Assumptions:** Business owners (Maria, Dan, David Bedier) are actively involved but not fully documented in repository materials.

**Gaps:** Missing user, admin, developer, verification matrix, and exit guide documentation; lack of formal record of business owner involvement; no reported outcomes or impact metrics.

**Recommended next actions:** Request completion of missing documentation to validate platform usability for stakeholders; Escalate Mystery Shopper DMZ smoke/sign-off completion status for accountability; Clarify stakeholder roles and expectations with business owners.

**Model's own confidence:** 0.3

### Rubric score

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
- Prompt: `project_summary__developer` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`

**Summary:** The CWS Pulse Awards project is in the build phase with an active status. The MVP admin cockpit supports local dev-auth-based recipient management, email workflows, and preview/send functionalities. Key blockers include awaiting Maria/P&C final MVP acceptance and configuring SMTP/Entra production auth. Next steps involve local browser testing, GitHub discipline verification, and SMTP validation.

**Gaps:** Missing user guide, admin guide, developer guide, and verification matrix documentation; Production SMTP/Entra auth configuration not implemented; Maria/P&C MVP approval pending

**Recommended next actions:** Complete local browser flow test with dev auth; Verify GitHub push/PR discipline; Validate SMTP relay and production email output; Confirm Maria/P&C MVP acceptance and deployment route

**Model's own confidence:** 0.7

### Rubric score

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
- Prompt: `project_summary__manager` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`

**Summary:** The CWS Pulse Awards platform development is in an active build phase with key functionality implemented locally but requires final approvals and production configuration before deployment. Progress includes MVP admin functionality for recognition entry and email workflows, but critical path items like SMTP relay setup and Maria/P&C final acceptance remain pending. The project faces dependencies on executive stakeholders and unresolved production authentication needs.

**Gaps:** No production deployment plan or final approval confirmation from Maria/P&C/CEO; missing verification matrix for quality assurance; incomplete documentation suite (user/admin/dev guides missing)

**Recommended next actions:** Escalate to Maria Pouponneau/CCCO for MVP acceptance sign-off and deployment path; prioritize SMTP relay configuration with DevOps; request documentation completion from development team

**Model's own confidence:** 0.4

### Rubric score

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
- Prompt: `project_summary__developer` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`

**Summary:** The vas-network-check tool is fully deployed on a VM with functional SMSC diagnostics, styled email reporting, and workbook generation. Recent fixes resolved SMSC authentication issues, but ongoing monitoring and UI improvements are needed. Formal handover documentation is pending confirmation of operational ownership.

**Assumptions:** Ownership confirmation is pending as process owner is unconfirmed, which may delay handover activities

**Gaps:** Missing developer guide, support runbook, verification matrix, and exit_md documentation critical for maintainability and onboarding; Unconfirmed process ownership may impact successor planning and transition processes

**Recommended next actions:** Continue monitoring SMSC authentication failures to validate resolution; Implement backend/UI error handling for missing email/workbook assets; Draft and compile formal handover documentation once ownership confirmation is received

**Model's own confidence:** 0.0

### Rubric score

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
- Prompt: `project_summary__manager` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`

**Summary:** The VAS Network Check platform is live and in active use, providing self-service server checks with automated reporting via email. Recent improvements include resolving SMSC authentication issues and finalizing branded email templates. However, unresolved documentation gaps and pending operational ownership confirmation pose risks to long-term maintenance and knowledge transfer.

**Assumptions:** Business owner IS/VAS/Network stakeholders status is unconfirmed despite project being in 'live' phase; Operational ownership confirmation is required before final handover processes can proceed

**Gaps:** Missing developer guide, support runbook, verification matrix, exit_md, and developer_guide documents create knowledge transfer risks; Unconfirmed operations team ownership may delay maintenance responsibilities

**Recommended next actions:** Formalize operational ownership confirmation with IS/VAS stakeholders to enable handover; Assign documentation completion tasks for missing guides to reduce future support risks

**Model's own confidence:** 0.4

### Rubric score

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
- Prompt: `project_summary__developer` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `passed`

**Summary:** Project is in the build phase but blocked due to unresolved blockers: final OHSE content confirmation, Entra admin authorization implementation, and hosting/DMZ path confirmation. Technical components like configurable content slices, admin UI, and APIs are implemented with passing tests, but deadlines require urgent prioritization.

**Assumptions:** Test results (ruff, pytest, Alembic) were sufficient for the configuration work; the tight 2026-07-31 deadline implies no room for delay in blockers.; Idempotency checks for previous submissions are likely part of the backend logic but not yet implemented as noted in next actions.

**Gaps:** Missing user, admin, developer, and support runbooks; verification matrix and exit MD are incomplete drafts or missing.; No details provided on Entra app configuration steps or specific hosting/DMZ requirements.; Testing strategy or coverage details are not documented.

**Recommended next actions:** Confirm final OHSE metrics/results/advice content with stakeholders; Implement backend authorization for Entra app roles; Validate hosting/network/DMZ setup feasibility; Complete idempotency checks for prior submissions; Finalize participant advice UX timing

**Model's own confidence:** 0.3

### Rubric score

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
- Prompt: `project_summary__manager` v1
- Model: openrouter/nvidia/nemotron-nano-9b-v2:free
- Validation status: `failed_schema`
- Error category: `malformed_output`

**No usable output - this attempt failed validation or the provider call.**

### Rubric score

| Dimension | Score (1-5) | Notes |
|---|---|---|
| Grounded | | |
| Accurate | | |
| Complete | | |
| Safe | | |
| Useful | | |
| **Overall pass (Y/N)** | | |

