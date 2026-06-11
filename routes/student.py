from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Event, JournalEntry, Attendance
from s3_utils import upload_file_to_s3
import random

student_bp = Blueprint('student', __name__, url_prefix='/student')

MAX_PHOTOS = 5


@student_bp.route('/dashboard')
@login_required
def dashboard():
    attended_records = (Attendance.query
                        .filter_by(user_id=current_user.id)
                        .order_by(Attendance.checked_in_at.asc())
                        .all())
    attended_ids = {a.event_id for a in attended_records}

    all_events = Event.query.filter_by(is_published=True).order_by(Event.date.asc()).all()

    entries = (JournalEntry.query
               .filter_by(user_id=current_user.id)
               .order_by(JournalEntry.created_at.desc())
               .all())
    journaled_ids = {e.event_id for e in entries}

    stamp_count = sum(a.stamps for a in attended_records)

    return render_template(
        'student/dashboard.html',
        attended_records=attended_records,
        attended_ids=attended_ids,
        all_events=all_events,
        entries=entries,
        journaled_ids=journaled_ids,
        stamp_count=stamp_count,
        total_points=current_user.total_points,
    )


# ── Check-in QR ────────────────────────────────────────────────────────────────

@student_bp.route('/checkin/<int:event_id>')
@login_required
def checkin_qr(event_id):
    event = Event.query.get_or_404(event_id)
    if not event.is_published:
        abort(404)
    attended = bool(Attendance.query.filter_by(
        user_id=current_user.id, event_id=event_id).first())
    return render_template('student/checkin_qr.html', event=event, attended=attended)


@student_bp.route('/api/checkin-token/<int:event_id>')
@login_required
def api_checkin_token(event_id):
    from checkin_utils import make_token, TOKEN_TTL
    event = Event.query.get_or_404(event_id)
    if not event.is_published:
        return {'error': 'event not found'}, 404
    token = make_token(current_user.id, event_id)
    return {'token': token, 'ttl': TOKEN_TTL}


@student_bp.route('/api/checkin-status/<int:event_id>')
@login_required
def api_checkin_status(event_id):
    attended = bool(Attendance.query.filter_by(
        user_id=current_user.id, event_id=event_id).first())
    return {'attended': attended}


# ── Journal ─────────────────────────────────────────────────────────────────────

@student_bp.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new_journal():
    # Staff can always journal; students must be checked in first
    if current_user.is_staff:
        events = Event.query.filter_by(is_published=True).order_by(Event.date.desc()).all()
    else:
        attended_ids_list = [
            a.event_id for a in Attendance.query.filter_by(user_id=current_user.id).all()
        ]
        if not attended_ids_list:
            flash('You need to check in to an event before writing a reflection.', 'info')
            return redirect(url_for('student.dashboard'))
        events = (Event.query
                  .filter(Event.id.in_(attended_ids_list), Event.is_published == True)
                  .order_by(Event.date.desc())
                  .all())

    if request.method == 'POST':
        event_id = request.form.get('event_id', type=int)
        written  = request.form.get('written_reflection', '').strip()
        share_photos = request.form.get('share_photos') == 'yes'

        event = Event.query.get(event_id)
        if not event:
            flash('Please select a valid event.', 'danger')
            return render_template('student/journal_form.html', events=events)

        # Attendance check for students
        if not current_user.is_staff:
            if not Attendance.query.filter_by(
                    user_id=current_user.id, event_id=event_id).first():
                flash('You need to check in to this event before writing a reflection.', 'warning')
                return redirect(url_for('student.checkin_qr', event_id=event_id))

        existing = JournalEntry.query.filter_by(
            user_id=current_user.id, event_id=event_id).first()
        if existing:
            flash('You have already submitted a journal entry for this event.', 'warning')
            return redirect(url_for('student.view_journal', entry_id=existing.id))

        # Photos
        photos = []
        photo_files = request.files.getlist('photos')[:MAX_PHOTOS]
        for pf in photo_files:
            if pf and pf.filename:
                try:
                    url = upload_file_to_s3(pf, folder='journal/photos')
                    visibility = 'pending' if share_photos else 'private'
                    photos.append({'url': url, 'visibility': visibility})
                except Exception as e:
                    flash(f'One photo failed to upload: {e}', 'warning')

        # Audio
        audio_url = None
        audio = request.files.get('audio')
        if audio and audio.filename:
            try:
                audio_url = upload_file_to_s3(audio, folder='audio')
            except Exception as e:
                flash(f'Audio upload failed: {e}', 'warning')

        # Points: 10 base + 5 photos + 5 audio
        points = 10
        if photos:
            points += 5
        if audio_url:
            points += 5

        share_anon = request.form.get('share_anonymous') == '1'

        entry = JournalEntry(
            user_id=current_user.id,
            event_id=event_id,
            written_reflection=written or None,
            audio_url=audio_url,
            points_awarded=points,
            share_anonymous=share_anon,
        )
        entry.photos = photos
        db.session.add(entry)
        db.session.commit()

        flash('Reflection saved!', 'success')
        return redirect(url_for('student.dashboard'))

    selected_event_id = request.args.get('event_id', type=int)
    # If directed here for an event but not checked in, redirect to QR
    if selected_event_id and not current_user.is_staff:
        if not Attendance.query.filter_by(
                user_id=current_user.id, event_id=selected_event_id).first():
            flash('Check in to this event first, then you can write your reflection.', 'info')
            return redirect(url_for('student.checkin_qr', event_id=selected_event_id))

    selected_event = Event.query.get(selected_event_id) if selected_event_id else None
    return render_template('student/journal_form.html',
                           events=events,
                           selected_event=selected_event,
                           max_photos=MAX_PHOTOS)


@student_bp.route('/journal/<int:entry_id>')
@login_required
def view_journal(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id and not current_user.is_staff:
        flash('You do not have permission to view that entry.', 'danger')
        return redirect(url_for('student.dashboard'))
    return render_template('student/journal_view.html', entry=entry)


@student_bp.route('/journal/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journal(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id and not current_user.is_staff:
        abort(403)

    if request.method == 'POST':
        entry.written_reflection = request.form.get('written_reflection', '').strip() or None
        entry.share_anonymous = request.form.get('share_anonymous') == '1'

        # Add new photos (append to existing, cap at MAX_PHOTOS total)
        share_photos = request.form.get('share_photos') == 'yes'
        photo_files = request.files.getlist('photos')
        existing = entry.photos
        new_photos = []
        slots_left = MAX_PHOTOS - len(existing)
        for pf in photo_files[:max(slots_left, 0)]:
            if pf and pf.filename:
                try:
                    url = upload_file_to_s3(pf, folder='journal/photos')
                    visibility = 'pending' if share_photos else 'private'
                    new_photos.append({'url': url, 'visibility': visibility})
                except Exception as e:
                    flash(f'One photo failed to upload: {e}', 'warning')
        if new_photos:
            entry.photos = existing + new_photos

        # New audio replaces old
        audio = request.files.get('audio')
        if audio and audio.filename:
            try:
                entry.audio_url = upload_file_to_s3(audio, folder='audio')
            except Exception as e:
                flash(f'Audio upload failed: {e}', 'warning')

        db.session.commit()
        flash('Reflection updated.', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/journal_form.html',
                           entry=entry,
                           events=[entry.event],
                           max_photos=MAX_PHOTOS)
