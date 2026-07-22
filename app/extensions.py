from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_login import LoginManager
from datetime import timedelta


db = SQLAlchemy()

mail = Mail()


socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="eventlet"
)


login_manager = LoginManager()


login_manager.login_view = "auth.login"

login_manager.login_message = "Please login to continue."


# Keep authenticated sessions alive
login_manager.remember_cookie_duration = timedelta(days=30)