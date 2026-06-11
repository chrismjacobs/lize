# Li-Ze Academy App 麗澤書院

A companion web app for the Li-Ze Academy intercultural programme at Ming Chi University of Technology (MCUT), Taiwan, run by the Office of International Affairs (OIA).

---

## Quick Start (local development)

**Requirements:** Python 3.10+

```bash
# 1. Clone and enter the project
git clone https://github.com/chrismjacobs/lize
cd lize

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file (copy from example, then fill in real values)
cp .env.example .env

# 5. Initialise the database and seed starter data
python seed.py

# 6. Run the app
flask run
```

The app will be available at `http://localhost:5000`.

---

## Environment Variables (.env)

| Variable | Description |
|---|---|
| `SECRET_KEY` | Long random string — change before deploying |
| `DATABASE_URL` | `sqlite:///lize.db` for local; set automatically on Render |
| `AWS_ACCESS_KEY_ID` | Your AWS IAM key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS IAM secret |
| `AWS_S3_BUCKET` | S3 bucket name (e.g. `lize`) |
| `AWS_S3_REGION` | AWS region (e.g. `ap-northeast-1`) |
| `ADMIN_EMAIL` | Email for the first staff/admin account |
| `ADMIN_PASSWORD` | Password for the first staff/admin account |

**Important:** Never commit `.env` to Git. It is in `.gitignore`.

---

## S3 Bucket Setup

1. Log in to the AWS Console
2. Go to **S3 → Create bucket**
   - Bucket name: `lize`
   - Region: `ap-northeast-1` (Tokyo) — closest to Taiwan
   - **Uncheck** "Block all public access" (photos need to be publicly readable)
   - Enable versioning (optional but recommended)
3. Go to **Permissions → Bucket Policy** and add:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicRead",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::lize/*"
  }]
}
```
4. Ensure the IAM user's key (in `.env`) has `s3:PutObject`, `s3:DeleteObject`, and `s3:GetObject` permissions on this bucket.

---

## Deploying to Render

1. Push the project to GitHub: `https://github.com/chrismjacobs/lize`
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect the GitHub repo
4. Settings:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
5. Add all environment variables from `.env` in the Render **Environment** tab
   - Generate a new `SECRET_KEY` for production (use `python -c "import secrets; print(secrets.token_hex(32))"`)
6. Click **Deploy**

After first deploy, run the seed script in Render's shell:
```bash
python seed.py
```

---

## Keeping the App Awake (UptimeRobot)

Render's free tier sleeps after 15 minutes of inactivity. To prevent this:

1. Create a free account at [uptimerobot.com](https://uptimerobot.com)
2. Add a new monitor:
   - **Monitor type:** HTTP(S)
   - **URL:** `https://your-app-name.onrender.com/health`
   - **Monitoring interval:** Every 15 minutes
3. That's it — UptimeRobot will ping the `/health` endpoint every 15 minutes to keep the app awake.

The app also shows a friendly "waking up" screen if the backend is slow to respond on first load.

---

## Project Structure

```
lize/
├── app.py              # Flask entry point — creates the app
├── config.py           # Reads .env and exposes config values
├── models.py           # SQLAlchemy database models
├── seed.py             # One-time script: creates DB + seeds data
├── s3_utils.py         # Helpers for uploading/deleting S3 files
├── routes/
│   ├── public.py       # Public pages (home, events, about)
│   ├── auth.py         # Login, register, logout
│   ├── student.py      # Student dashboard and journal
│   └── staff.py        # Admin panel
├── templates/
│   ├── base.html       # Shared layout (nav, footer, flash messages)
│   ├── index.html      # Home page
│   ├── events.html     # Event list
│   ├── event_detail.html
│   ├── about.html
│   ├── auth/           # login.html, register.html
│   ├── student/        # dashboard.html, journal_form.html, journal_view.html
│   └── staff/          # dashboard.html, events.html, event_form.html,
│                       # photo_queue.html, journal_view.html, page_edit.html
├── static/
│   ├── css/main.css    # All custom styles
│   └── js/app.js       # Wake-up screen, audio recorder, UI helpers
├── requirements.txt
├── README.md
└── CLAUDE.md           # Maintenance guide for non-technical staff
```

---

## User Roles

| Role | Access |
|---|---|
| **Public** | Browse events, view schedules and galleries. No login needed. |
| **Student** | Register/login → personal journal, reflections, photo/audio uploads, points. |
| **Staff** | Admin panel → manage events, approve photos, view all journals, edit pages. |

---

## Points System

| Action | Points |
|---|---|
| Written reflection | 10 |
| + Photo upload | +5 |
| + Audio recording | +5 |
| **Maximum per event** | **20** |

---

## Database

SQLite file at `lize.db` (local) or `instance/lize.db` (Render persistent disk).

To reset the database entirely:
```bash
rm lize.db
python seed.py
```
