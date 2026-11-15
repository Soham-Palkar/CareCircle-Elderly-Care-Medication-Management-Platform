# CareCircle: Project Structure

> Companion to `PROJECT_DESIGN.md`. This file answers: **where does each piece of code live, who may import whom, and what do we create first?**
>
> **Roles in scope:** `elder`, `caretaker`, `family`. (A read-only `doctor` view is roadmap only.)

---

## Table of Contents

1. [Structure Principles](#1-structure-principles)
2. [Repository Overview](#2-repository-overview)
3. [Backend Structure](#3-backend-structure)
4. [Frontend Structure](#4-frontend-structure)
5. [ML and Data Folder](#5-ml-and-data-folder)
6. [Scripts, Infra and CI](#6-scripts-infra-and-ci)
7. [Layer Dependency Rules](#7-layer-dependency-rules)
8. [Feature-to-File Map](#8-feature-to-file-map)
9. [Naming and Coding Conventions](#9-naming-and-coding-conventions)
10. [Configuration and Environment](#10-configuration-and-environment)
11. [Testing Layout](#11-testing-layout)
12. [Git Workflow and Team Ownership](#12-git-workflow-and-team-ownership)
13. [Build Order: What to Create First](#13-build-order-what-to-create-first)
14. [Definition of Done](#14-definition-of-done)

---

## 1. Structure Principles

| Principle | What it means in practice |
|---|---|
| **Separation of concerns** | Routers parse and authorize. Services run use-cases. Repositories talk to the DB. Domain holds pure logic. Adapters wrap third parties. |
| **Pure core** | The hardest logic (state machine, escalation, risk rules, forecast, permissions) has no database or network calls, so it is trivial to unit test. |
| **Circle scoping by default** | Repositories always take `circle_id`. There is no method that reads data without it. |
| **Swap-able providers** | Email, Telegram, vision and intent classifier sit behind interfaces with fakes for tests. |
| **One place per concept** | Each rule lives in exactly one file (for example, valid dose transitions live only in `state_machine.py`). |
| **Small files** | Aim for under ~250 lines per file. If a file grows beyond that, split by responsibility. |
| **Feature traceability** | Every PS requirement and feature (F1, F4, F5, F6, F7) maps to named files (Section 8). |

---

## 2. Repository Overview

Monorepo with three deployable units: `backend` (API), `worker` (lives inside backend code, runs as its own process), and `frontend`.

```
carecircle/
├── README.md                    # what it is, quick start, architecture, demo steps
├── docker-compose.yml           # api, worker, postgres, mailhog
├── Makefile                     # make up | test | lint | seed | migrate
├── .env.example                 # every variable documented, no secrets
├── .gitignore
├── .pre-commit-config.yaml      # ruff, black, mypy, eslint, prettier hooks
├── .github/
│   ├── workflows/ci.yml         # lint, types, tests, a11y, audit
│   └── pull_request_template.md
├── docs/
│   ├── PROJECT_DESIGN.md
│   ├── PROJECT_STRUCTURE.md     # this file
│   ├── adr/                     # short architecture decision records
│   ├── api-examples.http        # sample requests for quick manual testing
│   └── demo-script.md
├── backend/                     # FastAPI app and worker
├── frontend/                    # Next.js PWA
├── ml/                          # datasets, training and evaluation (optional but planned)
└── scripts/                     # seed, simulate, helpers
```

---

## 3. Backend Structure

```
backend/
├── pyproject.toml               # dependencies, ruff, black, mypy, pytest config
├── Dockerfile
├── alembic.ini
├── migrations/
│   └── versions/                # one migration per schema change
├── app/
│   ├── main.py                  # app factory: routers, middleware, exception handlers
│   │
│   ├── core/                    # cross-cutting infrastructure (no business rules)
│   │   ├── config.py            # typed settings from environment
│   │   ├── security.py          # argon2 hashing, JWT, signed one-time tokens
│   │   ├── deps.py              # FastAPI dependencies: db session, current member, role guard
│   │   ├── rate_limit.py        # login/upload/voice/action-link limits
│   │   ├── logging.py           # structured JSON logs, request IDs, no health data
│   │   └── errors.py            # error types and the {code, message, details} format
│   │
│   ├── api/v1/                  # HTTP layer: validate, authorize, call a service
│   │   ├── router.py            # mounts all routers under /api/v1
│   │   ├── auth.py              # create circle, login, logout, invites, redeem
│   │   ├── members.py           # list, permissions (elder), deactivate
│   │   ├── medications.py       # CRUD, archive, schedules
│   │   ├── doses.py             # list, next, taken, snooze, skip
│   │   ├── adherence.py         # summary, streaks
│   │   ├── appointments.py      # CRUD
│   │   ├── notifications.py     # list, notify preferences
│   │   ├── actions.py           # one-tap email links (signed token)
│   │   ├── scans.py             # upload, draft, confirm, verify-dose
│   │   ├── twin.py              # profile, flags, forecast, readings
│   │   ├── proposals.py         # what-if proposals: list, create, decide
│   │   ├── voice.py             # intent in, grounded response out
│   │   ├── messaging.py         # Telegram link and webhook
│   │   ├── audit.py             # audit log
│   │   ├── stream.py            # SSE live updates
│   │   └── health.py            # /health and /ready
│   │
│   ├── schemas/                 # Pydantic request/response models (no logic)
│   │   ├── common.py            # pagination, error envelope
│   │   ├── auth.py  member.py  medication.py  dose.py
│   │   ├── appointment.py  twin.py  scan.py  voice.py  notification.py
│   │
│   ├── models/                  # SQLAlchemy models (tables only)
│   │   ├── base.py              # base class, id and timestamp mixins
│   │   ├── circle.py  recipient.py  member.py  invite.py  permission.py
│   │   ├── medication.py  schedule.py  dose_event.py  appointment.py
│   │   ├── notification.py  escalation_policy.py
│   │   ├── health_reading.py  risk_flag.py  proposal.py
│   │   ├── scan_draft.py  streak.py  reward.py
│   │   ├── adherence_daily.py  interaction_rule.py  audit.py
│   │
│   ├── repositories/            # DB access. Every method requires circle_id.
│   │   ├── base.py              # circle-scoped base repository
│   │   ├── member_repo.py  medication_repo.py  schedule_repo.py
│   │   ├── dose_repo.py  appointment_repo.py  notification_repo.py
│   │   ├── reading_repo.py  flag_repo.py  proposal_repo.py
│   │   ├── scan_repo.py  audit_repo.py  adherence_repo.py
│   │
│   ├── services/                # use-cases, transactions, orchestration
│   │   ├── auth_service.py          # circle creation, invite, login, lockout
│   │   ├── member_service.py        # permissions, deactivation
│   │   ├── medication_service.py    # CRUD, duplicate/interaction advisory, doctor-confirm rule
│   │   ├── schedule_service.py      # versioning, event regeneration
│   │   ├── dose_service.py          # taken/snooze/skip/late, stock decrement, streak update
│   │   ├── adherence_service.py     # stats and daily aggregates
│   │   ├── appointment_service.py
│   │   ├── notification_service.py  # build messages, enqueue to outbox (dedupe keys)
│   │   ├── action_token_service.py  # signed single-use links
│   │   ├── scan_service.py          # F5: upload, extract, draft, confirm, verify
│   │   ├── twin_service.py          # F1: profile, run rules, forecast
│   │   ├── proposal_service.py      # F1: what-if proposals and approval
│   │   ├── voice_service.py         # F4: map intent to action and grounded reply
│   │   ├── messaging_service.py     # F7: link account, handle inbound replies
│   │   ├── streak_service.py        # streaks and rewards
│   │   ├── audit_service.py         # write audit rows
│   │   └── realtime.py              # SSE broker (publish to circle channel)
│   │
│   ├── domain/                  # PURE logic: no DB, no network, no framework imports
│   │   ├── state_machine.py     # valid dose transitions
│   │   ├── schedule_expansion.py# schedule rules to concrete datetimes (timezones, anchors)
│   │   ├── escalation.py        # given event + now + policy, return the next action
│   │   ├── risk_rules.py        # R1 to R6 as functions returning flags with evidence
│   │   ├── forecast.py          # per-slot miss risk (smoothed) with explanation
│   │   ├── intents.py           # intent matching rules (English and Hindi keywords)
│   │   ├── permissions.py       # role x action matrix plus elder overrides
│   │   └── types.py             # enums and dataclasses shared by domain
│   │
│   ├── adapters/                # third-party integrations behind interfaces
│   │   ├── email/    base.py  smtp.py  fake.py
│   │   ├── messaging/base.py  telegram.py  fake.py
│   │   ├── vision/   base.py  llm_vision.py  tesseract.py  fake.py
│   │   └── intent/   base.py  rules.py  classifier.py  # classifier optional (from ml/)
│   │
│   ├── worker/                  # separate process: python -m app.worker.main
│   │   ├── main.py              # loop: runs jobs on a 30s tick
│   │   ├── generator.py         # materialize next 7 days of dose events
│   │   ├── tick.py              # due-soon, overdue, escalation steps
│   │   ├── dispatcher.py        # outbox: lock, send, retry with backoff
│   │   └── risk_job.py          # periodic twin rule evaluation
│   │
│   ├── templates/email/         # en/ and hi/: dose_due, dose_missed, appointment, refill, risk_flag
│   │
│   └── db/
│       ├── session.py           # engine and session factory
│       └── seed_data/           # curated interaction rules, demo medicine cards (verified)
│
└── tests/                       # see Section 11
```

**One-line responsibility per layer**

| Layer | Allowed to do | Must not do |
|---|---|---|
| `api` | Parse input, check role, call one service, shape the response | Query the DB, hold business rules |
| `services` | Open transactions, call repositories/domain/adapters, write audit and notifications | Import from `api`; contain SQL |
| `repositories` | Run queries scoped by `circle_id` | Contain business decisions |
| `domain` | Decide (what state next, who to alert, what risk) | Touch DB, network, or framework code |
| `adapters` | Talk to email/Telegram/vision/ML | Contain business rules |
| `worker` | Call services/domain on a schedule | Have its own business logic |

---

## 4. Frontend Structure

Next.js (App Router), TypeScript strict, Tailwind, Radix/shadcn primitives. One route group per role.

```
frontend/
├── package.json
├── next.config.js  tsconfig.json  tailwind.config.ts
├── middleware.ts                # redirect by role; block routes the role cannot use
├── public/
│   ├── manifest.webmanifest     # PWA install
│   ├── icons/
│   └── sw.js                    # service worker (app shell, offline fallback page)
│
├── app/
│   ├── layout.tsx               # fonts, theme, i18n provider, live region for announcements
│   ├── (public)/
│   │   ├── login/               # circle code + passcode
│   │   ├── create-circle/
│   │   └── join/                # redeem invite, set passcode
│   │
│   ├── elder/                   # ELDERLY MODE (huge text, one action per screen)
│   │   ├── page.tsx             # "Take your <medicine> now" + Taken / Later / Help
│   │   ├── voice/               # voice interaction screen
│   │   ├── medicine/[id]/       # large plain-language medicine card
│   │   ├── today/               # today's doses, simple list
│   │   ├── people/              # who can see my data, my permissions, my audit log
│   │   └── help/                # alert caretaker
│   │
│   ├── care/                    # CARETAKER MODE (data-rich dashboard)
│   │   ├── page.tsx             # live dose timeline, alerts, flags
│   │   ├── medications/         # list, new, [id] edit, schedule versions
│   │   ├── scan/                # upload photo, review draft, confirm
│   │   ├── appointments/
│   │   ├── adherence/           # charts, streaks
│   │   ├── twin/                # flags, 48h forecast, readings (simulated label)
│   │   ├── proposals/           # what-if proposals and approvals
│   │   ├── members/             # invites, permissions
│   │   ├── audit/
│   │   └── settings/            # escalation policy, notify prefs, Telegram link
│   │
│   └── family/                  # FAMILY MODE (status first, limited actions)
│       ├── page.tsx             # today's status, missed alerts
│       ├── medications/         # only if elder granted access
│       ├── appointments/
│       └── alerts/
│
├── components/
│   ├── ui/                      # accessible primitives: Button, Dialog, Tabs, Toast, Switch
│   ├── elder/                   # BigDoseCard, TakenButton, VoiceControl, HelpButton
│   ├── care/                    # DoseTimeline, AdherenceChart, FlagCard, RiskForecast, ProposalCard, ScanReview
│   ├── family/                  # StatusSummary, AlertList
│   └── common/                  # RoleGuard, TextSizeControl, LanguageSwitch, LiveAnnouncer, SimulatedBadge
│
├── lib/
│   ├── api/                     # typed client + hooks per resource; one error handler
│   ├── auth/                    # session helpers, role utilities
│   ├── realtime/                # SSE subscription hook
│   ├── voice/                   # speech recognition and synthesis wrappers, intent mapping, fallback
│   ├── i18n/                    # next-intl config
│   ├── a11y/                    # focus management, announcements, reduced-motion helpers
│   └── utils/
│
├── messages/                    # en.json, hi.json (all user-visible strings)
├── styles/                      # design tokens: sizes, spacing, contrast-safe colors
└── tests/
    ├── unit/                    # Vitest + Testing Library
    ├── e2e/                     # Playwright flows
    └── a11y/                    # axe-core checks for every role view
```

**Frontend rules**

- Hiding a button is never security. The backend enforces permissions. The frontend only mirrors them for usability.
- Elder routes use a separate design scale (24px+ text, 7:1 contrast, 48px+ targets) defined in `styles/`, not ad-hoc classes.
- All strings come from `messages/`, so Hindi is a translation task and not a refactor.
- Every data screen has loading, empty and error states.

---

## 5. ML and Data Folder

Optional but planned. It is where the Adaption Labs credits fit, and it keeps AI work reproducible and out of the app code.

```
ml/
├── README.md                    # what each dataset is, how it was produced, limitations
├── intent/
│   ├── seed_examples.csv        # hand-written examples per intent (English, Hindi, Hinglish)
│   ├── adapted/                 # expanded dataset exported from the data tool
│   ├── train.py                 # trains a small intent classifier
│   ├── evaluate.py              # accuracy, per-intent confusion, confidence threshold choice
│   └── model/                   # exported artifact loaded by adapters/intent/classifier.py
├── scan_eval/
│   ├── cases.jsonl              # synthetic label text and expected structured fields
│   └── evaluate_scan.py         # runs the vision extractor on cases, reports accuracy
└── twin_sim/
    ├── scenarios.yaml           # named scenarios: "evening misses", "poor sleep", "refill soon"
    └── generate.py              # produces readings and dose histories for the simulator
```

Rules: **synthetic data only** (never real patient data), every dataset documented, and the app must keep working if the classifier is absent (falls back to `domain/intents.py` rules).

---

## 6. Scripts, Infra and CI

```
scripts/
├── seed_demo.py                 # demo circle, three members, medicines, 14 days of history
├── simulate_readings.py         # live simulated readings during the demo
├── create_demo_events.py        # create doses due in 1 to 2 minutes for the live escalation demo
└── export_openapi.py            # writes OpenAPI JSON for docs
```

**docker-compose services:** `api`, `worker`, `db` (Postgres), `mailhog` (see sent emails at a local web UI), optionally `frontend`.

**Makefile targets:** `make up`, `make down`, `make migrate`, `make seed`, `make test`, `make lint`, `make e2e`.

**CI pipeline (`ci.yml`) stages**

1. Lint and format check (ruff, black, ESLint, Prettier)
2. Type check (mypy, tsc)
3. Backend unit and integration tests (Postgres service container)
4. Frontend unit tests
5. E2E and accessibility tests (Playwright + axe)
6. Dependency audit (`pip-audit`, `npm audit`)

All stages must pass to merge.

---

## 7. Layer Dependency Rules

```
frontend  --HTTP-->  api  -->  services  -->  repositories  -->  models/db
                                  |
                                  +--> domain      (pure; imported by services and worker)
                                  +--> adapters    (behind interfaces; injected)
worker  -->  services, domain      (never api)
```

| From | May import | Must NOT import |
|---|---|---|
| `api` | `services`, `schemas`, `core` | `repositories`, `models`, `adapters` |
| `services` | `repositories`, `domain`, `adapters` (interfaces), `schemas` | `api` |
| `repositories` | `models`, `db`, `core` | `services`, `domain` rules |
| `domain` | standard library and `domain.types` only | everything else |
| `adapters` | `core.config`, third-party SDKs | `services`, `repositories` |
| `worker` | `services`, `domain`, `db` | `api` |

These rules can be enforced in CI with an import-linter check, which is also a good Code Quality talking point.

---

## 8. Feature-to-File Map

### 8.1 Problem statement must-haves

| Requirement | Backend | Frontend |
|---|---|---|
| Passcode access, roles | `services/auth_service.py`, `core/security.py`, `domain/permissions.py`, `api/v1/auth.py` | `app/(public)/*`, `middleware.ts`, `components/common/RoleGuard` |
| Medication schedules (view/add/edit/manage) | `medication_service.py`, `schedule_service.py`, `domain/schedule_expansion.py`, `api/v1/medications.py` | `app/care/medications/*` |
| Adherence tracking | `dose_service.py`, `domain/state_machine.py`, `adherence_service.py`, `api/v1/doses.py` | `app/elder/page.tsx`, `app/care/adherence/*` |
| Appointments | `appointment_service.py`, `api/v1/appointments.py` | `app/care/appointments/*`, `app/family/appointments/*` |
| Email reminders (dose, missed, appointment) | `notification_service.py`, `worker/tick.py`, `worker/dispatcher.py`, `adapters/email/*`, `templates/email/*` | `app/care/settings` (preferences) |
| Escalation ladder | `domain/escalation.py`, `worker/tick.py`, `models/escalation_policy.py` | `app/care/settings` |
| Elder in control, audit | `member_service.py`, `audit_service.py`, `api/v1/members.py`, `api/v1/audit.py` | `app/elder/people/*`, `app/care/audit/*` |

### 8.2 Selected differentiators

| Feature | Backend | Frontend | ML / data |
|---|---|---|---|
| **F1 Digital twin** | `twin_service.py`, `proposal_service.py`, `domain/risk_rules.py`, `domain/forecast.py`, `worker/risk_job.py`, `api/v1/twin.py`, `api/v1/proposals.py` | `app/care/twin/*`, `app/care/proposals/*`, `SimulatedBadge` | `ml/twin_sim/*` |
| **F4 Voice-first** | `voice_service.py`, `domain/intents.py`, `adapters/intent/*`, `api/v1/voice.py` | `app/elder/voice/*`, `lib/voice/*`, `VoiceControl` | `ml/intent/*` |
| **F5 Vision scan** | `scan_service.py`, `adapters/vision/*`, `api/v1/scans.py` | `app/care/scan/*`, `ScanReview` | `ml/scan_eval/*` |
| **F6 Role dashboards** | `domain/permissions.py`, `core/deps.py` (role guard), `stream.py`, `services/realtime.py` | `app/elder`, `app/care`, `app/family`, `lib/realtime/*` | none |
| **F7 Messaging bridge** | `messaging_service.py`, `adapters/messaging/telegram.py`, `api/v1/messaging.py` | `app/care/settings` (Telegram link) | none |

---

## 9. Naming and Coding Conventions

**Python**
- `snake_case` for modules, functions, variables. `PascalCase` for classes. Constants in `UPPER_SNAKE`.
- Type hints everywhere; `mypy --strict` on `domain/` and `services/`.
- Services expose verbs (`mark_dose_taken`), repositories expose data operations (`get_due_events`).
- No raw SQL strings in services. Parameterized ORM queries only.
- Raise typed errors from `core/errors.py`; routers convert them to the standard error format.
- No health data in log messages. Log IDs and event names only.

**TypeScript / React**
- `PascalCase` components, `camelCase` functions, `kebab-case` folders under `app/`.
- `strict` mode on, no `any` without a comment explaining why.
- One component per file; shared logic goes in hooks under `lib/`.
- No user-visible hard-coded strings; use `messages/`.

**Database**
- Table names plural `snake_case`; UUID primary keys; `created_at` and `updated_at` on every table.
- Timestamps always `timestamptz` (UTC); convert to the person's timezone only at the edges.
- Archive, don't delete, for medications and schedules.

**API**
- Versioned under `/api/v1`. Nouns for resources, actions as sub-resources (`/doses/{id}/taken`).
- Consistent error body `{code, message, details}`.
- Dose actions accept an idempotency key.

**Commits and PRs**
- Conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`.
- One concern per PR, using the PR template checklist (Section 14).

---

## 10. Configuration and Environment

`.env.example` (documented, no secrets committed):

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection |
| `JWT_SECRET`, `ACTION_TOKEN_SECRET` | Signing keys (long random values) |
| `ACCESS_TOKEN_MINUTES`, `REFRESH_TOKEN_DAYS` | Session lifetimes |
| `CORS_ORIGINS` | Allowed frontend origins |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM` | Email provider (MailHog values for dev) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET` | Messaging bridge |
| `VISION_PROVIDER`, `VISION_API_KEY` | Scan extraction (`fake` in tests) |
| `INTENT_CLASSIFIER_PATH` | Optional trained intent model |
| `TICK_SECONDS`, `REMINDER_LEAD_MINUTES`, `DEFAULT_GRACE_MINUTES` | Scheduler tuning |
| `ENV` | `dev`, `test`, `prod` |

Rules: settings loaded once through `core/config.py` with validation (the app refuses to start on missing secrets), secrets only from environment, and different `.env` per environment.

---

## 11. Testing Layout

```
backend/tests/
├── conftest.py                  # test DB, app client, fake adapters, freeze-time helper
├── factories.py                 # builders for circle, members, medications, events
├── unit/
│   ├── domain/                  # test_state_machine, test_escalation, test_risk_rules,
│   │                            # test_forecast, test_schedule_expansion, test_permissions, test_intents
│   └── services/                # test_dose_service, test_notification_service, test_scan_service ...
├── integration/
│   ├── api/                     # auth, medications, doses, appointments, proposals, voice
│   └── worker/                  # tick progression, outbox dedupe, retry, two workers no double-send
└── security/                    # cross-circle access, role abuse, lockout, token reuse, upload abuse

frontend/tests/
├── unit/                        # components and hooks
├── e2e/                         # login, mark taken, missed dose to escalation (MailHog), Telegram reply, elder revokes access
└── a11y/                        # axe-core per role page, keyboard-only flow

ml/                              # evaluate.py scripts produce reports saved to ml/reports/
```

**Must-have tests (write these first)**

| Area | Why |
|---|---|
| State machine: every valid and invalid transition | Core reliability |
| Escalation timing across levels and criticality | The most questioned feature |
| Notification dedupe and idempotency | "No duplicate emails" guarantee |
| Permission matrix for each role and each action | Security and elder control |
| Cross-circle access returns not found | IDOR protection |
| Schedule expansion with routine anchors and timezone | Easy to get wrong |
| Risk rules R1 to R6 with known scenarios | Digital twin credibility |

Use a **fake clock** (freeze time) so escalation tests don't wait real minutes.

---

## 12. Git Workflow and Team Ownership

**Branches:** `main` (always demo-able), `feat/<area>-<short-name>`, `fix/<short-name>`. Merge by PR with at least one review, even in a hackathon.

**Suggested ownership (4 people; merge roles if fewer)**

| Person | Owns | Main folders |
|---|---|---|
| A: Backend core | Auth, RBAC, meds, doses, audit, schema and migrations | `core/`, `api/`, `services/`, `repositories/`, `models/`, `domain/state_machine.py`, `domain/permissions.py` |
| B: Frontend and accessibility | Elder, caretaker, family UIs, i18n, PWA, a11y tests | `frontend/*` |
| C: Reliability and channels | Worker, escalation, outbox, email, Telegram, SSE | `worker/`, `domain/escalation.py`, `adapters/email`, `adapters/messaging`, `services/notification_service.py`, `services/realtime.py` |
| D: AI and intelligence | Vision scan, voice intents, twin rules and forecast, ML data, tests and docs | `adapters/vision`, `adapters/intent`, `domain/risk_rules.py`, `domain/forecast.py`, `domain/intents.py`, `ml/`, `docs/` |

**Shared contracts to agree on early (to avoid blocking each other):** the OpenAPI spec (A publishes stubs on day one so B can build against it), the dose state machine, the notification types, and the permission matrix.

---

## 13. Build Order: What to Create First

1. **Skeleton (all):** repo, Docker Compose, CI, lint/type config, empty folders with `__init__`/placeholder files, `.env.example`, README stub.
2. **Schema:** models and the first Alembic migration for circles, members, recipients, medications, schedules, dose events, notifications, audit.
3. **Auth and permissions:** circle creation, invite, login, lockout, `domain/permissions.py`, role guard dependency, and the authorization tests.
4. **Medications and schedules:** CRUD, versioning, `schedule_expansion.py`, generator job.
5. **Dose lifecycle:** `state_machine.py`, `dose_service.py`, taken/snooze/skip endpoints, audit rows.
6. **Worker and notifications:** tick, escalation, outbox dispatcher, email adapter with MailHog, email templates.
7. **Frontend core:** login, Elderly Mode main screen, caretaker dashboard, SSE live updates.
8. **Appointments and adherence stats.**
9. **Differentiators in value order:** vision scan, voice mode, Telegram bridge, digital twin (rules and forecast first, proposals last).
10. **Hardening:** test gaps, security pass, accessibility pass, seed data, demo scripts, README polish.

---

## 14. Definition of Done

A feature is done only when all boxes are true (copy into the PR template):

- [ ] Backend authorization enforced and covered by a test for each role
- [ ] Inputs validated; errors use the standard format
- [ ] No health data in logs
- [ ] Unit tests for domain logic; integration test for the endpoint or job
- [ ] Types pass (`mypy`, `tsc`); lint and format pass
- [ ] UI: loading, empty and error states handled
- [ ] Accessibility: keyboard works, labels present, contrast checked, axe has no critical issues
- [ ] Strings in `messages/` (English; Hindi if time)
- [ ] Audit entry written for state-changing actions
- [ ] Documented: README or docs updated, `.env.example` updated if new variables
- [ ] Mapped to a PS requirement or selected feature in Section 8