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

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
