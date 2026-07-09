from functools import wraps
from flask import abort
from flask_login import current_user


# ==========================================
# SUPER ADMIN ONLY
# ==========================================
def super_admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            abort(401)

        if current_user.role != "super_admin":
            abort(403)

        return func(*args, **kwargs)

    return wrapper


# ==========================================
# ADMIN OR SUPER ADMIN
# ==========================================
def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            abort(401)

        if current_user.role not in ["admin", "super_admin"]:
            abort(403)

        return func(*args, **kwargs)

    return wrapper