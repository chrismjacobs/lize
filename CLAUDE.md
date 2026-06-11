# CLAUDE.md — Maintenance Guide for Li-Ze Academy App

This file is for the OIA staff member who maintains this app using Claude Code.
It explains how the app works, what the common tasks are, and how to make changes safely.

**Golden rule: Make one change at a time and test it before making the next one.**

---

## What This App Is

The Li-Ze Academy App is a companion app for the Li-Ze intercultural programme at MCUT.
It has three types of users:
- **Public visitors** — can browse events without logging in
- **Students** — log in to write journal entries (text, photo, audio) after attending events
- **OIA Staff (you)** — log in to manage events, approve photos, and view all journals

The app does not replace Google Forms registration, LINE groups, or email. If the app breaks,
everything continues to work as before. The app is a helpful extra layer, not a dependency.

---

## How to Run Locally

```bash
# In this folder:
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt
python seed.py                 # Only needed the first time, or after resetting the database
flask run
```

Then open `http://localhost:5000` in your browser.

---

## Key Files

| File | What it does |
|---|---|
| `app.py` | Creates and starts the Flask app. Rarely needs editing. |
| `config.py` | Reads environment variables. Rarely needs editing. |
| `models.py` | Defines the database tables. Edit carefully — changes need a migration. |
| `routes/public.py` | Public pages: home, events list, event detail, about. |
| `routes/auth.py` | Login, register, logout. |
| `routes/student.py` | Student dashboard and journal form. |
| `routes/staff.py` | Admin panel: events, photos, journals, page editing. |
| `templates/` | HTML templates. One file per page. |
| `static/css/main.css` | All visual styles — colours, cards, layout. |
| `static/js/app.js` | JavaScript: wake-up screen, audio recorder, small UI helpers. |
| `.env` | Secret keys and passwords. **Never commit this file to Git.** |
| `seed.py` | Populates the database with starter events and pages. |

---

## Common Tasks

### Add a new event
1. Log in as staff: go to `/staff/events` → **+ New Event**
2. Fill in the title, description, date, location, capacity, and registration URL
3. Add reflection prompts (one per line)
4. Upload a hero image if you have one
5. Toggle **Published** on and click Save

### Edit an existing event
1. Go to `/staff/events` → click **Edit** on the event
2. Make your changes
3. To update how many people have registered: change the **Registered Count** field manually
4. Click Save

### Upload photos to an event gallery
1. Edit the event → scroll to **Gallery Images** → choose files → Save

### Approve a student's shared photo
1. Go to `/staff/photos`
2. Review the photo — click **Approve** to add it to the event gallery, or **Reject** to return it to the student's private journal

### View all student journal entries
1. Go to `/staff/journals`
2. Use the dropdown to filter by student if needed

### Edit the Home or About page text
1. Go to `/staff/dashboard` → click **Home Page** or **About Page** in the sidebar
2. Edit the HTML content
3. Save

---

## Adding a New Staff Account

There is no self-registration for staff. To add a new staff member:

1. Have them register a normal student account first
2. Then update their role in the database:

```bash
# Open Python in the project directory with venv active:
python
```
```python
from app import create_app
from models import db, User
app = create_app()
with app.app_context():
    user = User.query.filter_by(email='newstaff@mcut.edu.tw').first()
    user.role = 'staff'
    db.session.commit()
    print('Done')
```

---

## Database Changes (Advanced)

The database is SQLite. The file is `lize.db` (local) or on Render's persistent disk.

If you need to add a new column to an existing table:
1. Edit `models.py` to add the new field
2. Run `flask db migrate -m "description of change"`
3. Run `flask db upgrade`

If the migration tools are not set up, the manual approach is:
```bash
python -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
"
```
(This is safe — `create_all` only adds new tables/columns, it does not delete anything.)

---

## Deploying Changes

1. Make your change locally and test it
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Brief description of what you changed"
   git push
   ```
3. Render will automatically detect the push and redeploy. This takes 1–3 minutes.
4. Check the Render dashboard for any errors.

---

## S3 Media Uploads

Photos and audio recordings are uploaded to an AWS S3 bucket called `lize`.

- Photos go to: `s3://lize/photos/`
- Audio recordings go to: `s3://lize/audio/`
- Event hero images go to: `s3://lize/events/hero/`
- Event gallery images go to: `s3://lize/events/gallery/`
- Page images go to: `s3://lize/pages/`

The S3 credentials are in `.env`. Do not share them. If you need to rotate the credentials,
update `.env` locally AND update the environment variables in the Render dashboard.

---

## Troubleshooting

**App is slow to load / shows "waking up" screen**
This is normal for the Render free tier. It sleeps after 15 minutes of inactivity.
UptimeRobot pings it every 15 minutes to prevent this — check that UptimeRobot is still active.

**Photo upload fails**
Check that the S3 bucket exists and the bucket policy allows public reads.
See the S3 setup section in README.md.

**"Internal Server Error" on Render**
Check the Render logs: Render dashboard → your service → Logs.
The error message will tell you what went wrong.

**Database is corrupted or needs resetting**
On Render: go to Shell → `rm lize.db && python seed.py`
Locally: `rm lize.db && python seed.py`
Warning: this deletes all student journal entries.

---

## What NOT to Change

- Do not edit `flask_login`, `flask_sqlalchemy`, or any library code in `venv/`
- Do not commit `.env` to Git
- Do not change the `role` field values (`student`, `staff`) — the whole auth system depends on them
- Do not delete `CLAUDE.md` or `README.md`
