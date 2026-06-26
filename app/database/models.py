from datetime import datetime
from app.extensions import db


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

    def __repr__(self):
        return f"<Log {self.event_type}>"


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

    def __repr__(self):
        return f"<Alert {self.alert_name}>"


# =========================
# QUARANTINED HOST MODEL
# =========================
class QuarantinedHost(db.Model):
    __tablename__ = 'quarantined_hosts'

    id = db.Column(db.Integer, primary_key=True)

    source_ip = db.Column(db.String(50), nullable=False)

    hostname = db.Column(db.String(100))

    reason = db.Column(db.String(255))

    quarantined_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default='quarantined'
    )

    released_at = db.Column(
        db.DateTime,
        nullable=True
    )

    def __repr__(self):
        return f"<QuarantinedHost {self.source_ip}>"
    

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