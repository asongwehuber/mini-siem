from datetime import datetime
from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# =========================
# ADMIN MODEL (ONLY ONE)
# =========================
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="admin")

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    last_login = db.Column(db.DateTime)

    failed_attempts = db.Column(db.Integer, default=0)

    locked_until = db.Column(db.DateTime)

    otp_enabled = db.Column(db.Boolean, default=True)

    last_activity = db.Column(
        db.DateTime,
        nullable=True
    )
    trusted_devices = db.relationship(
        "TrustedDevice",
        backref="admin",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


# =========================
# LOG MODEL
# =========================
class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source_ip = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(100))
    event_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(50))
    destination_port = db.Column(db.Integer)
    message = db.Column(db.Text)
    raw_log = db.Column(db.Text)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)
    event_category = db.Column(db.String(50), default="system")


# =========================
# ALERT MODEL
# =========================
class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    alert_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(50), nullable=False)
    source_ip = db.Column(db.String(100), nullable=False)
    event_count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='OPEN')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# QUARANTINED HOST
# =========================
class QuarantinedHost(db.Model):
    __tablename__ = 'quarantined_hosts'
    id = db.Column(db.Integer, primary_key=True)
    source_ip = db.Column(db.String(50), nullable=False)
    hostname = db.Column(db.String(100))
    reason = db.Column(db.String(255))
    quarantined_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='quarantined')
    released_at = db.Column(db.DateTime, nullable=True)


# =========================
# ATTACK LOCATION
# =========================
class AttackLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    source_ip = db.Column(db.String(50))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    attack_type = db.Column(db.String(100))
    severity = db.Column(db.String(20))


# =========================
# USER LOADER (ONLY ONE)
# =========================
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

from app.database.trusted_device import TrustedDevice