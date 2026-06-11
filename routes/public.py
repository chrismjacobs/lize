import random
from flask import Blueprint, render_template, abort
from flask_login import current_user
from models import Event, Page, Attendance, JournalEntry

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def home():
    page = Page.query.filter_by(slug='home').first()
    featured = Event.query.filter_by(is_published=True).order_by(Event.date.asc()).limit(3).all()
    return render_template('index.html', page=page, featured_events=featured)


@public_bp.route('/events')
def events():
    all_events = Event.query.filter_by(is_published=True).order_by(Event.date.asc()).all()
    return render_template('events.html', events=all_events)


@public_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    if not event.is_published:
        abort(404)
    user_attended = False
    if current_user.is_authenticated and not current_user.is_staff:
        user_attended = bool(Attendance.query.filter_by(
            user_id=current_user.id, event_id=event_id).first())

    anon_reflections = (JournalEntry.query
        .filter(
            JournalEntry.event_id == event_id,
            JournalEntry.share_anonymous == True,
            JournalEntry.written_reflection != None,
            JournalEntry.written_reflection != '',
        )
        .all())
    random.shuffle(anon_reflections)
    anon_reflections = anon_reflections[:5]

    return render_template('event_detail.html', event=event,
                           user_attended=user_attended,
                           anon_reflections=anon_reflections)


@public_bp.route('/about')
def about():
    page = Page.query.filter_by(slug='about').first()
    return render_template('about.html', page=page)
