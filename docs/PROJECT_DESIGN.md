# CareCircle: Elderly Care & Medication Management Platform

> Working title: **CareCircle**. A shared care ecosystem where the elderly person stays in control, and family, caretakers and doctors stay informed.
>
> **Pitch line:** *Reminders that keep working even when the elderly person can't or won't use an app, and a family that stays in the loop without taking control away.*

---

## Table of Contents

1. [Problem Statement Summary and Traceability](#1-problem-statement-summary-and-traceability)
2. [Feature Scope](#2-feature-scope)
3. [Tech Stack](#3-tech-stack)
4. [System Design](#4-system-design)
5. [Database Design](#5-database-design)
6. [API Design](#6-api-design)
7. [Functional Requirements](#7-functional-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Evaluation Focus Areas: How We Address Each](#9-evaluation-focus-areas-how-we-address-each)
10. [Project Structure](#10-project-structure)
11. [Build Plan and Cut List](#11-build-plan-and-cut-list)
12. [Demo Script](#12-demo-script)
13. [Risks, Ethics and Safety Notes](#13-risks-ethics-and-safety-notes)
14. [Assumptions and Open Decisions](#14-assumptions-and-open-decisions)

---

## 1. Problem Statement Summary and Traceability

**Challenge:** Build a smart, interconnected healthcare management platform that helps elderly individuals manage daily medications, medical appointments and routines, while keeping family and caretakers informed. It must go beyond a basic reminder app and keep the elderly person at the centre of their own healthcare decisions.

### 1.1 Must-have requirements taken directly from the PS

| # | PS requirement | Where we meet it |
|---|---|---|
| P1 | Shared ecosystem for elderly, caretakers and family | Care Circle model with roles (FR-A*, FR-R*) |
| P2 | Secure, **passcode-based** access | Circle code + member passcode, hashed, rate-limited, lockout (FR-A*) |
| P3 | View, add, edit, manage **medication schedules** | Medication and schedule CRUD with versioning (FR-M*) |
| P4 | Track **adherence** | Dose events, states, adherence stats, streaks (FR-D*) |
| P5 | Monitor **upcoming doctor appointments** | Appointment CRUD and reminders (FR-P*) |
| P6 | Proactive **email reminders**: missed medications, upcoming doses, appointments | Notification outbox with email channel and escalation (FR-N*) |
| P7 | Go beyond a basic reminder app | Digital twin, vision scan, voice-first, messaging bridge, escalation (Section 2.2) |
| P8 | More **smart, accessible, reliable, collaborative** | Mapping in 1.2 |
| P9 | Elderly **at the centre** of healthcare decisions | Elder-controlled permissions, approval of proposals, audit log (FR-A6, FR-L*, FR-W5) |

### 1.2 Mapping of the PS adjectives to our features

| PS word | What we build |
|---|---|
| Smarter | Rule-based digital twin, explainable risk flags, per-slot miss-risk forecast, interaction/duplicate advisory |
| More accessible | Elderly Mode (huge UI, one tap), voice-first, Telegram/WhatsApp bridge, Hindi and English, WCAG 2.2 AA |
| Reliable | Outbox pattern, idempotent notifications, retries, escalation ladder, at-least-once delivery |
| Collaborative | Role-based Care Circle dashboards, shared logs, rotating alerts to the right person |
| Elder at the centre | Elder grants and revokes permissions, approves system and family proposals, sees the audit log |

---

## 2. Feature Scope

### 2.1 Core (mandatory, build first)

1. **Care Circle and passcode access** with roles: `elder`, `caretaker`, `family`, `doctor`.
2. **Medication management:** CRUD, fixed-time or routine-anchored schedules, stock tracking.
3. **Dose tracking and adherence:** taken, snoozed, skipped (with reason), missed, late.
4. **Appointment management:** CRUD with reminders.
5. **Email notifications:** upcoming dose, missed dose, upcoming appointment, refill warning.
6. **Escalation ladder:** elder, then caretaker, then family, with configurable delays.
7. **Audit log and elder-controlled permissions.**

### 2.2 Differentiator features (the five selected)

| ID | Feature | Scoped, honest definition |
|---|---|---|
| **F1** | **Digital Twin Guardian** | A unified health profile (dose logs, readings, appointments). Readings come from a simulator or manual entry, labeled as such. An **explainable rule engine** raises risk flags, shows a 24 to 48 hour per-slot miss-risk forecast, and creates **what-if schedule proposals** that need caretaker/doctor and elder approval. No black-box ML, and nothing auto-applies. |
| **F4** | **Voice-first care coordinator** | Browser speech recognition and synthesis. Reads the next dose aloud and understands: *taken, remind me later, what's next, what is this for, help*. Answers are **grounded in stored data only**. A caregiver can ask for a medicine explainer to be read aloud. |
| **F5** | **Vision scan and wrong-pill check** | Photo of a prescription, strip or box is turned into a draft schedule (name, strength, frequency) that a human confirms. At dose time, a photo of the strip is matched against the scheduled medicine to catch mix-ups. Reads labels and packaging, **not loose pills**. |
| **F6** | **Care Circle role-based dashboards** | Elderly Mode (one big next action), Caregiver Mode (data-rich, schedule control), Family Mode (status, alerts, limited edit), Doctor Mode (read-only longitudinal view). Enforced on the backend. |
| **F7** | **Low-tech messaging bridge** | Reminders and replies over Telegram (WhatsApp via Twilio sandbox as an alternative). Reply `1` taken, `2` snooze, `3` skip. Writes to the same dose log, so it is another channel and not a separate system. |

### 2.3 Supporting features (cheap, high value)

- **Routine-anchored reminders** ("after breakfast", "before sleep") with a daily check-in.
- **Adherence streaks** with relationship-based rewards (a family call or photo, not points).
- **One-tap email action:** signed, single-use link to mark "Taken" without logging in.
- **Plain-language medicine card** (purpose, cautions, food to avoid), advisory only.
- **Dose-change safeguard:** old schedule archived, new schedule needs a "confirmed with doctor" tick.
- **Inactivity safety net:** no activity by wake time plus 3 hours alerts the caretaker.

### 2.4 Explicitly out of scope (state this on stage)

Real wearable hardware, passive pillbox sensors, clinical-grade prediction, loose-pill identification, e-prescriptions, payments. These appear as **roadmap** items that plug into the same event API.

---

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Next.js (App Router) + TypeScript (strict) + Tailwind CSS** as an installable **PWA** | One codebase for all role views; installable on a phone; SSR for fast first paint |
| UI primitives | **Radix UI / shadcn-ui** | Accessible components out of the box (focus management, ARIA) |
| i18n | **next-intl** (English, Hindi) | Accessibility for local users |
| Voice | **Web Speech API** (`SpeechRecognition`, `speechSynthesis`) with button fallback | No server cost, works offline-ish, zero extra infra |
| Backend API | **FastAPI (Python 3.11+)** | Fast to build, auto OpenAPI docs, Pydantic validation, fits the AI/ML stack |
| ORM / migrations | **SQLAlchemy 2.x + Alembic** | Typed models, versioned schema |
| Database | **PostgreSQL 16** | Transactions, `FOR UPDATE SKIP LOCKED` for the job queue, JSONB for flexible payloads, `timestamptz` |
| Scheduler / worker | **Separate worker process** polling Postgres (tick every 30s) | No extra infra, no duplicate sends with row locking, easy to test. Optional upgrade: Celery + Redis |
| Email | **SMTP provider (Resend / SendGrid / Gmail SMTP)**, **MailHog** in development | Visible emails in demo and tests |
| Messaging | **Telegram Bot API** (webhook), optional Twilio WhatsApp sandbox | Free, no business approval, same adapter interface |
| Vision / AI | **Vision-capable LLM API** with structured JSON output; **Tesseract** as OCR fallback | Label reading with confidence scores |
| Real-time UI | **Server-Sent Events (SSE)** | Live "missed dose" update on the caregiver dashboard without polling |
| Auth | **argon2id** hashing, short-lived **JWT in httpOnly cookie**, refresh rotation | Safe session handling |
| Testing | **pytest, httpx, pytest-asyncio**; **Vitest + Testing Library**; **Playwright**; **axe-core** | Unit, integration, E2E, accessibility |
| Quality | **ruff, black, mypy**; **ESLint, Prettier, tsc**; **pre-commit**; **GitHub Actions** | Enforced code quality |
| Packaging / deploy | **Docker Compose** (api, worker, db, mailhog); Vercel (frontend), Render/Railway (api, worker, db) | One-command local run, easy deploy |

> **Rule:** every external service sits behind an interface (`EmailSender`, `MessagingChannel`, `VisionExtractor`). Tests use fakes, and providers can be swapped without touching business logic.

---

## 4. System Design

### 4.1 High-level architecture

```
                     +----------------------------------------------+
                     |                 CLIENTS                      |
                     |  Elder PWA | Caretaker/Family Web | Doctor   |
                     |  (Next.js, voice, camera)   Telegram app     |
                     +---------+------------------------+-----------+
                               | HTTPS (REST + SSE)     | Bot webhook
                               v                        v
                     +----------------------------------------------+
                     |                 API (FastAPI)                |
                     |  Auth/RBAC | Meds | Doses | Appts | Twin |   |
                     |  Vision | Voice-intents | Telegram webhook   |
                     +--+-----------+-------------+-----------------+
                        |           |             |
                        v           v             v
                +-------------+ +-----------+ +--------------------+
                | PostgreSQL  | | Vision    | | Notification Outbox|
                | (all data)  | | provider  | | (table in Postgres)|
                +------+------+ +-----------+ +---------+----------+
                       ^                                ^
                       |                                |
                 +-----+--------------------------------+-----+
                 |             WORKER PROCESS                  |
                 | 1. Dose-event generator                     |
                 | 2. Tick: due-soon / overdue / escalation    |
                 | 3. Risk-rule engine (twin)                  |
                 | 4. Outbox dispatcher -> Email / Telegram    |
                 +---------------------------------------------+
```

### 4.2 Layered backend structure

```
api (routers, schemas)  ->  services (use-cases)  ->  repositories (DB access)  ->  models
                                   |
                                   +-> domain (pure functions: schedule expansion,
                                        state machine, escalation rules, risk rules)
                                   +-> adapters (email, telegram, vision) behind interfaces
```

- **Routers** only parse input, authorize, and call a service.
- **Services** hold use-case logic and transactions.
- **Domain** has no I/O, which makes the hardest logic (scheduler, escalation, risk rules) trivially unit-testable.
- **Adapters** isolate third parties.

### 4.3 Dose lifecycle (state machine)

```
 scheduled --(lead time reached)--> reminded
 reminded  --(user taps taken)-----> taken
 reminded  --(snooze)--------------> snoozed --(snooze ends)--> reminded
 reminded/snoozed --(skip + reason)-> skipped
 reminded/snoozed --(now > due + grace)--> missed  --(taken later)--> taken_late
```

Rules:
- Only valid transitions are allowed, enforced in one domain function.
- Every transition writes an audit row and, where relevant, a notification.
- `taken` or `taken_late` **cancels** any pending escalation for that event.

### 4.4 Scheduler and escalation flow

**Generator (daily and on schedule change):** materializes `dose_events` for the next 7 days in the person's timezone, with a unique key on `(schedule_id, scheduled_at)` so reruns are safe.

**Tick (every 30 seconds):**
1. **Due soon:** events in `scheduled` whose `scheduled_at - lead_time <= now` get a reminder notification and move to `reminded`.
2. **Escalation:** for unresolved events, apply the policy:

| Level | Default delay after due time | Who is notified | Channel |
|---|---|---|---|
| L0 | 0 min | Elder | In-app, voice, Telegram, email |
| L1 | +10 min | Elder (repeat) | Same |
| L2 | +30 min, event becomes `missed` | Caretaker | Email and Telegram |
| L3 | +60 min | Family | Email and Telegram |

   Critical medicines can use shorter delays (policy per medication criticality).
3. **Outbox dispatch:** pick pending notifications with `FOR UPDATE SKIP LOCKED`, send, mark `sent`, or retry with exponential backoff (max attempts, then `failed` and surfaced in the dashboard).

**Idempotency:** each notification has a unique `dedupe_key = "{dose_event_id}:{type}:{level}"`. A crash and restart can never double-send.

**Reliability properties:** at-least-once delivery, no duplicate sends, survives worker restart, multiple workers are safe.

### 4.5 Passcode authentication flow

1. A caretaker (or the elder) **creates a Care Circle** and gets a short public `circle_code`.
2. They **generate single-use invites** (role, expiry) for other members. An invite contains a one-time passcode, stored hashed.
3. On first login the invitee **sets their own passcode** (minimum 6 digits for the elder's easy PIN, and a longer passphrase recommended for caretakers).
4. **Login = `circle_code` + member passcode.** The server looks up members of that circle and verifies the hash (argon2id).
5. Protections: rate limit per circle and IP, lockout after repeated failures (`locked_until`), constant-time compares, generic error messages, and audit entries for failures.
6. A short-lived JWT carries `member_id`, `circle_id`, `role`. **Every query is scoped by `circle_id`**, so there is no cross-circle access.

> Why a PIN is acceptable: PIN logins have low entropy, so we compensate with hashing, lockout, rate limiting, per-circle scoping, short sessions, and a **trusted-device option** for the elder's own phone.

### 4.6 Authorization model

Roles define the maximum. The elder's per-member permissions narrow it.

| Capability | Elder | Caretaker | Family | Doctor |
|---|---|---|---|---|
| View medications and schedules | Yes | Yes | If granted | Yes (read-only) |
| Add/edit medications | Yes | Yes | If granted | No |
| Mark dose taken/skipped | Yes | Yes (on behalf, logged) | If granted | No |
| View adherence and flags | Yes | Yes | Summary | Yes |
| Manage appointments | Yes | Yes | If granted | Read-only |
| Approve proposals / schedule changes | **Yes (final say)** | Propose and approve if elder delegates | Propose only | Propose only |
| Manage members and permissions | **Yes** | Yes (invites) | No | No |
| View audit log | Yes | Yes | No | No |

### 4.7 Digital Twin (F1) design

**Inputs:** dose events, `health_readings` (simulated, manual, or future device), appointments, routine times.

**Rule engine (explainable, configurable thresholds, illustrative not clinical):**

| Rule | Trigger (default) | Output |
|---|---|---|
| R1 `ADHERENCE_DROP` | 7-day adherence below 70%, or same slot missed 3+ times in 7 days | Flag to caretaker with evidence |
| R2 `REFILL_SOON` | stock / daily use <= 5 days | Refill warning (email) |
| R3 `MISS_AND_VITALS` | Critical dose missed in 24h and resting heart rate 15% above 7-day baseline | High-severity flag |
| R4 `POOR_SLEEP` | Under 5 hours for 2 consecutive nights | Fatigue-window flag, optional timing **proposal** |
| R5 `INACTIVITY` | No activity by wake time + 3h | Caretaker alert |
| R6 `DUPLICATE_OR_INTERACTION` | New medicine matches an existing one or a curated interaction pair | Advisory warning (curated local table; not a substitute for a pharmacist) |

**Forecast (simple and defensible):** per time slot and weekday, miss risk = `(missed + 1) / (total + 2)` (Laplace-smoothed). The caregiver sees the next 24 to 48 hours as low/medium/high risk windows with the evidence ("evening dose missed 4 of last 7 days").

**What-if proposals:** the system or a member drafts a change ("move afternoon dose 30 minutes later"). It lands in `schedule_proposals` as **pending**. Only a delegated approver plus the elder's consent can apply it, and the old schedule is archived.

**Honesty rule:** the UI labels simulated data as simulated, and every flag says "advisory, discuss with your doctor".

### 4.8 Vision scan (F5) flow

1. Client uploads an image (JPEG/PNG/WebP, size-limited, downscaled client-side).
2. Server validates type and size, strips EXIF metadata, and passes the image to the `VisionExtractor`.
3. Extractor returns structured JSON: `name, strength, form, frequency, instructions, confidence`.
4. Low-confidence fields are highlighted. The result is stored as a **`scan_draft`** and never as a live medication.
5. A caretaker/elder reviews, edits, and **confirms**, which creates the medication and schedule through the normal service (so audit and validation apply).
6. **Wrong-pill check:** at dose time, a photo of the strip is matched against the scheduled medicine name and strength. Match shows a green confirmation. Mismatch shows a loud warning plus a caretaker alert.
7. Images are deleted after extraction, or kept with a short TTL if the user opts in.

### 4.9 Voice-first (F4) flow

- **Intents (fixed set):** `taken`, `later`, `next_dose`, `what_for`, `repeat`, `help`.
- Intent detection uses keyword/regex rules in English and basic Hindi ("le liya", "baad mein"). An LLM is **not** required, which keeps it fast, offline-friendly and safe.
- **Grounded answers:** responses are built from templates filled with database values (medicine name, time, purpose card). No free-form medical generation.
- `help` triggers an immediate alert to the caretaker (L2 path).
- Fallback: large on-screen buttons for every voice action.
- Caregiver query ("Mom seems confused about her new pill") opens that medicine's verified card and can read it aloud for the elder.

### 4.10 Messaging bridge (F7) flow

- Member links Telegram through a **deep link with a one-time token**, which stores `telegram_chat_id`.
- Outbound messages use the same outbox, with a `TelegramChannel` adapter.
- Inbound webhook is verified with Telegram's **secret token header**. Reply `1`/`2`/`3` maps to taken/snooze/skip and calls the same `DoseService`.
- The adapter interface makes WhatsApp (Twilio sandbox) a drop-in replacement.

### 4.11 Real-time updates

Caregiver dashboards subscribe to an SSE stream scoped by `circle_id`. Dose state changes and new flags are pushed instantly, which is the heart of the live demo.

---

## 5. Database Design

PostgreSQL. All timestamps `timestamptz` stored in UTC. Every table that holds circle data carries `circle_id` (or reaches it through a foreign key) so authorization is a simple scoped filter.

### 5.1 Entity relationships

```
care_circles 1---* members 1---* member_permissions
care_circles 1---1 care_recipients (the elder)
care_recipients 1---* medications 1---* medication_schedules 1---* dose_events
care_recipients 1---* appointments
care_recipients 1---* health_readings
care_recipients 1---* risk_flags
medications 1---* schedule_proposals
care_recipients 1---* scan_drafts
care_recipients 1---1 streaks 1---* rewards
members 1---* notifications (outbox)
care_circles 1---* audit_log
care_circles 1---* invites
care_recipients 1---* escalation_policies
```

### 5.2 Tables

**care_circles**
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| name | text | |
| circle_code | text UNIQUE | Short public code used at login |
| created_at | timestamptz | |

**care_recipients** (the elderly person)
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| circle_id | uuid FK | |
| full_name | text | |
| date_of_birth | date | optional |
| timezone | text | default `Asia/Kolkata` |
| language | text | `en` / `hi` |
| wake_time, sleep_time | time | for the inactivity rule |
| routine_times | jsonb | `{"breakfast":"08:30","lunch":"13:30","dinner":"20:30"}` for anchored schedules |

**members**
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| circle_id | uuid FK | |
| display_name | text | |
| role | enum | `elder, caretaker, family, doctor` |
| passcode_hash | text | argon2id |
| email | text | notifications |
| telegram_chat_id | bigint NULL | |
| notify_prefs | jsonb | channels and quiet hours |
| failed_attempts | int | |
| locked_until | timestamptz NULL | |
| is_active | bool | revocable by elder |
| created_at | timestamptz | |

**member_permissions** (set by the elder)
| Column | Type |
|---|---|
| member_id | uuid PK/FK |
| can_view_meds | bool |
| can_edit_meds | bool |
| can_mark_doses | bool |
| can_view_appointments | bool |
| can_edit_appointments | bool |
| can_view_health | bool |
| receives_alerts | bool |
| alert_level_min | int (which escalation level they receive) |

**invites**
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| circle_id | uuid FK | |
| role | enum | |
| code_hash | text | one-time code, hashed |
| expires_at | timestamptz | |
| used_at | timestamptz NULL | |
| created_by | uuid FK members | |

**medications**
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| recipient_id | uuid FK | |
| name | text | |
| strength | text | e.g. "500 mg" |
| form | text | tablet, syrup |
| instructions | text | |
| purpose_card | jsonb | plain-language explainer, advisory |
| criticality | enum | `normal, critical` |
| dose_quantity | numeric | units per dose |
| stock_count | numeric | |
| refill_threshold_days | int | |
| status | enum | `active, archived` |
| source | enum | `manual, scan` |
| confirmed_with_doctor | bool | |
| created_by | uuid FK | |
| created_at | timestamptz | |

**medication_schedules** (immutable: edits create a new row)
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| medication_id | uuid FK | |
| kind | enum | `fixed_time, routine_anchor` |
| time_of_day | time NULL | for fixed |
| anchor | text NULL | `breakfast`, `bedtime`... |
| anchor_offset_min | int | e.g. +15 after breakfast |
| days_of_week | smallint | bitmask |
| start_date, end_date | date | |
| grace_minutes | int | before `missed` |
| is_active | bool | old versions archived, not deleted |
| supersedes_id | uuid NULL | link to the previous version |

**dose_events**
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| schedule_id | uuid FK | |
| medication_id | uuid FK | |
| recipient_id | uuid FK | |
| scheduled_at | timestamptz | |
| state | enum | `scheduled, reminded, snoozed, taken, taken_late, skipped, missed` |
| escalation_level | smallint | 0 to 3 |
| snooze_until | timestamptz NULL | |
| taken_at | timestamptz NULL | |
| recorded_by | uuid NULL | member who recorded it |
| recorded_via | enum | `app, voice, telegram, email_link, caretaker` |
| skip_reason | text NULL | forgot / felt unwell / ran out / other |
| UNIQUE | `(schedule_id, scheduled_at)` | idempotent generation |

**appointments**
| Column | Type |
|---|---|
| id | uuid PK |
| recipient_id | uuid FK |
| doctor_name, specialty, location | text |
| scheduled_at | timestamptz |
| notes | text |
| status | enum `upcoming, done, cancelled` |
| reminder_offsets_min | int[] (default `{1440, 120}`) |
| created_by | uuid FK |

**notifications** (outbox)
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| member_id | uuid FK | recipient |
| channel | enum | `email, telegram, in_app` |
| type | enum | `dose_due, dose_missed, appointment, refill, risk_flag, help` |
| payload | jsonb | rendered content and links |
| dedupe_key | text UNIQUE | prevents duplicates |
| status | enum | `pending, sent, failed` |
| attempts | int | |
| next_attempt_at | timestamptz | backoff |
| sent_at | timestamptz NULL | |
| related_event_id | uuid NULL | |

**escalation_policies**
| Column | Type |
|---|---|
| id | uuid PK |
| recipient_id | uuid FK |
| criticality | enum |
| level | smallint |
| delay_minutes | int |
| target_role | enum |

**health_readings** (twin input)
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| recipient_id | uuid FK | |
| kind | enum | `heart_rate, sleep_hours, steps, bp_sys, bp_dia, glucose, mood` |
| value | numeric | |
| recorded_at | timestamptz | |
| source | enum | `simulated, manual, device` |

**risk_flags**
| Column | Type |
|---|---|
| id | uuid PK |
| recipient_id | uuid FK |
| rule_code | text (R1..R6) |
| severity | enum `info, warning, high` |
| message | text |
| evidence | jsonb |
| status | enum `open, acknowledged, resolved` |
| created_at | timestamptz |

**schedule_proposals**
| Column | Type |
|---|---|
| id | uuid PK |
| medication_id | uuid FK |
| proposed_by | uuid NULL (NULL = system) |
| change | jsonb |
| rationale | text |
| status | enum `pending, approved, rejected, expired` |
| decided_by | uuid NULL |
| decided_at | timestamptz NULL |

**scan_drafts**
| Column | Type |
|---|---|
| id | uuid PK |
| recipient_id | uuid FK |
| uploaded_by | uuid FK |
| extracted | jsonb |
| confidence | numeric |
| status | enum `pending, confirmed, rejected, expired` |
| expires_at | timestamptz |

**streaks / rewards**
| Table | Columns |
|---|---|
| streaks | recipient_id PK, current_streak, best_streak, last_date |
| rewards | id, recipient_id, threshold_days, reward_type (`call`, `photo`, `message`), reward_ref, unlocked_at, claimed_at |

**adherence_daily** (aggregate for fast dashboards): `recipient_id, date, scheduled_count, taken_count, missed_count`, PK `(recipient_id, date)`.

**interaction_rules** (curated, small): `drug_a, drug_b, severity, note`.

**audit_log** (append-only)
| Column | Type |
|---|---|
| id | bigserial PK |
| circle_id | uuid |
| actor_member_id | uuid NULL (NULL = system) |
| action | text |
| entity_type, entity_id | text, uuid |
| before, after | jsonb |
| ip | inet |
| created_at | timestamptz |

Application role has `INSERT`/`SELECT` only on `audit_log`, with no `UPDATE`/`DELETE`.

### 5.3 Key indexes

- `dose_events (state, scheduled_at)`: scheduler tick scans (partial index where `state IN ('scheduled','reminded','snoozed')`)
- `dose_events (recipient_id, scheduled_at DESC)`: timelines and adherence
- `notifications (status, next_attempt_at)`: outbox dispatcher (partial where `status='pending'`)
- `appointments (recipient_id, scheduled_at)`
- `health_readings (recipient_id, kind, recorded_at DESC)`
- `audit_log (circle_id, created_at DESC)`
- Unique: `circle_code`, `notifications.dedupe_key`, `(schedule_id, scheduled_at)`

### 5.4 Data rules

- Medication and schedule rows are **archived, never deleted**, to preserve history and audit.
- Retention: scan images deleted after extraction; notification payloads pruned after 90 days; user can export or delete their circle's data.

---

## 6. API Design

REST, JSON, versioned under `/api/v1`, documented by auto-generated OpenAPI. All endpoints except login/invite-redeem require auth and are circle-scoped.

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/circles` create circle, `POST /auth/login`, `POST /auth/logout`, `POST /auth/invites`, `POST /auth/invites/redeem` |
| Members | `GET /members`, `PATCH /members/{id}/permissions` (elder), `DELETE /members/{id}` (deactivate) |
| Medications | `GET/POST /medications`, `GET/PATCH /medications/{id}`, `POST /medications/{id}/archive`, `POST /medications/{id}/schedules` |
| Doses | `GET /doses?from&to`, `POST /doses/{id}/taken`, `/snooze`, `/skip`, `GET /doses/next` |
| Adherence | `GET /adherence/summary?range=7d`, `GET /streaks` |
| Appointments | `GET/POST /appointments`, `PATCH/DELETE /appointments/{id}` |
| Notifications | `GET /notifications`, `PATCH /members/me/notify-prefs` |
| One-tap email | `GET /actions/{signed_token}` (single-use, short expiry, confirm page then POST) |
| Scan | `POST /scans` upload, `GET /scans/{id}`, `POST /scans/{id}/confirm`, `POST /scans/verify-dose` |
| Twin | `GET /twin/profile`, `GET /twin/flags`, `GET /twin/forecast`, `POST /twin/readings`, `GET/POST /proposals`, `POST /proposals/{id}/decide` |
| Voice | `POST /voice/intent` (text in, grounded response out) |
| Messaging | `POST /messaging/telegram/link`, `POST /messaging/telegram/webhook` |
| Audit | `GET /audit` |
| Realtime | `GET /stream` (SSE) |
| Ops | `GET /health`, `GET /ready` |

Conventions: Pydantic request/response schemas, consistent error format `{code, message, details}`, pagination on lists, idempotency key accepted on dose actions.

---

## 7. Functional Requirements

Priority: **P0** = must ship, **P1** = should ship, **P2** = stretch.

### 7.1 Access and roles
| ID | Requirement | Pri |
|---|---|---|
| FR-A1 | A user can create a Care Circle and receives a circle code | P0 |
| FR-A2 | Members join through single-use, expiring invites with an assigned role | P0 |
| FR-A3 | Login with circle code + passcode; passcodes stored as argon2id hashes | P0 |
| FR-A4 | Failed logins are rate-limited and lock the member after a threshold | P0 |
| FR-A5 | Authorization enforced on the backend by role and circle scope | P0 |
| FR-A6 | The elder can grant/revoke per-member permissions and deactivate members | P0 |
| FR-R1 | UI adapts by role: Elderly, Caregiver, Family, Doctor views | P0 |

### 7.2 Medications and schedules
| ID | Requirement | Pri |
|---|---|---|
| FR-M1 | Authorized members can add, view, edit and archive medications | P0 |
| FR-M2 | Schedules support fixed times and routine anchors, days of week, date range | P0 |
| FR-M3 | Schedule edits create a new version and archive the old one | P0 |
| FR-M4 | Dose changes require a "confirmed with doctor" confirmation before activation | P1 |
| FR-M5 | Stock decreases on taken doses and warns before running out | P1 |
| FR-M6 | Each medicine has a plain-language card, shown large and readable aloud | P1 |
| FR-M7 | Adding a duplicate or curated-interacting medicine shows an advisory warning | P1 |

### 7.3 Dose tracking and adherence
| ID | Requirement | Pri |
|---|---|---|
| FR-D1 | The system generates upcoming dose events automatically | P0 |
| FR-D2 | A dose can be marked taken, snoozed or skipped (with reason) from app, voice, Telegram or email link | P0 |
| FR-D3 | Unresolved doses become `missed` after the grace period; late completion becomes `taken_late` | P0 |
| FR-D4 | Adherence statistics (daily, weekly, per medicine) are visible to permitted members | P0 |
| FR-D5 | Streaks and relationship-based rewards for consistent adherence | P1 |

### 7.4 Notifications and escalation
| ID | Requirement | Pri |
|---|---|---|
| FR-N1 | Email reminder before each upcoming dose | P0 |
| FR-N2 | Email alert to caretaker/family for missed doses | P0 |
| FR-N3 | Email reminders for appointments (24h and 2h before, configurable) | P0 |
| FR-N4 | Escalation ladder with configurable delays and targets | P0 |
| FR-N5 | Delivery is idempotent, retried with backoff, and failures are visible | P0 |
| FR-N6 | Members choose channels and quiet hours | P1 |
| FR-N7 | One-tap "Taken" link in email (signed, single-use, short expiry) | P1 |
| FR-N8 | Refill and risk-flag notifications | P1 |

### 7.5 Appointments
| ID | Requirement | Pri |
|---|---|---|
| FR-P1 | Add, view, edit, cancel appointments | P0 |
| FR-P2 | Upcoming appointments shown on all permitted dashboards | P0 |
| FR-P3 | Doctor view shows adherence summary for the period before a visit | P2 |

### 7.6 Digital Twin (F1)
| ID | Requirement | Pri |
|---|---|---|
| FR-W1 | Accept readings from a simulator/manual entry, labeled with source | P1 |
| FR-W2 | Unified health profile combining doses, readings, appointments | P1 |
| FR-W3 | Rule engine R1 to R6 raises flags with evidence | P1 |
| FR-W4 | 24 to 48 hour per-slot miss-risk forecast with explanation | P1 |
| FR-W5 | What-if proposals need approval; elder has the final say; old schedule archived | P1 |
| FR-W6 | All predictions labeled advisory | P0 (if F1 ships) |

### 7.7 Voice-first (F4)
| ID | Requirement | Pri |
|---|---|---|
| FR-S1 | Elderly Mode reads the next dose aloud on request | P1 |
| FR-S2 | Recognizes taken / later / next / what-for / repeat / help | P1 |
| FR-S3 | Answers come only from stored data (no free-form medical generation) | P0 (if F4 ships) |
| FR-S4 | `help` immediately alerts the caretaker | P1 |
| FR-S5 | Voice features degrade gracefully to buttons when unsupported | P0 (if F4 ships) |

### 7.8 Vision (F5)
| ID | Requirement | Pri |
|---|---|---|
| FR-V1 | Upload a photo of a prescription/strip/box | P1 |
| FR-V2 | Extract name, strength, frequency with a confidence score | P1 |
| FR-V3 | Extraction creates a **draft** that a human must confirm | P0 (if F5 ships) |
| FR-V4 | At dose time, a photo check flags a mismatch with the scheduled medicine | P2 |
| FR-V5 | Images validated, stripped of metadata, and deleted after processing | P0 (if F5 ships) |

### 7.9 Messaging bridge (F7)
| ID | Requirement | Pri |
|---|---|---|
| FR-T1 | Link a Telegram account through a one-time deep link | P1 |
| FR-T2 | Send reminders and alerts over Telegram | P1 |
| FR-T3 | Replies `1/2/3` record taken/snooze/skip | P1 |
| FR-T4 | Webhook requests are authenticated with the secret token | P0 (if F7 ships) |

### 7.10 Transparency
| ID | Requirement | Pri |
|---|---|---|
| FR-L1 | Every create/update/delete and dose action is written to an append-only audit log | P0 |
| FR-L2 | The elder (and caretaker) can view who changed what and when | P0 |

---

## 8. Non-Functional Requirements

### 8.1 Reliability and performance
| ID | Requirement | Target |
|---|---|---|
| NFR-R1 | Reminder timeliness | Sent within 60 seconds of the due time |
| NFR-R2 | Delivery guarantee | At-least-once with idempotent dedupe (no duplicates) |
| NFR-R3 | Worker crash recovery | Resumes without losing or duplicating notifications |
| NFR-R4 | API latency | p95 under 300 ms for dashboard and dose actions (excluding AI calls) |
| NFR-R5 | AI scan latency | Under 10 seconds with a visible progress state and timeout fallback |
| NFR-R6 | Graceful degradation | If email/AI provider fails: retry, surface status, and keep core app working |

### 8.2 Security and privacy
| ID | Requirement |
|---|---|
| NFR-S1 | Passcodes hashed with argon2id; never logged |
| NFR-S2 | httpOnly, Secure, SameSite cookies; short access token, refresh rotation |
| NFR-S3 | RBAC plus circle-scoped queries on every endpoint (no IDOR) |
| NFR-S4 | Input validation on all inputs (Pydantic/Zod); parameterized queries via ORM |
| NFR-S5 | Rate limiting on login, invites, uploads, voice and action links |
| NFR-S6 | Upload hardening: type/size allowlist, EXIF stripping, no execution, deletion after use |
| NFR-S7 | Signed, single-use, expiring action tokens; webhook secret verification |
| NFR-S8 | Secrets only via environment variables; `.env.example` provided; none in git |
| NFR-S9 | TLS in transit; encrypted storage at rest (managed DB); sensitive free-text fields optionally encrypted at field level |
| NFR-S10 | Security headers (CSP, HSTS, X-Content-Type-Options), strict CORS allowlist |
| NFR-S11 | No health data in logs or error messages; log IDs only |
| NFR-S12 | Dependency vulnerability scanning in CI (`pip-audit`, `npm audit`) |
| NFR-S13 | Privacy by design: consent for each member, data minimization, export and delete circle data (aligned with the principles of India's DPDP Act, 2023) |
| NFR-S14 | Clear disclaimer: advisory tool, not a medical device |

### 8.3 Accessibility and usability
| ID | Requirement |
|---|---|
| NFR-A1 | Conformance target **WCAG 2.2 AA**; Elderly Mode aims for AAA contrast (7:1) |
| NFR-A2 | Base font 18px; Elderly Mode 24px or larger; user-adjustable text size |
| NFR-A3 | Touch targets at least 48x48 px; spacing between destructive actions |
| NFR-A4 | One primary action per screen in Elderly Mode ("Take your blue pill now" with one Taken button) |
| NFR-A5 | Full keyboard navigation, visible focus, semantic HTML, ARIA labels, screen-reader tested |
| NFR-A6 | Information never conveyed by color alone (icons + text) |
| NFR-A7 | Respects `prefers-reduced-motion`; no time-limited interactions |
| NFR-A8 | Voice input and output with a button fallback |
| NFR-A9 | English and Hindi; simple, jargon-free wording; large readable dates |
| NFR-A10 | Works on low-end Android and on slow networks (PWA, small bundles) |
| NFR-A11 | Forgiving UX: undo for accidental "Taken", confirmation only for risky actions |

### 8.4 Maintainability, testability, observability
| ID | Requirement |
|---|---|
| NFR-M1 | Layered architecture; domain logic pure and free of I/O |
| NFR-M2 | Static typing (mypy, strict TypeScript); linters and formatters enforced in CI |
| NFR-M3 | 70%+ coverage on domain and service layers; 100% on state machine, escalation and permission matrix |
| NFR-M4 | Provider adapters behind interfaces so fakes can be used in tests |
| NFR-M5 | Structured JSON logs with request IDs; `/health` and `/ready` endpoints |
| NFR-M6 | One-command setup (`docker compose up`), seed script, README, architecture decision notes |
| NFR-M7 | Database migrations versioned with Alembic |

### 8.5 Efficiency and portability
| ID | Requirement |
|---|---|
| NFR-E1 | Pre-materialized dose events (no heavy on-the-fly schedule math per request) |
| NFR-E2 | Aggregates (`adherence_daily`) for dashboards; indexed, paginated queries; no N+1 queries |
| NFR-E3 | Batched outbox dispatch; backoff avoids hammering providers |
| NFR-E4 | AI is called **only** for scanning; images downscaled before upload |
| NFR-E5 | SSE instead of polling; frontend code-splitting and image optimization |
| NFR-E6 | Stateless API; the worker scales horizontally thanks to row locking |

---

## 9. Evaluation Focus Areas: How We Address Each

| Criterion | What we do | Evidence to show judges |
|---|---|---|
| **Code Quality** | Layered architecture (router, service, repository, domain). Pure domain functions. Type checking (mypy, strict TS). ruff/black/ESLint/Prettier with pre-commit. Small, focused modules. Consistent naming and error format. Meaningful README, `.env.example`, ADR notes. | Clean folder tree, passing lint/type CI, short readable service functions, OpenAPI docs |
| **Security** | argon2id passcodes, lockout and rate limits, httpOnly cookies, RBAC plus circle scoping, signed single-use action links, webhook verification, upload hardening, secure headers, no PHI in logs, append-only audit, dependency scanning, advisory-only AI with human confirmation | Threat table (below), authorization tests, pip-audit/npm-audit results, cross-circle access attempt returning 404 in a live demo |
| **Efficiency** | Materialized dose events, partial indexes, SKIP LOCKED worker, outbox batching, cached aggregates, SSE instead of polling, AI only where needed, downscaled uploads | Query plans for hot queries, small bundle size, notification latency metric |
| **Testing** | Unit tests for state machine, escalation, risk rules, permissions. Integration tests with a real Postgres test DB. E2E with Playwright and MailHog (missed dose leads to an email). Security tests. Accessibility tests with axe-core. | CI badge, coverage report, recorded E2E run |
| **Accessibility** | Elderly Mode, voice I/O, WCAG 2.2 AA, 7:1 contrast in Elderly Mode, large targets, Hindi and English, messaging bridge for people who won't install apps, keyboard and screen-reader support | Lighthouse accessibility score of 95+, axe-core zero critical issues, live voice demo |
| **Problem Statement Alignment** | Traceability table (Section 1) maps each PS line to features. Elder-centred controls and audit. Email reminders for all three required cases. Differentiators target "smarter, accessible, reliable, collaborative". | Section 1 matrix, a demo that follows the PS sentence by sentence |

### 9.1 Threat model summary

| Threat | Mitigation |
|---|---|
| Guessing the passcode | argon2id, lockout, rate limit per circle and IP, generic errors, audit of failures |
| Accessing another circle's data (IDOR) | Every query filtered by `circle_id` from the token; authorization tests |
| Role escalation (family edits what they shouldn't) | Backend permission matrix plus elder-set permissions; tests for each role |
| Stolen email/action link | Single-use, short expiry, signed, confirm step, scope limited to one dose |
| Malicious file upload | Type/size allowlist, EXIF stripping, no execution, deleted after use |
| Forged Telegram webhook | Secret token header verification |
| Wrong medical advice from AI | AI limited to label extraction into drafts that humans confirm; voice answers from stored data only; advisory labels |
| Data leakage via logs | No health content in logs; IDs only |
| Tampering with history | Append-only audit; archived (not deleted) medications and schedules |
| Injection / XSS | ORM parameterization, validation, output escaping, CSP |

### 9.2 Testing plan

| Level | What | Tools |
|---|---|---|
| Unit | State-machine transitions; schedule expansion (incl. routine anchors, timezone); escalation timing; risk rules R1 to R6; miss-risk formula; permission matrix; intent matching | pytest |
| Integration | API plus real Postgres: auth, RBAC, dose actions, outbox dedupe, concurrent workers not double-sending | pytest, httpx, test DB |
| Contract | Adapters tested against fakes; webhook payload shapes | pytest |
| E2E | Login, mark dose taken, miss a dose, escalation email arrives (MailHog), Telegram reply logs a dose, elder revokes a member | Playwright |
| Security | Cross-circle access, role abuse, expired/reused tokens, rate-limit and lockout, upload abuse | pytest, Playwright |
| Accessibility | axe-core on every role view, keyboard-only walkthrough, Lighthouse | Playwright + axe, Lighthouse CI |
| Smoke / load (optional) | Tick performance with 10k dose events | k6 or a script |

**CI gates:** lint, type-check, unit and integration tests, accessibility check, dependency audit. All must pass before merge.

---

## 10. Project Structure

```
carecircle/
├── README.md                  # setup, architecture, demo steps
├── docker-compose.yml         # api, worker, postgres, mailhog
├── .env.example
├── docs/
│   ├── PROJECT_DESIGN.md      # this document
│   └── adr/                   # short architecture decision records
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/              # config, security, logging, rate limit
│   │   ├── api/v1/            # routers: auth, meds, doses, appts, twin, scans, voice, messaging
│   │   ├── schemas/           # Pydantic models
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/      # DB access, always circle-scoped
│   │   ├── services/          # use-cases (DoseService, NotificationService, ...)
│   │   ├── domain/            # pure logic: state_machine, schedule, escalation, risk_rules, forecast
│   │   ├── adapters/          # email, telegram, vision (interfaces + implementations + fakes)
│   │   └── worker/            # generator, tick, outbox dispatcher, risk job
│   ├── migrations/            # Alembic
│   ├── tests/                 # unit/, integration/, security/
│   └── pyproject.toml
├── frontend/
│   ├── app/                   # routes by role: /elder, /care, /family, /doctor
│   ├── components/            # accessible UI building blocks
│   ├── lib/                   # api client, voice helpers, i18n
│   ├── messages/              # en.json, hi.json
│   ├── tests/                 # vitest, playwright, a11y
│   └── package.json
└── scripts/
    ├── seed_demo.py           # demo circle, meds, 14 days of history, simulated readings
    └── simulate_readings.py   # twin data generator
```

---

## 11. Build Plan and Cut List

Percentages of total time (adjust to your hours and team size).

| Phase | Share | Deliverables |
|---|---|---|
| 0. Setup | 8% | Repo, Docker Compose, CI, lint/type config, DB migrations skeleton |
| 1. Foundation | 17% | Data model, auth (circle, invites, passcode), RBAC, audit log |
| 2. Core reminders | 20% | Meds and schedules, dose events, state machine, worker, outbox, emails, appointments |
| 3. Escalation and roles | 10% | Escalation ladder, role-based dashboards, Elderly Mode UI, SSE live updates |
| 4. Differentiators | 25% | Vision scan, voice mode, Telegram bridge, digital twin (rules, forecast, proposals) |
| 5. Hardening | 10% | Tests, security checks, accessibility pass, seed data |
| 6. Demo and polish | 10% | Script, rehearsal, README, slides |

**Suggested ownership (4 people):** (1) backend core and worker, (2) frontend and accessibility, (3) AI/vision, voice, Telegram, (4) twin rules, testing, DevOps, docs. With fewer people, merge roles and cut from the list below.

**Cut order if time slips (cut from the top):**
1. Twin what-if proposals (keep flags and forecast)
2. Wrong-pill check at dose time (keep prescription/strip scan)
3. Telegram bridge
4. Streak rewards
5. Hindi translations (keep the i18n structure)

**Never cut:** passcode auth and roles, medication and dose tracking, email reminders, escalation, audit log, Elderly Mode, basic tests.

---

## 12. Demo Script (about 5 minutes)

1. **The problem (20s):** most reminder apps stop at an alarm, but elderly people forget, family worries, and the person loses control.
2. **Onboard (40s):** caretaker scans a prescription photo, the draft schedule appears, caretaker confirms it. *(F5)*
3. **Elder view (40s):** open Elderly Mode, big screen "Take your blue pill now", say "taken" by voice. *(F4, F6)*
4. **Escalation (80s):** skip responding to the next dose and show the live timeline. The reminder repeats, the caretaker dashboard flips to **missed** in real time, and the caretaker email appears in the inbox. Reply `1` from Telegram to log it. *(Core, F7)*
5. **Digital twin (50s):** show flags ("evening dose missed 4 of 7 days", "refill in 3 days"), the 48-hour risk windows, and a what-if proposal that waits for the elder's approval. State that data is simulated. *(F1)*
6. **Elder in control (30s):** elder revokes a family member's access, then opens the audit log showing every change.
7. **Close (20s):** quality evidence: tests passing, accessibility score, security measures.

---

## 13. Risks, Ethics and Safety Notes

| Risk | Mitigation |
|---|---|
| AI misreads a label | Confidence scores, human confirmation, never auto-activates |
| Users over-trust predictions | "Advisory" labels, rule-based and explainable flags, no automatic dose changes |
| Alert fatigue for caregivers | Configurable levels, quiet hours, only escalate unresolved events |
| Elder loses autonomy to family | Elder-controlled permissions, approval of proposals, visible audit log |
| Simulated data mistaken for real | Source labeled everywhere; said on stage |
| Provider outage (email, AI, Telegram) | Retries, status visibility, core app unaffected |
| Sensitive data exposure | Scoped queries, hashing, minimal logging, deletion and export |
| Regulatory misunderstanding | Disclaimer: reminder and coordination tool, not a diagnostic or medical device |

---

## 14. Assumptions and Open Decisions

**Assumptions**
- One Care Circle serves one elderly person (the schema can extend to several).
- Primary users are in India (timezone `Asia/Kolkata`, English and Hindi).
- Email is the mandatory channel; Telegram is the bonus channel.
- Wearable and sensor data is simulated for the demo.

**Decide before coding**
1. Final team size and hours (drives the cut list).
2. Vision provider and API key availability.
3. Email provider (and a verified sender domain or SMTP account).
4. Deployment targets (local-only demo vs hosted).
5. The list of 10 to 15 demo medicines for the interaction table and plain-language cards (use a trusted source and mark advisory).
