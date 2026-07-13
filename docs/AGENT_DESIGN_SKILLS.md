# Agent design skills and UI guidance

This file tells OpenCode, Claude Code, Codex and future agents which design skills/design system to use for the CWS Internal Development Coordinator.

Read this before substantial frontend/UI work, then read the project-level design system:

```text
DESIGN.md
```

## 1. Project UI classification

This project is a **CWS internal SaaS-like operational control plane**.

Primary UI work is:

- portfolio dashboard;
- project registry/profile pages;
- status/event evidence capture;
- documentation matrix and deterministic gap lists;
- starter-pack intake/review/export;
- AI summary generation/review with full source/freshness/review metadata;
- audit visibility.

Therefore use the CWS internal product UI stack, not Horizon Digital/premium website styling and not event/awards presentation styling.

## 2. Default Hermes design skill bundle

Use this bundle for normal UI/dashboard/form/table work:

| Skill | Path | Why it applies |
|---|---|---|
| `design-skill-stack` | `/home/gpanagary/.hermes/skills/creative/design-skill-stack/SKILL.md` | Router for choosing the right design skills without overloading the task. |
| `cws-saas-product-ui` | `/home/gpanagary/.hermes/skills/creative/cws-saas-product-ui/SKILL.md` | Main product UI rules for CWS internal SaaS/workflow apps. |
| `shadcn-ui-components` | `/home/gpanagary/.hermes/skills/software-development/shadcn-ui-components/SKILL.md` | Use when/if React/Tailwind/shadcn components are introduced. Component composition, semantic tokens, forms, tables, dialogs. |
| `frontend-design-quality-gate` | `/home/gpanagary/.hermes/skills/software-development/frontend-design-quality-gate/SKILL.md` | Required verification loop before claiming UI is complete. |

Agents do not need to load/read every file above for every backend task. For frontend work, use the relevant files and always obey `DESIGN.md`.

## 3. Optional design skills by task type

| Task need | Optional skill | Path | Use / avoid |
|---|---|---|---|
| Visual style/token exploration | `web-design-style-library` | `/home/gpanagary/.hermes/skills/creative/web-design-style-library/SKILL.md` | Use only if visual direction is being revised. Current selected families: `clean`, `professional`, `shadcn`, `bento`, light `enterprise`/`Sentry`. |
| Motion/interaction polish | `gsap-web-animation` | `/home/gpanagary/.hermes/skills/software-development/gsap-web-animation/SKILL.md` | Use only for restrained product motion. No marketing/cinematic motion. |
| Mobile-first app patterns | `mobile-app-ui-design` | `/home/gpanagary/.hermes/skills/creative/mobile-app-ui-design/SKILL.md` | Use only if Gregory asks for mobile-first workflows. MVP is laptop-first. |

## 4. Skills not appropriate by default

Do **not** use these as the design base for this project unless Gregory explicitly changes the product direction:

- `horizon-digital-premium-websites` — for Horizon Digital client websites, not CWS internal control planes.
- `creative-web-artifacts` — for one-off artifacts/prototypes, not the production app design system.
- event/awards/presentation styling from Pulse Awards guidance — this app should be operational and evidence-led.

## 5. Current design system decision

Use the design system in `DESIGN.md`:

- **Primary style:** clean/professional internal SaaS.
- **References:** Linear/Supabase structure, Sentry-style operational status clarity, Stripe-like trust and form polish.
- **Mode:** light-first, neutral surfaces, strong contrast.
- **Accent:** one restrained CWS/product blue/teal accent.
- **Data density:** compact but readable.
- **Motion:** minimal and purposeful.
- **Core UX:** evidence/freshness/review state must be visible wherever relevant.

## 6. Implementation rules for OpenCode/Claude

Before frontend implementation:

1. Read `AGENTS.md` and `docs/PROJECT_SCOPE.md` first.
2. Read this file and `DESIGN.md`.
3. Confirm the current task from `docs/MVP_TASK_PLAN.md`.
4. Do only the current task.
5. Do not introduce out-of-scope features such as WorkItems, repo integration, RAG, separate trainee views, or autonomous actions.

When building UI:

- Keep React + TypeScript.
- Use controlled vocabulary labels from `docs/DATA_MODEL.md` / `backend/app/vocab.py`; do not invent statuses.
- Build reusable components once patterns repeat: app shell, page header, status chip, metadata block, data table, empty state, evidence link, review-state badge.
- Forms need visible labels, validation, required/optional states and safe submit/cancel behaviour.
- Tables/lists need empty/loading/error states and responsive behaviour.
- AI output screens must show source IDs, prompt/version, generated date, `data_as_of`, stale caveats, validation status and human review status.
- Official/export/destructive actions need clear review copy.

## 7. shadcn/Tailwind note

The frontend currently starts as a minimal Vite/React scaffold. If a task introduces Tailwind/shadcn:

- inspect `package.json` and existing frontend structure first;
- add shadcn deliberately as the component-system layer, not just for looks;
- use semantic tokens (`background`, `foreground`, `muted`, `primary`, `border`, etc.);
- avoid screen-by-screen hard-coded colour/style drift;
- use shadcn composition for cards/forms/tables/dialogs/sheets where useful.

## 8. UI quality gate

For any completed UI work, provide evidence:

```text
cd frontend && npm run build
```

Plus, when routes are viewable:

- browser inspection of changed routes;
- console check;
- desktop and narrower viewport review;
- short scorecard against `DESIGN.md`:
  - workflow clarity;
  - information hierarchy;
  - form/table usability;
  - status/error/empty/loading handling;
  - accessibility/focus/contrast;
  - visual consistency;
  - motion restraint.

Do not call UI complete from code inspection or a successful build alone.

## 9. Handoff wording for future prompts

When prompting OpenCode/Claude for a UI task in this repo, include:

```text
Before UI work, read docs/AGENT_DESIGN_SKILLS.md and DESIGN.md. Use the CWS internal SaaS control-plane design system: clean/professional, light-first, evidence-led, status/freshness/review states visible, restrained motion. Use shadcn-style component discipline if adding component libraries. Verify with npm run build and browser/console/responsive review before claiming completion.
```
