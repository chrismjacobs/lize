import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' | 'staff'
    nationality = db.Column(db.String(80))
    student_id = db.Column(db.String(8), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    journal_entries = db.relationship('JournalEntry', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_staff(self):
        return self.role == 'staff'

    @property
    def total_points(self):
        return sum(a.stamps * 5 for a in self.attendances)

    @property
    def stamp_count(self):
        return sum(a.stamps for a in self.attendances)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.String(300))
    full_description_html = db.Column(db.Text)
    date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    capacity = db.Column(db.Integer, default=0)
    registered_count = db.Column(db.Integer, default=0)
    registration_url = db.Column(db.String(500))
    hero_image_url = db.Column(db.String(500))
    _gallery_images = db.Column('gallery_images', db.Text, default='[]')
    _reflection_prompts = db.Column('reflection_prompts', db.Text, default='[]')
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    journal_entries = db.relationship('JournalEntry', backref='event', lazy=True)

    @property
    def description_data(self):
        """Returns structured description dict if stored as JSON, else None (legacy HTML)."""
        val = (self.full_description_html or '').strip()
        if val.startswith('{'):
            try:
                return json.loads(val)
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    @property
    def gallery_images(self):
        return json.loads(self._gallery_images or '[]')

    @gallery_images.setter
    def gallery_images(self, value):
        self._gallery_images = json.dumps(value)

    @property
    def reflection_prompts(self):
        return json.loads(self._reflection_prompts or '[]')

    @reflection_prompts.setter
    def reflection_prompts(self, value):
        self._reflection_prompts = json.dumps(value)

    @property
    def spots_remaining(self):
        if self.capacity == 0:
            return None
        return max(0, self.capacity - self.registered_count)

    @property
    def fill_percent(self):
        if not self.capacity:
            return 0
        return min(100, int((self.registered_count / self.capacity) * 100))

    @property
    def approved_student_photos(self):
        result = []
        for entry in self.journal_entries:
            for photo in entry.photos:
                if photo['visibility'] == 'approved':
                    result.append(photo['url'])
        return result


class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    written_reflection = db.Column(db.Text)
    audio_url = db.Column(db.String(500))
    # Photos stored as JSON: [{"url": "...", "visibility": "private|pending|approved"}, ...]
    _photos = db.Column('photos', db.Text, default='[]')
    points_awarded = db.Column(db.Integer, default=0)
    share_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def photos(self):
        return json.loads(self._photos or '[]')

    @photos.setter
    def photos(self, value):
        self._photos = json.dumps(value)

    @property
    def has_photos(self):
        return bool(self.photos)

    @property
    def pending_photos(self):
        return [(i, p) for i, p in enumerate(self.photos) if p['visibility'] == 'pending']


class Attendance(db.Model):
    __tablename__ = 'attendances'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id         = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    stamps           = db.Column(db.Integer, default=1)       # 2 for presenter
    checked_in_at    = db.Column(db.DateTime, default=datetime.utcnow)
    checked_in_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    method           = db.Column(db.String(20), default='qr') # 'qr' | 'manual'

    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='uq_user_event_attendance'),
    )

    user          = db.relationship('User', foreign_keys=[user_id], backref='attendances')
    event         = db.relationship('Event', foreign_keys=[event_id], backref='attendances')
    checked_in_by = db.relationship('User', foreign_keys=[checked_in_by_id])


class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200))
    content_html = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    last_updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AllowedStudent(db.Model):
    __tablename__ = 'allowed_students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(8), unique=True, nullable=False)
