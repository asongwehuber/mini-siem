from datetime import datetime

from app.extensions import db


class OTP(db.Model):
    __tablename__ = "otp_codes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admins.id"),
        nullable=False
    )

    otp_code = db.Column(
        db.String(6),
        nullable=False
    )

    purpose = db.Column(
        db.String(30),
        default="password_reset"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    is_used = db.Column(
        db.Boolean,
        default=False
    )

    attempts = db.Column(
        db.Integer,
        default=0
    )

    admin = db.relationship(
        "Admin",
        backref="otp_codes"
    )