from flask import Flask, session, redirect, url_for
from app.extensions import db, mail, socketio, login_manager

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from flask_login import current_user, logout_user


load_dotenv()


def create_app():

    app = Flask(__name__)

    # -----------------------------
    # SECURITY / SESSION CONFIG
    # -----------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

    # Flask session lifetime
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=20)

    # Refresh active sessions
    app.config["SESSION_REFRESH_EACH_REQUEST"] = True


    # -----------------------------
    # SAFETY CHECK (SIEM HARDENING)
    # -----------------------------
    required_vars = [
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_NAME"
    ]

    for var in required_vars:

        if not os.getenv(var):
            raise ValueError(
                f"[SIEM ERROR] Missing environment variable: {var}"
            )


    # -----------------------------
    # DATABASE CONFIG
    # -----------------------------
    app.config['SQLALCHEMY_DATABASE_URI'] = (

        f"mysql+pymysql://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/"
        f"{os.getenv('DB_NAME')}"
    )


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



    # -----------------------------
    # EMAIL CONFIG
    # -----------------------------
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')

    app.config['MAIL_PORT'] = int(
        os.getenv('MAIL_PORT', 587)
    )

    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    app.config['MAIL_USERNAME'] = os.getenv(
        'MAIL_USERNAME'
    )

    app.config['MAIL_PASSWORD'] = os.getenv(
        'MAIL_PASSWORD'
    )

    app.config['MAIL_DEFAULT_SENDER'] = os.getenv(
        'MAIL_DEFAULT_SENDER'
    )



    # -----------------------------
    # INIT EXTENSIONS
    # -----------------------------
    db.init_app(app)

    mail.init_app(app)

    socketio.init_app(app)

    login_manager.init_app(app)



    # -----------------------------
    # FLASK LOGIN CONFIG
    # -----------------------------
    login_manager.login_view = "auth.login"

    login_manager.session_protection = "strong"

    login_manager.remember_cookie_duration = timedelta(days=30)

    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SECURE"] = False
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"



    # -----------------------------
    # ADMIN ACTIVITY SESSION CONTROL
    # -----------------------------
    @app.before_request
    def check_admin_activity():

        if current_user.is_authenticated:

            timeout = timedelta(minutes=20)

            now = datetime.utcnow()


            # Check inactivity period
            if current_user.last_activity:

                inactive_time = (
                    now - current_user.last_activity
                )


                if inactive_time > timeout:

                    logout_user()

                    session.clear()

                    return redirect(
                        url_for("auth.login")
                    )


            # Update activity timestamp
            current_user.last_activity = now

            db.session.commit()



    # -----------------------------
    # IMPORT + REGISTER BLUEPRINTS
    # -----------------------------
    from app.routes.log_routes import log_bp
    from app.routes.report_routes import report_bp
    from app.routes.ai import ai_bp
    from app.routes.chat import chat_bp
    from app.routes.geo_routes import geo_bp
    from app.auth import auth_bp



    app.register_blueprint(log_bp)

    app.register_blueprint(report_bp)

    app.register_blueprint(chat_bp)

    app.register_blueprint(
        ai_bp,
        url_prefix="/ai"
    )

    app.register_blueprint(geo_bp)

    app.register_blueprint(auth_bp)



    # -----------------------------
    # STARTUP LOG
    # -----------------------------
    print(
        "[SIEM] Flask application initialized successfully"
    )


    return app