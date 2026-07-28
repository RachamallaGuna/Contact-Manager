import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # --- Database config ---
    # Uses MySQL if DB_* env vars are set, otherwise falls back to local SQLite
    # so the app is easy to run/demo without setting up MySQL first.
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")

    if db_user and db_pass and db_host and db_name:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
        )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # 4MB upload cap

    # --- AWS S3 config (optional) ---
    app.config["AWS_S3_BUCKET"] = os.environ.get("AWS_S3_BUCKET")
    app.config["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
    app.config["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    app.config["AWS_REGION"] = os.environ.get("AWS_REGION", "us-east-1")

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth import auth_bp
    from app.contacts import contacts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(contacts_bp)

    with app.app_context():
        db.create_all()

    return app
