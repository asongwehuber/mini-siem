import hashlib

from datetime import datetime, timedelta

from flask import request

from app.extensions import db
from app.database.trusted_device import TrustedDevice


# ======================================
# GENERATE DEVICE HASH
# ======================================

def generate_device_hash():

    fingerprint = "|".join([
        request.headers.get("User-Agent", ""),
        request.headers.get("Accept-Language", ""),
        request.headers.get("Accept-Encoding", "")
    ])

    return hashlib.sha256(
        fingerprint.encode()
    ).hexdigest()


# ======================================
# GET DEVICE NAME
# ======================================

def get_device_name():

    return f"{get_browser()} on {get_operating_system()}"


# ======================================
# GET BROWSER
# ======================================

def get_browser():

    user_agent = request.headers.get(
        "User-Agent",
        ""
    )


    if "Firefox" in user_agent:
        return "Firefox"

    elif "Chrome" in user_agent:
        return "Chrome"

    elif "Edg" in user_agent:
        return "Edge"

    elif "Safari" in user_agent:
        return "Safari"

    else:
        return "Unknown"



# ======================================
# GET OPERATING SYSTEM
# ======================================

def get_operating_system():

    user_agent = request.headers.get(
        "User-Agent",
        ""
    )


    if "Windows" in user_agent:
        return "Windows"

    elif "Linux" in user_agent:
        return "Linux"

    elif "Macintosh" in user_agent:
        return "macOS"

    elif "Android" in user_agent:
        return "Android"

    elif "iPhone" in user_agent:
        return "iOS"

    else:
        return "Unknown"


# ======================================
# REGISTER TRUSTED DEVICE
# ======================================

def register_trusted_device(admin, days):

    device_hash = generate_device_hash()

    existing_device = TrustedDevice.query.filter_by(
        admin_id=admin.id,
        device_hash=device_hash
    ).first()


    # Device already exists
    if existing_device:

        existing_device.is_active = True

        if days is None:
            existing_device.trusted_until = None

        else:
            existing_device.trusted_until = (
                datetime.utcnow() +
                timedelta(days=days)
            )

        existing_device.last_used = datetime.utcnow()

        db.session.commit()

        return existing_device



    device = TrustedDevice(
        admin_id=admin.id,
        device_name=get_device_name(),
        device_hash=device_hash,
        ip_address=request.remote_addr,
        browser=get_browser(),
        operating_system=get_operating_system(),
        last_used=datetime.utcnow()
    )


    if days is None:

        device.trusted_until = None

    else:

        device.trusted_until = (
            datetime.utcnow() +
            timedelta(days=days)
        )


    db.session.add(device)

    db.session.commit()


    return device

# ======================================
# CHECK TRUSTED DEVICE
# ======================================

def is_trusted_device(admin):

    device_hash = generate_device_hash()


    device = TrustedDevice.query.filter_by(
        admin_id=admin.id,
        device_hash=device_hash
    ).first()


    if not device:
        return False


    if not device.is_active:
        return False


    if device.trusted_until is None:
        return True


    if device.trusted_until < datetime.utcnow():


        device.is_active = False

        db.session.commit()

        return False


    print("RESULT: Device trusted")

    return True


# ======================================
# UPDATE LAST USED
# ======================================

def update_last_used(admin):

    device = TrustedDevice.query.filter_by(
        admin_id=admin.id,
        device_hash=generate_device_hash(),
        is_active=True
    ).first()

    if device:

        device.last_used = datetime.utcnow()

        db.session.commit()


# ======================================
# REVOKE DEVICE
# ======================================

def revoke_trusted_device(device_id):

    device = TrustedDevice.query.get(device_id)

    if not device:

        return False

    device.is_active = False

    db.session.commit()

    return True

# ======================================
# CLEANUP EXPIRED DEVICES
# ======================================

def cleanup_expired_devices():

    now = datetime.utcnow()

    expired = TrustedDevice.query.filter(
        TrustedDevice.trusted_until.isnot(None),
        TrustedDevice.trusted_until < now
    ).all()

    for device in expired:

        device.is_active = False

    db.session.commit()