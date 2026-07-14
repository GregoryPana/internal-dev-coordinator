# Design system - CWS Internal Development Coordinator

This is the project-level UI/design source of truth for the CWS Internal Development Coordinator. OpenCode, Claude Code and other implementation agents must read this before substantial frontend work.

## 1. Product personality

The product is a CWS internal development **control plane**: a serious workspace for project registry, status evidence, documentation readiness, starter packs, AI summaries and auditability.

It should feel like:

- a clean Linear/Supabase-style operational product;
- with Sentry-like status/evidence clarity;
- with Stripe-like trust and form polish;
- restrained, professional and fast for repeated use.

It should **not** feel like:

- a decorative marketing site;
- an awards/event/presentation surface;
- a second task tracker;
- a generic admin template with vanity metrics;
- a futuristic AI toy.

Primary principle:

> Data before AI. Workflow before automation. Integration before scale.

UI translation:

> Evidence before dashboards. Freshness before summaries. Human review before export.

## 2. Design skill bundle

Default bundle for this project:

1. `cws-saas-product-ui` — CWS internal SaaS/product UI principles.
2. `shadcn-ui-components` — component composition and semantic token discipline when Tailwind/shadcn is introduced.
3. `frontend-design-quality-gate` — required before calling implemented UI complete.

Optional task-specific skills:

- `web-design-style-library` — only for token/style exploration; selected families here are `clean`, `professional`, `shadcn`, `bento`, with light `enterprise`/`Sentry` influence.
- `gsap-web-animation` — only for restrained feedback/motion tokens; no cinematic motion.
- `mobile-app-ui-design` — only if designing meaningful mobile workflows. This MVP is laptop-first.

Do not load Horizon Digital/premium website design skills for this project.

## 3. UX architecture

### Primary surfaces

| Surface | Purpose | Default device | Priority |
|---|---|---|---|
| Portfolio dashboard | See projects, phases, stale status, blockers, documentation gaps | Desktop/laptop | T3 |
| Project profile | One project’s current state, links, ownership, next action, evidence | Desktop/laptop | T3 |
| Status events | Create/list factual updates with verification notes | Desktop/laptop | T4 |
| Documentation matrix | Required docs, current/stale/missing state, deterministic gaps | Desktop/laptop | T5 |
| Starter-pack intake/review | Generate/review/export Internal Dev Kit starter packs | Desktop/laptop | Phase 2 |
| AI summary review | Generate/review audience summaries over structured fields | Desktop/laptop | Phase 3 |

### App shell

Use a persistent product shell once more than one route exists:

- top-left product mark/name: `Internal Dev Coordinator`;
- environment indicator when not production: `Local`, `Dev`, `Pilot`;
- primary navigation: `Portfolio`, `Projects`, `Documentation`, `Starter Packs`, `AI Summaries`, `Audit`;
- user/role menu once auth surface exists;
- page header with title, one-sentence purpose, primary action, secondary actions.

For MVP, keep navigation simple and avoid building future modules until their task arrives.

## 4. Information hierarchy

Every major project page should make these visible without hunting:

1. project name and purpose;
2. phase/status/priority;
3. owner and business owner;
4. latest `data_as_of` / freshness state;
5. current next action;
6. blocker state;
7. repo/environment/docs links;
8. documentation readiness/gaps;
9. latest status evidence;
10. audit/review state where relevant.

Dashboards must answer operational questions, not show vanity charts:

- Which projects are blocked?
- Which project data is stale?
- Which projects lack required documentation?
- Which projects need Gregory/developer/manager action?
- Which outputs are generated but not reviewed?

## 5. Visual direction

### Style family

Recommended direction:

- **Primary:** `clean` / `professional` internal SaaS.
- **Component influence:** `shadcn` neutral component-library aesthetic.
- **Dashboard structure:** `bento` only for useful summary grouping.
- **Operational clarity:** light `Sentry` influence for status, issue and evidence surfaces.
- **Admin/settings clarity:** light `Supabase` influence for structured forms and metadata.

### Colour tokens

Start light-first. Dark mode can come later only if needed.

Suggested semantic tokens:

| Token | Direction | Use |
|---|---|---|
| `background` | near-white / slate-50 | app background |
| `surface` | white | cards, panels, forms |
| `surface-muted` | slate-50/100 | grouped metadata, table headers |
| `border` | slate-200 | card/table/form separation |
| `text` | slate-950 | primary text |
| `muted-text` | slate-500/600 | helper text, metadata |
| `primary` | deep CWS-aligned blue/teal | primary actions, active nav |
| `accent` | cyan/teal or controlled CWS accent | freshness/info highlights |
| `success` | green | current/approved/passed |
| `warning` | amber | stale/review needed |
| `danger` | red | blocked/failed/missing critical |
| `neutral-status` | slate | paused/draft/unknown |

Avoid hard-coded colour classes scattered across screens. Put decisions into CSS variables/tokens and reusable components.

### Typography

- Use system UI stack unless a project-wide font is deliberately added.
- Prefer clear product typography over expressive branding.
- Use tabular numerals for counts/status metrics.
- Page titles should be plain and specific.
- Helper copy should explain operational consequence, not marketing benefits.

### Spacing/radius/depth

- Spacing: 4px base scale; common gaps 8/12/16/24/32.
- Radius: medium, consistent; cards/buttons around 10-14px equivalent.
- Shadows: minimal; use borders and subtle elevation. No heavy glow.
- Density: compact but readable. This is an operational app, not a landing page.

## 6. Component rules

### Cards

Use cards for meaningful groupings only:

- portfolio KPI/status cards;
- project metadata panels;
- documentation profile summaries;
- generated-output review panels.

Every card needs a title and clear purpose. Do not create decorative cards that duplicate table data.

### Tables/lists

Tables are first-class UI here. They must include:

- clear column priority;
- status chips with consistent labels;
- empty states that tell the user what to do;
- loading states once async data exists;
- row actions that do not clutter scanning;
- readable responsive fallback for narrower screens.

Likely tables:

- project list;
- status-event list;
- documentation artifact matrix;
- starter-pack generated file list;
- audit-event list.

### Forms

Forms must be boring, clear and safe:

- labels always visible;
- placeholders are examples, not labels;
- required/optional indicated;
- bounded choices use selects/radio/toggles from controlled vocabularies;
- server errors mapped to fields/global messages;
- dangerous or official actions require confirmation/review copy.

### Status chips

Use consistent statuses from controlled vocabularies. Do not invent display states without updating `docs/DATA_MODEL.md` and `backend/app/vocab.py`.

Suggested visual mapping:

| Concept | Visual treatment |
|---|---|
| `active`, `current`, `approved`, `passed` | green/subtle success |
| `blocked`, `failed_*`, `access_denied` | red/subtle danger |
| `stale`, `generated`, `review needed`, `queued/running` | amber/blue info |
| `paused`, `draft`, `missing`, `retired` | neutral/slate or amber for missing-required |

### AI output UI

AI outputs must visibly show:

- task type and audience;
- source IDs / source bundle reference;
- prompt ID/version;
- generated timestamp;
- `data_as_of` and stale caveat where relevant;
- validation status;
- human review status;
- reviewer/export state.

AI copy should be framed as **draft/reviewed output**, never automatic truth.

## 7. Responsive behaviour

**Direction change (2026-07-14, Gregory):** this is now a dual-target app — full mobile usability plus a desktop layout that uses the full screen. Superseded the earlier "laptop-first" default below.

- **Desktop (≥768px, `md:` and up):** the app shell content area is fluid/edge-to-edge (no fixed max-width container) with responsive side padding (`px-4` → `px-12` as viewport grows). Top nav (`Portfolio`, `Audit`, `Settings`) stays in the header. Tables render as real tables.
- **Mobile (<768px):** primary navigation moves to a fixed bottom tab bar (icon + label, `Portfolio`/`Audit`/`Settings`); the top header collapses to the product name/environment badge and the dev-auth email field only. Data tables (project list, documentation matrix, audit trail, AI activity log) render as stacked label/value cards instead of a scrolling table — no horizontal scroll on any primary view. Forms and page-header actions wrap rather than overflow.
- Breakpoint used for the nav/table switch is Tailwind's `md` (768px), matching the existing tablet reference point.

Minimum responsive standard:

- 1280px+ desktop: full shell, fluid width, tables/cards as designed.
- 768px tablet: bottom tab bar active; cards stack in 2 columns; tables switch to card view at the same breakpoint as mobile.
- 375px mobile: no broken layout, no horizontal scrolling on core pages; all primary workflows (create/edit project, status update, documentation matrix edit, audit browsing, AI summary review) are fully usable.

## 8. Accessibility and safety

- Visible focus states for all interactive elements.
- Semantic headings in order.
- Inputs have labels and error descriptions.
- Icon-only buttons need accessible labels.
- Colour is not the only status signal; include text labels.
- Contrast must remain strong on status chips and muted metadata.
- Respect reduced motion when animation is added.

## 9. Motion

Motion should be restrained and functional:

- short transitions for drawers/dialogs/toasts;
- subtle loading skeletons;
- clear active/pressed button states;
- no scroll storytelling, parallax, cinematic transitions or over-animation.

Never use broad `transition: all` as a default.

## 10. Implementation guidance

Current frontend is a minimal Vite/React scaffold. When real UI work begins:

1. Keep React + TypeScript.
2. Add Tailwind/shadcn only as a deliberate design-system implementation step, not as random styling.
3. If shadcn is added, use semantic tokens and component composition; do not hard-code visual decisions screen by screen.
4. Create reusable local components for app shell, page header, status chip, metadata row, evidence link, empty state and data table patterns.
5. Keep frontend state simple until the app needs more.
6. Validate UI against this file and `docs/AGENT_DESIGN_SKILLS.md`.

## 11. Quality gate before UI is done

Any implemented UI task must report:

- build/typecheck result: `cd frontend && npm run build`;
- backend/API checks if flow depends on them;
- routes inspected in browser;
- console errors/warnings checked;
- responsive review at desktop and at least one narrower viewport;
- score against: workflow clarity, hierarchy, form/table quality, status/error feedback, accessibility, consistency with this design system.

A passing build alone is not enough for UI completion.
