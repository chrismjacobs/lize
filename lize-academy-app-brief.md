# Li-Ze Academy App — Claude Code Project Brief

## Project Overview

The **Li-Ze Academy App** is a companion web application for the Li-Ze Academy programme run by the Office of International Affairs (OIA) at Ming Chi University of Technology (MCUT), Taiwan.

Li-Ze Academy is an intercultural programme where international and local students participate in themed activities together — host family visits, food/culture events, a cultural night, a buddy programme, and more. The app's purpose is to make the programme more meaningful and better organised, not to replace existing systems.

**Key principle:** If the app fails or is unavailable, the existing systems (university website, email, LINE group, Google Forms) continue to work as before. The app is a helpful layer on top, not a dependency.

**Long-term maintenance model:** The app will be maintained by a non-technical staff member using Claude Code as their maintenance tool. Code must therefore be clean, well-commented, and structured so that Claude Code can make targeted changes safely without deep technical knowledge.

---

## Users

| Role | Description |
|---|---|
| **Student (public)** | Any visitor — can browse events, schedules, fill rates. No login required. |
| **Student (enrolled)** | Logged-in students — can access their personal journal, log reflections, upload photos/audio, track points. |
| **OIA Staff** | Admin login — can manage events, view all student journals, edit page content, manage registrations overview. |

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Backend | **Flask (Python)** | Developer's existing skill set |
| Frontend | **Vue.js** (CDN, not build-tool) | Developer's existing skill set; keep simple |
| Database | **SQLite** | Zero cost, zero setup, sufficient for this scale |
| Media storage | **AWS S3** | Developer already has a bucket; photos and audio uploads go here, URLs stored in SQLite |
| Hosting | **Render (free tier)** | Free, deploys from GitHub |
| Source control | **GitHub** | Required for Render deployment; Claude Code integration |

### Frontend approach
Use Vue.js loaded via CDN (not a build pipeline). This keeps the project simple enough for a non-developer to understand and for Claude Code to modify safely. Jinja2 templates serve the HTML; Vue handles interactivity within pages.

### No SPA
Do **not** build this as a Single Page Application. Standard Flask routes with Vue.js enhancing individual pages is the correct architecture here.

---

## Hosting & Infrastructure Notes

### Render free tier sleep behaviour
Render's free tier sleeps after a period of inactivity. Two mitigations:

1. **Wake-up screen:** The frontend should detect when the backend is slow to respond on first load and display a friendly placeholder: *"Li-Ze Academy is waking up... 🌱 Please wait a moment."* Once the backend responds, dismiss it automatically.
2. **UptimeRobot:** A free UptimeRobot account should ping the app's `/health` endpoint every 15 minutes to prevent sleep. This is an external setup step, not part of the codebase — document it in the README.

### Health endpoint
Add a `/health` route to Flask that returns `{"status": "ok"}`. This is used by UptimeRobot and also by the frontend to detect when the backend is ready.

---

## Database Schema (SQLite)

```
users
  id, email, name, role (student | staff), nationality, created_at

events
  id, title, short_description, full_description_html,
  date, location, capacity, registered_count,
  registration_url (Google Form link),
  hero_image_url,           -- main event image (staff uploads)
  gallery_images (JSON),    -- list of S3 URLs for staff-uploaded past photos
  reflection_prompts (JSON), -- list of prompt strings, editable by staff
  is_published, created_at

journal_entries
  id, user_id, event_id, written_reflection (text, nullable),
  audio_url (S3 URL, nullable), photo_url (S3 URL, nullable),
  photo_visibility,         -- enum: private | pending | approved
  points_awarded, created_at

pages (for staff-editable content)
  id, slug, title, content_html, image_url, last_updated_by, updated_at
```

### Photo visibility flow
- When a student uploads a photo in their journal, they are asked: **"Would you like to share this photo in the event gallery?"**
- If **No** → `photo_visibility = private`. Photo is only visible to the student and staff in the full journal view. Never enters the approval queue.
- If **Yes** → `photo_visibility = pending`. Appears in the staff approval queue on the admin dashboard.
- Staff approves → `photo_visibility = approved`. Photo appears in the event's public gallery alongside staff-uploaded photos.

---

## Features by Phase

### Phase 1 — MVP (launch next semester)

**Public (no login)**
- Home page with programme description and featured activities
- Event schedule — list of upcoming events with date, short description, capacity, fill rate
- **Event detail page** (one per event) containing:
  - Hero image
  - Full description — what the event is, what to expect, practical info
  - Date, location, capacity, spots remaining
  - Register button (links to Google Form)
  - **Reflection prompts** — a set of questions to prime students before and after attending (e.g. for "Welcome to My Home": *"What did you notice about how the family organised their home?"*, *"Was there a moment that surprised you?"*). Editable by staff through the admin panel.
  - **Photo gallery** — staff-uploaded images from past runs of the event, plus student journal photos that have been approved by staff
- About / contact page

**Student (login required)**
- Register / login with email + password (simple, no OAuth for now)
- Personal dashboard — events attended, points total, journal entries
- Post-event journal entry form:
  - Select which event they attended
  - Written reflection (text area)
  - Audio recording (browser-based via MediaRecorder API, uploads to S3)
  - Photo upload (uploads to S3)
  - Submit → points awarded automatically
- View own past journal entries

**Staff (admin login)**
- Event management — create, edit, delete events; update fill rates manually; upload hero image and gallery photos
- Edit reflection prompts per event (simple list of questions, editable in the admin panel)
- Photo approval queue — review student-submitted photos marked as "share publicly"; approve or reject
- View all student journal entries (read-only), including private photos (for programme monitoring)
- Basic content editing for home/about pages (edit text and image)

---

### Phase 2 — Presentation Guide (next priority after MVP)

The journal system feeds a guided presentation builder. After attending multiple events and writing reflections, students are prompted to build their final presentation using their own content.

- Presentation checklist / guide page (replaces "upload slides and read text")
- Students can review all their journal entries in one view as preparation material
- Guided prompts: "What surprised you?", "What would you tell a friend about this event?", "Choose one photo that tells a story"
- Staff can see how prepared each student is based on journal completeness

---

### Phase 3 — Later / When Needed

- Google Forms data integration (read registration data via Google Sheets API to display in staff dashboard)
- Credits tracking (once the programme's credit system is understood)
- PWA / installable app with push notifications (infrastructure is already understood)
- Mandatory audio journaling enforcement (toggle in admin settings)
- AI-assisted reflection prompts (experimental)

---

## Journal Entry — Audio Recording Notes

- Use the browser's **MediaRecorder API** — no libraries needed, works on mobile and desktop
- Record as WebM/audio or MP4 audio depending on browser support
- Upload the recorded blob to S3 via a signed URL or a Flask upload endpoint
- Store the S3 URL in `journal_entries.audio_url`
- Staff can play back audio from the admin journal view
- Audio is optional in Phase 1; the system is designed so it can be made mandatory later via a single settings flag

---

## Project Structure (suggested)

```
lize-academy/
├── app.py                  # Flask app entry point
├── config.py               # Environment config (S3, secret key, etc.)
├── models.py               # SQLAlchemy models
├── routes/
│   ├── public.py           # Public routes (home, events, about)
│   ├── auth.py             # Login, register, logout
│   ├── student.py          # Student dashboard, journal
│   └── staff.py            # Admin routes
├── templates/
│   ├── base.html           # Base layout with Vue CDN included
│   ├── index.html
│   ├── events.html
│   ├── journal.html
│   └── admin/
│       ├── dashboard.html
│       ├── events.html
│       └── journal_view.html
├── static/
│   ├── css/
│   └── js/
│       └── app.js          # Vue component definitions
├── requirements.txt
├── README.md               # Includes UptimeRobot setup instructions
└── CLAUDE.md               # Instructions for Claude Code maintenance
```

---

## CLAUDE.md — Maintenance Instructions (to be created)

The `CLAUDE.md` file in the project root should include:

- What the app is and who it serves
- How to run it locally (virtualenv, `flask run`)
- Where to find the `.env` file / what environment variables are needed
- How database migrations work (simple: SQLite file, use Flask-Migrate or manual ALTER TABLE)
- How to deploy (push to GitHub → Render auto-deploys)
- Common tasks: adding an event type, changing page text, adding a new staff user
- S3 upload pattern (how media uploads work)
- "Make one change at a time and test before the next"

---

## Language

**English only.** Students are expected to use browser translation tools if needed. No bilingual UI required.

---

## What to Build First

Start with this sequence:

1. Project scaffold — Flask app, SQLite setup, folder structure, requirements.txt, README
2. `/health` endpoint
3. Database models and initial migration
4. Public event listing page (static data seeded in DB)
5. Student registration and login (email + password, session-based)
6. Journal entry form (written + photo upload to S3)
7. Student dashboard (own entries + points)
8. Staff login + basic event management
9. Wake-up screen (frontend detects slow backend response)
10. Deploy to Render + document UptimeRobot setup in README

Do not begin Phase 2 features until Phase 1 is live and tested with real users.

---

## Out of Scope (for now)

- OAuth / social login
- Real-time features (websockets, live fill-rate updates)
- Mobile app (PWA installability is a nice-to-have, not required)
- Replacing Google Forms registration
- Automated Google Forms data sync
- Credits / grade integration
- Multilingual UI
