from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'replace-with-a-secure-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coverless.db'
    db.init_app(app)
    login_manager.init_app(app)

    from .models import User, MessageLog
    with app.app_context():
        db.create_all()

    from .routes import auth_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
