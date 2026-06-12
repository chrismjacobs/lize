from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.staff import staff_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(staff_bp)

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.context_processor
    def inject_lang():
        from flask import session
        return {'lang': session.get('lang', 'en')}

    # Migrations — safe to run on every startup; no-op if already applied
    with app.app_context():
        db.create_all()
        for sql in [
            "ALTER TABLE journal_entries ADD COLUMN share_anonymous BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN student_id VARCHAR(8)",
            "ALTER TABLE events ADD COLUMN title_zh VARCHAR(200)",
            "ALTER TABLE events ADD COLUMN short_description_zh TEXT",
            "ALTER TABLE events ADD COLUMN full_description_zh TEXT",
            "ALTER TABLE events ADD COLUMN reflection_prompts_zh TEXT",
            "ALTER TABLE pages ADD COLUMN content_html_zh TEXT",
            "ALTER TABLE events ADD COLUMN enrolled_student_ids TEXT DEFAULT '[]'",
            "ALTER TABLE journal_entries ADD COLUMN is_approved BOOLEAN",
        ]:
            try:
                db.session.execute(db.text(sql))
                db.session.commit()
            except Exception:
                db.session.rollback()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
