from datetime import datetime, timedelta
import secrets
import string

from app.extensions import db
from app.database.otp import OTP


def generate_otp(length=6):
    """
    Generates a cryptographically secure numeric OTP.
    """

    digits = string.digits

    return "".join(
        secrets.choice(digits)
        for _ in range(length)
    )


def create_otp(admin, purpose="password_reset", expiry_minutes=10):
    """
    Creates and stores a new OTP.
    """

    # Expire all previous unused OTPs
    OTP.query.filter_by(
        admin_id=admin.id,
        purpose=purpose,
        is_used=False
    ).update(
        {"is_used": True}
    )

    otp_code = generate_otp()

    otp = OTP(
        admin_id=admin.id,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
    )

    db.session.add(otp)
    db.session.commit()

    return otp


def verify_otp(admin, code, purpose="password_reset"):
    """
    Verifies an OTP.
    """

    otp = OTP.query.filter_by(
        admin_id=admin.id,
        purpose=purpose,
        is_used=False
    ).order_by(
        OTP.created_at.desc()
    ).first()

    if not otp:
        return False

    if datetime.utcnow() > otp.expires_at:
        return False

    if otp.otp_code != code:
        otp.attempts += 1
        if otp.attempts >=5:
            otp.is_used = True
        db.session.commit()
        return False
    
    if otp.attempts >= 5:

        otp.is_used = True

        db.session.commit()

        return False

    otp.is_used = True
    db.session.commit()

    return True