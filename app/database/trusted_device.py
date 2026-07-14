from datetime import datetime

from app.extensions import db


class TrustedDevice(db.Model):
    __tablename__ = "trusted_devices"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admins.id"),
        nullable=False
    )

    device_name = db.Column(
        db.String(255),
        nullable=False
    )

    device_hash = db.Column(
        db.String(255),
        nullable=False
    )

    ip_address = db.Column(
        db.String(45),
        nullable=False
    )

    browser = db.Column(
        db.String(120)
    )

    operating_system = db.Column(
        db.String(120)
    )

    trusted_until = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    last_used = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    __table_args__ = (
    db.UniqueConstraint(
        "admin_id",
        "device_hash",
        name="uq_admin_device"
    ),
)