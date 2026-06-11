"""
One-time migration: adds share_anonymous column to journal_entries.
Safe to run multiple times (uses IF NOT EXISTS).

Usage:
    python migrate_add_share_anonymous.py
"""
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.session.execute(db.text(
        "ALTER TABLE journal_entries "
        "ADD COLUMN IF NOT EXISTS share_anonymous BOOLEAN DEFAULT FALSE"
    ))
    db.session.commit()
    print("Done — share_anonymous column added (or already existed).")
