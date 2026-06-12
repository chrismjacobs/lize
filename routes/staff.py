import json
from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
import re
from models import db, User, Event, JournalEntry, Page, Attendance, AllowedStudent
from s3_utils import upload_file_to_s3, delete_s3_file
from checkin_utils import verify_token

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ─────────────────────────────────────────────────────────────────

@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    events = Event.query.order_by(Event.date.desc()).all()
    students = User.query.filter_by(role='student').all()
    pending_photos = JournalEntry.query.filter(
        JournalEntry.share_anonymous == True,
        JournalEntry.is_approved == None
    ).count()
    total_entries = JournalEntry.query.count()
    total_checkins = Attendance.query.count()
    return render_template('staff/dashboard.html',
                           events=events,
                           students=students,
                           pending_photos=pending_photos,
                           total_entries=total_entries,
                           total_checkins=total_checkins)


# ── Events ─────────────────────────────────────────────────────────────────────

@staff_bp.route('/events')
@login_required
@staff_required
def events():
    all_events = Event.query.order_by(Event.date.desc()).all()
    return render_template('staff/events.html', events=all_events)


@staff_bp.route('/events/new', methods=['GET', 'POST'])
@login_required
@staff_required
def new_event():
    if request.method == 'POST':
        return _save_event(None)
    return render_template('staff/event_form.html', event=None)


@staff_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        return _save_event(event)
    return render_template('staff/event_form.html', event=event)


def _save_event(event):
    title = request.form.get('title', '').strip()
    if not title:
        flash('Event title is required.', 'danger')
        return render_template('staff/event_form.html', event=event)

    if event is None:
        event = Event()
        db.session.add(event)

    event.title = title
    event.short_description = request.form.get('short_description', '').strip()

    # Build structured description JSON from individual fields
    try:
        expect_items = json.loads(request.form.get('desc_expect', '[]'))
    except (json.JSONDecodeError, ValueError):
        expect_items = []
    event.full_description_html = json.dumps({
        'intro':   request.form.get('desc_intro', '').strip(),
        'details': request.form.get('desc_details', '').strip(),
        'expect':  [i for i in expect_items if i.strip()],
        'closing': request.form.get('desc_closing', '').strip(),
    })
    event.location = request.form.get('location', '').strip()
    event.capacity = request.form.get('capacity', 0, type=int)
    event.registered_count = request.form.get('registered_count', 0, type=int)
    event.registration_url = request.form.get('registration_url', '').strip()
    event.is_published = request.form.get('is_published') == 'on'

    date_str = request.form.get('date', '').strip()
    if date_str:
        try:
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass

    # Reflection prompts — one per line
    prompts_raw = request.form.get('reflection_prompts', '')
    event.reflection_prompts = [p.strip() for p in prompts_raw.splitlines() if p.strip()]

    # Per-event student enrollment list (empty = open to all)
    enrolled_raw = request.form.get('enrolled_student_ids', '')
    event.enrolled_student_ids = list(set(re.findall(r'\b\d{8}\b', enrolled_raw)))

    # Chinese version (all optional)
    event.title_zh = request.form.get('title_zh', '').strip() or None
    event.short_description_zh = request.form.get('short_description_zh', '').strip() or None
    zh_expect = [i.strip() for i in request.form.get('desc_expect_zh', '').splitlines() if i.strip()]
    event.full_description_zh = json.dumps({
        'intro':   request.form.get('desc_intro_zh', '').strip(),
        'details': request.form.get('desc_details_zh', '').strip(),
        'expect':  zh_expect,
        'closing': request.form.get('desc_closing_zh', '').strip(),
    }, ensure_ascii=False) if event.title_zh else None
    prompts_zh_raw = request.form.get('reflection_prompts_zh', '')
    event.reflection_prompts_zh = [p.strip() for p in prompts_zh_raw.splitlines() if p.strip()]

    # Hero image upload
    hero = request.files.get('hero_image')
    if hero and hero.filename:
        try:
            if event.hero_image_url:
                delete_s3_file(event.hero_image_url)
            event.hero_image_url = upload_file_to_s3(hero, folder='events/hero')
        except Exception as e:
            flash(f'Hero image upload failed: {e}', 'warning')

    # Gallery image upload (multiple)
    gallery_files = request.files.getlist('gallery_images')
    existing_gallery = event.gallery_images
    for gf in gallery_files:
        if gf and gf.filename:
            try:
                url = upload_file_to_s3(gf, folder='events/gallery')
                existing_gallery.append(url)
            except Exception as e:
                flash(f'Gallery image upload failed: {e}', 'warning')
    event.gallery_images = existing_gallery

    db.session.commit()
    flash('Event saved.', 'success')
    return redirect(url_for('staff.events'))


@staff_bp.route('/events/<int:event_id>/gallery/remove', methods=['POST'])
@login_required
@staff_required
def remove_gallery_image(event_id):
    event = Event.query.get_or_404(event_id)
    url = request.form.get('url', '')
    gallery = [u for u in event.gallery_images if u != url]
    event.gallery_images = gallery
    delete_s3_file(url)
    db.session.commit()
    flash('Gallery image removed.', 'success')
    return redirect(url_for('staff.edit_event', event_id=event_id))


@staff_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@staff_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(url_for('staff.events'))


# ── Reflection Approval Queue ──────────────────────────────────────────────────

@staff_bp.route('/reflections')
@login_required
@staff_required
def photo_queue():
    pending = (JournalEntry.query
               .filter(JournalEntry.share_anonymous == True,
                       JournalEntry.is_approved == None)
               .order_by(JournalEntry.created_at.asc())
               .all())
    return render_template('staff/photo_queue.html', pending=pending)


@staff_bp.route('/reflections/<int:entry_id>/approve', methods=['POST'])
@login_required
@staff_required
def approve_photo(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    entry.is_approved = True
    db.session.commit()
    flash('Reflection approved — it will appear on the event page.', 'success')
    return redirect(url_for('staff.photo_queue'))


@staff_bp.route('/reflections/<int:entry_id>/reject', methods=['POST'])
@login_required
@staff_required
def reject_photo(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    entry.is_approved = False
    db.session.commit()
    flash('Reflection rejected — it stays private to the student.', 'info')
    return redirect(url_for('staff.photo_queue'))


# ── Journal View ───────────────────────────────────────────────────────────────

@staff_bp.route('/journals')
@login_required
@staff_required
def journals():
    entries = (JournalEntry.query
               .order_by(JournalEntry.created_at.desc())
               .all())
    students = User.query.filter_by(role='student').order_by(User.name).all()
    selected_student_id = request.args.get('student_id', type=int)
    if selected_student_id:
        entries = [e for e in entries if e.user_id == selected_student_id]
    return render_template('staff/journal_view.html',
                           entries=entries,
                           students=students,
                           selected_student_id=selected_student_id)


# ── Page Content Editing ───────────────────────────────────────────────────────

@staff_bp.route('/pages/<slug>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit_page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    if request.method == 'POST':
        page.content_html = request.form.get('content_html', '')
        page.content_html_zh = request.form.get('content_html_zh', '') or None
        page.title = request.form.get('title', page.title)
        page.last_updated_by = current_user.id

        img = request.files.get('image')
        if img and img.filename:
            try:
                page.image_url = upload_file_to_s3(img, folder='pages')
            except Exception as e:
                flash(f'Image upload failed: {e}', 'warning')

        db.session.commit()
        flash('Page updated.', 'success')
        return redirect(url_for('staff.dashboard'))
    return render_template('staff/page_edit.html', page=page)


# ── QR Check-in ────────────────────────────────────────────────────────────────

@staff_bp.route('/scanner')
@login_required
@staff_required
def scanner():
    events   = Event.query.filter_by(is_published=True).order_by(Event.date.desc()).all()
    students = User.query.order_by(User.name).all()  # includes staff for self-checkin
    return render_template('staff/scanner.html', events=events, students=students)


@staff_bp.route('/api/checkin', methods=['POST'])
@login_required
@staff_required
def api_checkin():
    data  = request.get_json(silent=True) or {}
    token = data.get('token', '')
    try:
        user_id, event_id = verify_token(token)
    except ValueError as e:
        return {'success': False, 'error': str(e)}, 400

    user  = User.query.get(user_id)
    event = Event.query.get(event_id)
    if not user or not event:
        return {'success': False, 'error': 'Student or event not found'}, 404

    existing = Attendance.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing:
        return {'success': False, 'already': True,
                'name': user.name, 'event': event.title}, 200

    attendance = Attendance(
        user_id=user_id,
        event_id=event_id,
        stamps=1,
        checked_in_by_id=current_user.id,
        method='qr',
    )
    db.session.add(attendance)
    db.session.commit()
    stamp_count = sum(a.stamps for a in user.attendances)
    return {'success': True, 'name': user.name,
            'event': event.title, 'stamp_count': stamp_count}, 200


@staff_bp.route('/checkin/manual', methods=['POST'])
@login_required
@staff_required
def manual_checkin():
    user_id  = request.form.get('user_id',  type=int)
    event_id = request.form.get('event_id', type=int)
    if not user_id or not event_id:
        flash('Please select both a person and an event.', 'warning')
        return redirect(url_for('staff.scanner'))

    user  = User.query.get_or_404(user_id)
    event = Event.query.get_or_404(event_id)

    existing = Attendance.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing:
        flash(f'{user.name} is already checked in to {event.title}.', 'info')
    else:
        db.session.add(Attendance(
            user_id=user_id,
            event_id=event_id,
            stamps=1,
            checked_in_by_id=current_user.id,
            method='manual',
        ))
        db.session.commit()
        flash(f'Checked in {user.name} for {event.title}.', 'success')

    return redirect(url_for('staff.scanner'))


@staff_bp.route('/attendance/<int:attendance_id>/presenter', methods=['POST'])
@login_required
@staff_required
def mark_presenter(attendance_id):
    record = Attendance.query.get_or_404(attendance_id)
    record.stamps = 2
    db.session.commit()
    flash(f'Presenter double-stamp added for {record.user.name}.', 'success')
    return redirect(request.referrer or url_for('staff.scanner'))


# ── Allowed students ───────────────────────────────────────────────────────────

@staff_bp.route('/allowed-students', methods=['GET', 'POST'])
@login_required
@staff_required
def allowed_students():
    if request.method == 'POST':
        raw = request.form.get('student_ids', '')
        ids = list(set(re.findall(r'\b\d{8}\b', raw)))
        AllowedStudent.query.delete()
        for sid in ids:
            db.session.add(AllowedStudent(student_id=sid))
        db.session.commit()
        flash(f'{len(ids)} student ID{"s" if len(ids) != 1 else ""} saved.', 'success')
        return redirect(url_for('staff.allowed_students'))

    allowed = AllowedStudent.query.order_by(AllowedStudent.student_id).all()
    registered_ids = {u.student_id for u in User.query.filter(User.student_id != None).all()}
    return render_template('staff/allowed_students.html',
                           allowed=allowed,
                           registered_ids=registered_ids)
