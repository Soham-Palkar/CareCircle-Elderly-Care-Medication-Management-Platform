# CareCircle: Elderly Care & Medication Management Platform

> A shared care ecosystem where the elderly person stays in control, and family, caretakers, and doctors stay informed.
>
> **Pitch line:** *Reminders that keep working even when the elderly person can't or won't use an app, and a family that stays in the loop without taking control away.*

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Frontend Architecture & Tech Stack](#frontend-architecture--tech-stack)
3. [Design System & Accessibility (WCAG 2.2 AA / AAA)](#design-system--accessibility-wcag-22-aa--aaa)
4. [Role Experiences & Route Map](#role-experiences--route-map)
5. [Core Flows & Differentiators](#core-flows--differentiators)
6. [Getting Started (Frontend Setup)](#getting-started-frontend-setup)
7. [Environment Variables](#environment-variables)
8. [Demo & Offline Assumptions](#demo--offline-assumptions)
9. [Safety, Privacy & Clinical Disclaimers](#safety-privacy--clinical-disclaimers)

---

## 1. Product Overview

CareCircle addresses the fundamental challenge of elderly health coordination: reminder apps usually stop at a ringing phone alarm, family members worry from afar, and elderly individuals risk losing autonomy over their daily lives.

CareCircle establishes a shared, respectful care circle where:
- **The elderly individual remains at the centre:** All schedule proposals require explicit consent, permissions can be granted or revoked per member, and an append-only audit trail is readily inspectable.
- **Caretakers manage routines proactively:** Live dose timelines with Server-Sent Events (SSE), explainable Digital Twin Guardian risk rules (R1–R6), prescription/box vision scanning, and escalation ladders.
- **Family members receive reassurance:** Status-first daily wellness summaries without clinical clutter.
- **Accessible & Multilingual:** Built for WCAG 2.2 AA (with AAA 7:1 contrast in Elderly Mode), 48px+ touch targets, Web Speech API voice interaction with visible fallbacks, and English & Hindi translations.

---

## 2. Frontend Architecture & Tech Stack

The frontend is built according to `PROJECT_STRUCTURE.md` and `PROJECT_DESIGN.md`:

- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript with strict mode (`noImplicitAny`, strict null checks)
- **Styling & Design Tokens:** Tailwind CSS with warm, reassuring, non-clinical color palettes
- **UI Primitives:** Radix UI / custom accessible primitives (focus management, ARIA live regions)
- **Internationalization:** English (`messages/en.json`) and Hindi (`messages/hi.json`) with in-app toggle
- **Real-Time Updates:** Server-Sent Events (SSE) via `lib/realtime/useSSE.ts`
- **Voice Interaction:** Web Speech API (`SpeechRecognition` & `speechSynthesis`) in `lib/voice/` with grounded intent matching and visible button fallbacks
- **PWA & Offline:** Installable PWA (`manifest.webmanifest`, `sw.js`, and offline fallback shell)

### Directory Structure

```
frontend/
├── app/
│   ├── (public)/                 # Public auth flows
│   │   ├── login/                # Circle code + Passcode PIN login
│   │   ├── create-circle/        # Circle creation & safe code storage
│   │   └── join/                 # Single-use invite redemption
│   ├── elder/                    # ELDERLY MODE (24px+ text, 7:1 contrast, 1 primary action)
│   │   ├── page.tsx              # Next due dose, Taken / Later / Help
│   │   ├── today/                # Today's simplified dose list
│   │   ├── voice/                # Voice assistant with grounded answers
│   │   ├── medicine/[id]/        # Large plain-language medicine card
│   │   ├── people/               # Elder-controlled permissions & audit log
│   │   └── help/                 # Priority caretaker alert screen
│   ├── care/                     # CARETAKER MODE (Data-rich dashboard)
│   │   ├── page.tsx              # Live dose timeline, SSE, alerts, flags
│   │   ├── medications/          # List, add, edit, schedule versioning
│   │   ├── scan/                 # Prescription & package vision scanning
│   │   ├── appointments/         # Medical appointment management
│   │   ├── adherence/            # 7-day adherence charts & streaks
│   │   ├── twin/                 # Digital Twin Guardian (R1-R6, 48h forecast)
│   │   ├── proposals/            # What-if schedule proposals & review
│   │   ├── members/              # Circle members & invite creation
│   │   ├── audit/                # Immutable audit history
│   │   └── settings/             # Escalation ladder, channels, Telegram
│   ├── family/                   # FAMILY MODE (Status first, peace of mind)
│   │   ├── page.tsx              # Today's status summary & progress
│   │   ├── medications/          # Permitted medication view
│   │   ├── appointments/         # Permitted upcoming visits
│   │   └── alerts/               # Missed dose escalation history
│   ├── doctor/                   # DOCTOR MODE (Roadmap placeholder)
│   ├── layout.tsx                # App shell, Navbar, LiveAnnouncer, i18n
│   ├── globals.css               # Base 18px / Elderly 24px+ / reduced-motion
│   └── page.tsx                  # Landing page & quick role selector
├── components/
│   ├── common/                   # Navbar, RoleGuard, TextSizeControl, LanguageSwitch, SimulatedBadge
│   ├── ui/                       # Button, Card, Badge, Dialog, Input, Tabs, Switch
│   ├── elder/                    # BigDoseCard, TakenButton, DoseStateLabel, VoiceControl, UndoToast
│   ├── care/                     # DoseTimeline, AdherenceChart, FlagCard, RiskForecast, ProposalCard, ScanReview
│   └── family/                   # StatusSummary, DoseStatusCard, AlertList, PermissionGate
├── lib/
│   ├── api/                      # Typed API client, domain types, and mock data fallback
│   ├── auth/                     # Session helpers and active role management
│   ├── realtime/                 # SSE subscription hook
│   ├── voice/                    # Speech recognition, synthesis, and intent mapper
│   ├── a11y/                     # ARIA live announcements and reduced motion
│   └── i18n/                     # Client i18n context & language toggles
└── messages/
    ├── en.json                   # English strings dictionary
    └── hi.json                   # Hindi (हिंदी) strings dictionary
```

---

## 3. Design System & Accessibility (WCAG 2.2 AA / AAA)

CareCircle rejects the cold, sterile hospital-management aesthetic in favor of warm amber, terracotta, and soft cream tones (`#FAF8F5`, `#C97B4B`, `#2D2318`).

### Accessibility Standards Implemented:
- **Base Typography:** Minimum 18px across default views.
- **Elderly Mode Scale:** 24px+ body font, 42px display headings, 7:1 AAA contrast ratios.
- **Text Size Switcher:** Instant toggles for Standard (18px), Large (20px), and Elderly Mode (24px+).
- **Touch Target Sizing:** Minimum 48×48px across all clickable elements; 64px min-height for Elder primary actions.
- **Status Representation:** Text and icons are **always** paired together (e.g. green CheckCircle + "Taken", red AlertCircle + "Missed"). Status is never conveyed by color alone.
- **Accidental Action Recovery:** 10-second undo toast for accidental "Taken" actions.
- **Reduced Motion:** Fully complies with `prefers-reduced-motion: reduce` by dampening animations.
- **Screen Reader Announcements:** Dual-mode ARIA live regions (`polite` for routine status changes, `assertive` for priority alerts).

---

## 4. Role Experiences & Route Map

### 1. Elder Role (`/elder/*`)
- **Main Home (`/elder`):** Shows the single most urgent dose on a `BigDoseCard` with high-contrast text, scheduled time, and what it's for. Two primary choices: **"I took it"** and **"Remind me later"**.
- **Voice Assistant (`/elder/voice`):** Reads the next dose aloud. Understands 6 grounded intents: `taken`, `later`, `next_dose`, `what_for`, `repeat`, and `help`. Includes large visible button fallbacks for all actions.
- **Today's Doses (`/elder/today`):** Clean list of today's morning, afternoon, and evening medicines.
- **Medicine Card (`/elder/medicine/[id]`):** Plain-language purpose, diet notes, instructions, and Web Speech read-aloud button.
- **Access Control (`/elder/people`):** The elder can review each member, toggle per-member permissions, deactivate members, and inspect the audit trail.
- **Help (`/elder/help`):** Instant alert to the primary caretaker with direct telephone link.

### 2. Caretaker Role (`/care/*`)
- **Dashboard (`/care`):** Live dose timeline with SSE real-time state changes, missed dose alerts, upcoming appointments, Digital Twin risk flags, 7-day adherence snapshot, and refill alerts.
- **Medications (`/care/medications`):** CRUD for medications, fixed-time and routine-anchored schedules ("15m after breakfast"), stock tracking, duplicate/interaction warnings, schedule versioning, and doctor-confirmation safeguards.
- **Prescription Scan (`/care/scan`):** Camera or file upload for prescriptions and box packaging. Extracts medicine name, strength, and frequency into an editable draft with confidence scores. Requires explicit doctor verification before activating.
- **Appointments (`/care/appointments`):** Schedule doctor visits with reminder offsets (24h and 2h before).
- **Adherence (`/care/adherence`):** 7-day bar chart, daily numbers, and relationship-based streaks (e.g. family video call reward).
- **Digital Twin Guardian (`/care/twin`):** Explainable rules (R1 `ADHERENCE_DROP`, R2 `REFILL_SOON`, R3 `MISS_AND_VITALS`), 24-48h miss-risk forecast, manual and simulated readings with source badges.
- **What-If Proposals (`/care/proposals`):** System-suggested schedule changes. Requires caretaker review and elder approval.
- **Members & Invites (`/care/members`):** Generate single-use expiring invite codes.
- **Security Audit Log (`/care/audit`):** Filterable, append-only historical log.
- **Settings & Escalation (`/care/settings`):** Configurable L0 → L1 → L2 → L3 escalation ladder, quiet hours, and Telegram linking (`1` = taken, `2` = snooze, `3` = skip).

### 3. Family Role (`/family/*`)
- **Status-First Home (`/family`):** High-level daily summary ("Savitri Devi has taken 2 of 3 doses today"), streak, and active missed alerts.
- **Medications (`/family/medications`):** Gated by the elder's permission settings. Shows informative purpose summaries if permitted.
- **Appointments (`/family/appointments`):** Upcoming consultations and dates.
- **Alerts (`/family/alerts`):** Historical log of missed dose alerts and resolutions.

### 4. Doctor Role (`/doctor`)
- **Roadmap Preview:** Read-only longitudinal record interface planned for pre-visit clinical consultation.

---

## 5. Core Flows & Differentiators

| Feature | Scope & Implementation | Safety Safeguard |
|---|---|---|
| **Passcode Authentication** | Circle code + member PIN. Generic error messages, account lockout after 5 attempts. | Passcodes are never logged or displayed. |
| **Dose Lifecycle** | `scheduled` → `reminded` → `taken` / `taken_late` / `snoozed` / `skipped` / `missed`. | Real-time SSE updates; 10s undo window. |
| **Prescription Vision Scan** | Photo of prescription, strip, or box extracted into draft with confidence scores. | **Does not identify loose pills.** Human doctor confirmation required. |
| **Voice Assistant** | Browser Speech Recognition & Synthesis for English & Hindi phrases. | **No free-form LLM hallucinations.** Grounded only in stored data. |
| **Digital Twin Guardian** | R1–R6 explainable rule engine and 24-48h Laplace-smoothed miss-risk forecast. | Labeled as **ADVISORY** or **SIMULATED**. |
| **Telegram Bridge** | Telegram notifications with replies `1` (taken), `2` (snooze), `3` (skip). | Writes to the shared dose log without bypassing audit. |

---

## 6. Getting Started (Frontend Setup)

### Prerequisites
- Node.js 18.17+ or 20+
- npm or pnpm

### Installation

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Copy environment variables
cp .env.example .env.local

# 4. Run type check
npm run type-check

# 5. Build production bundle
npm run build

# 6. Start development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.

---

## 7. Environment Variables

Create `.env.local` inside the `frontend/` directory:

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL for the FastAPI backend | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_APP_URL` | Canonical app URL for PWA and redirects | `http://localhost:3000` |

---

## 8. Demo & Offline Assumptions

1. **Standalone Demo Mode:** The frontend client (`lib/api/client.ts`) includes an integrated, typed mock data layer. If the backend is not yet started or is offline, all routes, forms, dose actions, scans, voice intents, and role transitions function smoothly.
2. **Evaluation Accounts:** Pre-filled credentials on the login screen (`DEVI-7892` / `123456`) allow immediate walkthroughs of Savitri Devi's Care Circle.
3. **Role Switcher Navigation:** A role-switcher bar is available in the top navbar (`Elder`, `Caretaker`, `Family`, `Doctor`) to allow evaluators to inspect different role perspectives without tedious logout/login steps.
4. **Offline Resilience:** The PWA service worker (`public/sw.js`) caches app shells and displays an offline fallback banner and page (`public/offline.html`) if disconnected.

---

## 9. Safety, Privacy & Clinical Disclaimers

> **Advisory Disclaimer:** CareCircle is an everyday routine coordination and medication reminder tool. It is **not** a certified medical device, diagnostic system, or treatment provider. 
> 
> - Vision scan results are always presented as **drafts** and must be verified by a human.
> - Voice answers are generated strictly from stored prescription fields.
> - Digital Twin forecasts and risk flags are purely advisory and based on routine timing, not clinical physiology.
> - The elderly individual retains final authority over carecircle permissions and schedule modifications.
