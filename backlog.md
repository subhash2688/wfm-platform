# WFM Platform — Backlog

## Apps

### 1. Cultivate (Corporate Giving) — IN PROGRESS
Corporate fundraising pipeline: prospect research, foundation 990 analysis, outreach emails, grant tracking, pipeline management.
- Status: Active development
- Entry point: `cultivate/run.py` → localhost:5001
- DB: `cultivate/data/wfm.db`

### 2. Rally (Volunteer Management) — PLANNED
Volunteer recruitment, scheduling, hours tracking, event coordination, impact reporting.
- Key workflows:
  - Volunteer registration & onboarding
  - Shift scheduling per campus (De Anza, Foothill, Chabot)
  - Hours logging & verification
  - Event creation & volunteer sign-up
  - Impact dashboard (hours served, meals packed, students reached)
  - Volunteer communications & reminders

### 3. Steward (Donor Management) — PLANNED
Individual donor CRM: donor profiles, gift tracking, acknowledgments, campaigns, retention.
- Key workflows:
  - Donor profile management (individuals, not corporates)
  - Gift entry & tracking (one-time, recurring, in-kind)
  - Acknowledgment/thank-you letter generation
  - Campaign management & progress tracking
  - Donor segmentation & retention analysis
  - Annual giving reports

---

## Rally — Volunteer App & Management Enhancement Backlog

> Context: ~100 volunteers now, scaling to ~200. Goal is to engage and retain existing volunteers.
> The volunteer app is a **mobile browser app** (not App Store). Volunteers open it on their phone or save to home screen.
> Photo upload, youth volunteer flag, shift type preferences already shipped (Feb 2026).

### Tier 1 — Build next (high emotional impact, mostly small effort)

| # | Feature | Side | Description |
|---|---------|------|-------------|
| 1 | **Shift day home screen** | Volunteer app | Home page transforms on shift day — prominent card at top with shift time, one-tap check-in, "X others are coming with you." Nothing currently changes on shift day. |
| 2 | **Post-shift acknowledgment** | Volunteer app | When a shift completes, show in My Shifts: "You helped serve ~80 students at De Anza. Thank you." Currently completed shifts silently appear in Past with no moment of recognition. |
| 3 | **Mission strip** | Volunteer app | Permanent "No Student Goes Hungry" line visible on every page, just below the header. Always present, never intrusive. |
| 4 | **"Who's coming"** | Volunteer app | Shift detail shows names/count of other signed-up volunteers. Turns signing up from a solo task into joining a team. |
| 5 | **What to expect per shift type** | Volunteer app | Each shift type (Meal Prep, Packing, Serving, etc.) has a short brief on shift detail: what you'll actually do, what to wear, how it runs. Reduces new-volunteer anxiety and no-shows. |
| 6 | **Day-before in-app reminder** | Volunteer app | When volunteer opens app the day before a shift, home screen leads with: "Tomorrow: De Anza, 9am. 11 others are coming." No push notifications needed — detects shift date on page load. |
| 7 | **Urgent shift surfacing** | Volunteer app | Shifts under 50% filled within 48hrs get a highlighted section on home: "De Anza needs 4 more volunteers this Saturday." |

### Tier 2 — ✅ Shipped (Feb 2026)

| # | Feature | Side | Description |
|---|---------|------|-------------|
| 8 | **Availability setting UI** | Both | Field exists in DB but no mobile UI. Volunteers set which days/times work. Unlocks smart scheduling on staff side. |
| 9 | **SMS shift reminder** | Volunteer app | Automatic text the day before a shift. SMS infrastructure already in the stack. More reliable than push notifications. |
| 10 | **Smart gap filling** | Management | Gaps page shows which available volunteers haven't signed up yet — with one-click contact. Turns a report into an action list. |
| 11 | **Volunteer engagement health** | Management | Per-volunteer: last app open, signup rate, check-in rate, cancellation rate. Know who's fading before they disappear. |
| 12 | **Shift briefing notes** | Both | Staff writes a short note per shift ("Parking: use B lot") — volunteers see it on shift detail and shift day card. First real two-way communication channel. |

### Tier 3 — Later (scale features)

| # | Feature | Side | Description |
|---|---------|------|-------------|
| 13 | **Availability heatmap** | Management | Dashboard widget showing which days have most available volunteers per campus. Schedule smarter. |
| 14 | **Volunteer activity feed** | Volunteer app | "Priya just signed up for De Anza Tuesday" — lightweight social proof on home page. |
| 15 | **Onboarding flow** | Volunteer app | 3-screen first-time experience after registration: WFM mission, what a shift looks like, what to expect. New-volunteer retention. |
| 16 | **Volunteer training modules** | Volunteer app | Short in-app training content per shift type — food safety basics, packing procedures, serving protocols. Volunteers complete before their first shift of that type. Staff can see completion status per volunteer. |
| 17 | **Volunteer onboarding checklist** | Both | After registration, volunteers see a checklist: complete profile → set availability → complete orientation training → sign up for first shift. Staff dashboard shows onboarding completion rate and flags new volunteers who have stalled. |

### Tier 4 — Volunteer ↔ Management Communication (big lift)

> Volunteers need a way to reach staff from inside the app — without relying on phone/WhatsApp for every question. This is the most requested feature type as the team grows past 100.

| # | Feature | Side | Description |
|---|---------|------|-------------|
| 18 | **Volunteer message inbox** | Both | Volunteers can tap "Message Staff" on any shift or profile page, write a short message (e.g. "I'll be 10 min late", "Is parking available?", "Can I bring a friend?"). Staff see an inbox on the management side with unread count in the nav. Replies go back to the volunteer's app. Each thread is tied to a volunteer (and optionally a shift). **New models needed:** Message (body, sender_type, volunteer_id, shift_id nullable, created_at, read_at), MessageThread. |
| 19 | **Shift cancellation with reason** | Volunteer app | When a volunteer cancels a shift, ask for a brief reason (dropdown: "conflict", "illness", "family", "other"). Staff see the reason alongside the cancellation in the management view. Helps distinguish reliable vs. at-risk volunteers and surfaces patterns. Low-lift addition to the existing cancel flow. |
| 20 | **Volunteer feedback after shift** | Volunteer app | 24 hours after a completed shift, volunteer sees a simple 1-tap rating card on home: "How did it go?" (3 emoji options) + optional one-line note. Staff see aggregate feedback per shift on the shift detail page. Closes the loop between doing the work and feeling heard. |
| 21 | **Staff broadcast message** | Management | Staff can compose a message sent to all active volunteers (or a filtered subset — by campus, by availability day). Delivered as SMS (via Twilio) and shown as a notification card on next app open. Use case: "Thanks everyone for a great pantry day!" or "We need extra help this Saturday at De Anza." |

**Technical complexity note:** Features 18–21 share a core communication model. #19 and #20 are the lightest lifts and can be built independently. #18 (full inbox) is the most complex — requires real-time-ish polling or periodic refresh on the management side, and a persistent thread model. #21 is straightforward given Twilio is already wired up. Suggested build order: 19 → 20 → 21 → 18.

---

## Shared Infrastructure

### Authentication & Authorization — PLANNED
- Login system shared across all three apps
- Role-based access: Admin, Staff, Volunteer, Read-only
- Options to evaluate:
  - Flask-Login with session-based auth (simplest)
  - OAuth2 / Google SSO (if team uses Google Workspace)
  - JWT tokens (if we add API access later)
- Shared user model in `shared/auth/`
- Single sign-on across Cultivate, Rally, Steward

### Shared Design System
- CSS variables/tokens: `shared/design/variables.css`
- Shared assets (logos, photos): `shared/assets/`
- Nav pattern: dark navy bar, Prabhupada photo, WFM logo, app-specific tabs
- Fonts: Karla (body), Bricolage Grotesque (headings)
- Color palette: #0067FF primary, #1d4288 nav, #E7F6FF bg

---

## Folder Structure

```
WFM/
  cultivate/          ← Corporate Giving app
  rally/              ← Volunteer Management (future)
  steward/            ← Donor Management (future)
  shared/
    design/           ← CSS tokens, design system reference
    assets/           ← WFM logos, Prabhupada photo
    auth/             ← Shared auth module (future)
  docs/               ← Strategy docs, playbooks, Excel
  backlog.md          ← This file
  CLAUDE.md           ← Project context
```
