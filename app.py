from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from config import Config
from models import db
from models.user import User
from views.auth import auth_bp
from views.student import student_bp
from views.admin import admin_bp
from extensions import mail  # import here

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)  # initialize mail here

    # init extensions
    db.init_app(app)
    mail.init_app(app)

    # flask-login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_student():
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
