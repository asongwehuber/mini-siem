

#Remove all functions which print OTP before deployment.
#Those functions were put so accounts can be accessed even without internet


from app.auth.utils import create_otp
from app.database.otp import OTP
from datetime import datetime
from app.auth.utils import verify_otp
from app.auth.utils import verify_otp as verify_otp_code
from app.notifications.email_alert import send_otp_email
from app.auth.trusted_device_utils import (
    register_trusted_device,
    is_trusted_device,
    update_last_used,
    cleanup_expired_devices
)

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app.auth import auth_bp
from app.auth.decorators import (
    super_admin_required,
    admin_required
)
from app.database.models import Admin
from app.extensions import db
from app.database.trusted_device import TrustedDevice


# ======================================
# LOGIN
# ======================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    cleanup_expired_devices()

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = Admin.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))
        if not user.is_active:
            flash("This administrator account has been disabled.", "danger")
            return redirect(url_for("auth.login"))
        # Device already trusted?

        if is_trusted_device(user):

            login_user(
                user,
                remember=True
            )

            session.permanent = True

            user.last_login = datetime.utcnow()
            user.last_activity = datetime.utcnow()

            db.session.commit()

            update_last_used(user)

            flash(
                "Welcome back. Trusted device recognized.",
                "success"
            )

            return redirect(
                url_for("log_bp.dashboard")
            )


        # Save login session
        session["login_admin_id"] = user.id

        session["trust_device"] = (
            request.form.get("trust_device") == "yes"
        )


        otp = create_otp(
            user,
            purpose="login"
        )

        # Development only - print OTP to the server console
        print("\n" + "=" * 60)
        print(f"[LOGIN OTP] User : {user.email}")
        print(f"[LOGIN OTP] OTP  : {otp.otp_code}")
        print("=" * 60 + "\n")

        session["login_otp_last_sent"] = datetime.utcnow().timestamp()

        try:
            send_otp_email(
                user,
                otp.otp_code
            )
        except Exception as e:
            flash(
                "unable to send verification email.",
                "danger"
                )

    

        flash(
            "A verification code has been sent to your email.",
            "success"
        )

        return redirect(
            url_for("auth.verify_login_otp")
        )

    return render_template("login.html")


# ======================================
# VERIFY LOGIN OTP
# ======================================

@auth_bp.route("/verify-login-otp", methods=["GET", "POST"])
def verify_login_otp():

    admin_id = session.get("login_admin_id")

    if not admin_id:

        flash(
            "Your login session has expired.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    admin = Admin.query.get(admin_id)

    if not admin:

        flash(
            "Administrator not found.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        code = request.form.get("otp")

        if verify_otp_code(
            admin,
            code,
            purpose="login"
        ):

            login_user(
                admin,
                remember=True
            )

            session.permanent = True

            admin.last_login = datetime.utcnow()
            admin.last_activity = datetime.utcnow()

            db.session.commit()


            if session.get("trust_device"):

                return redirect(
                    url_for("auth.trust_device")
                )


            session.pop("login_admin_id", None)
            session.pop("trust_device", None)
            session.pop("login_otp_last_sent", None)


            flash(
                "Login successful.",
                "success"
            )


            return redirect(
                url_for("log_bp.dashboard")
            )
        
        flash(
            "Invalid or expired verification code.",
            "danger"
        )

    return render_template(
        "verify_login_otp.html"
    )


# ======================================
# RESEND LOGIN OTP
# ======================================

@auth_bp.route("/resend-login-otp")
def resend_login_otp():

    admin_id = session.get("login_admin_id")
    last_sent = session.get("login_otp_last_sent")

    if not admin_id:

        flash(
            "Your login session has expired.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    if last_sent:

        elapsed = datetime.utcnow().timestamp() - last_sent

        if elapsed < 60:

            remaining = int(60 - elapsed)

            flash(
                f"Please wait {remaining} seconds before requesting another code.",
                "warning"
            )

            return redirect(
                url_for("auth.verify_login_otp")
            )

    admin = Admin.query.get(admin_id)

    if not admin:

        flash(
            "Administrator not found.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    otp = create_otp(
        admin,
        purpose="login"
    )
    print("\n" + "=" * 60)
    print(f"[LOGIN OTP - RESEND] User : {admin.email}")
    print(f"[LOGIN OTP - RESEND] OTP  : {otp.otp_code}")
    print("=" * 60 + "\n")

    session["login_otp_last_sent"] = datetime.utcnow().timestamp()

    try:

        send_otp_email(
            admin,
            otp.otp_code
        )

    except Exception as e:

        print(e)

        flash(
            "Unable to send verification email.",
            "danger"
        )

        return redirect(
            url_for("auth.verify_login_otp")
        )

    flash(
        "A new verification code has been sent to your mail.",
        "success"
    )

    return redirect(
        url_for("auth.verify_login_otp")
    )


# ======================================
# FORGOT PASSWORD
# ======================================

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")

        admin = Admin.query.filter_by(
            email=email
        ).first()

        if not admin:

            flash(
                "No administrator account found.",
                "danger"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        otp = create_otp(admin)

        print("\n" + "=" * 60)
        print(f"[RESET OTP] User : {admin.email}")
        print(f"[RESET OTP] OTP  : {otp.otp_code}")
        print("=" * 60 + "\n")

        session["reset_admin_id"] = admin.id
        session["otp_last_sent"] = datetime.utcnow().timestamp()

        try:

            send_otp_email(
                admin,
                otp.otp_code
            )

        except Exception as e:

            print(f"[OTP EMAIL ERROR] {e}")

            flash(
                "Unable to send OTP email.",
                "danger"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        flash(
            "An OTP has been generated.",
            "success"
        )

        return redirect(
            url_for("auth.verify_otp")
        )

    return render_template(
        "forgot_password.html"
    )
# ======================================
# VERIFY OTP
# ======================================

@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    admin_id = session.get("reset_admin_id")

    if not admin_id:

        flash(
            "Password reset session has expired.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    admin = Admin.query.get(admin_id)

    if not admin:

        flash(
            "Administrator not found.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    if request.method == "POST":

        code = request.form.get("otp")

        if verify_otp_code(admin, code):

            session["otp_verified"] = True

            flash(
                "OTP verified successfully.",
                "success"
            )

            return redirect(
                url_for("auth.reset_password")
            )

        flash(
            "Invalid or expired OTP.",
            "danger"
        )

    return render_template(
        "verify_otp.html"
    )

# ======================================
# RESEND OTP
# ======================================

@auth_bp.route("/resend-otp")
def resend_otp():

    admin_id = session.get("reset_admin_id")
    last_sent = session.get("otp_last_sent")

    if last_sent:

        elapsed = datetime.utcnow().timestamp() - last_sent

        if elapsed < 60:

            remaining = int(60 - elapsed)

            flash(
                f"Please wait {remaining} seconds before requesting another OTP.",
                "warning"
            )

            return redirect(
                url_for("auth.verify_otp")
            )

    if not admin_id:

        flash(
            "Password reset session has expired.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    admin = Admin.query.get(admin_id)

    if not admin:

        flash(
            "Administrator not found.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    otp = create_otp(admin)

    print("\n" + "=" * 60)
    print(f"[RESET OTP - RESEND] User : {admin.email}")
    print(f"[RESET OTP - RESEND] OTP  : {otp.otp_code}")
    print("=" * 60 + "\n")

    session["otp_last_sent"] = datetime.utcnow().timestamp()

    try:

        send_otp_email(
            admin,
            otp.otp_code
        )

    except Exception:

        flash(
            "Unable to send OTP email.",
            "danger"
        )
    

        return redirect(
            url_for("auth.verify_otp")
        )

    flash(
        "A new OTP has been sent.",
        "success"
    )

    return redirect(
        url_for("auth.verify_otp")
    )


# ======================================
# TRUST DEVICE
# ======================================

@auth_bp.route("/trust-device", methods=["GET", "POST"])
def trust_device():

    admin_id = session.get("login_admin_id")


    if not admin_id:

        flash(
            "Session expired.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    admin = Admin.query.get(admin_id)


    if not admin:

        flash(
            "Administrator not found.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )
    
    # ======================================
    # CHECK IF DEVICE IS ALREADY TRUSTED
    # ======================================

    if is_trusted_device(admin):

        update_last_used(admin)

        login_user(
            admin,
            remember=True
        )

        session.pop("trust_device", None)
        session.pop("login_admin_id", None)
        session.pop("login_otp_last_sent", None)

        flash(
            "This device is already trusted.",
            "info"
        )

        return redirect(
            url_for("log_bp.dashboard")
        )


    # ======================================
    # REGISTER NEW TRUSTED DEVICE
    # ======================================

    if request.method == "POST":

        duration = request.form.get("duration")


        if duration == "forever":

            days = None

        else:

            days = int(duration)


        register_trusted_device(
            admin,
            days
        )


        session.pop("trust_device", None)
        session.pop("login_admin_id", None)
        session.pop("login_otp_last_sent", None)


        login_user(
            admin,
            remember=True
        )


        flash(
            "This device has been trusted successfully.",
            "success"
        )


        return redirect(
            url_for("log_bp.dashboard")
        )


    return render_template(
        "trust_device.html"
    )


# ======================================
# RESET PASSWORD
# ======================================

@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    admin_id = session.get("reset_admin_id")

    otp_verified = session.get("otp_verified")

    if not admin_id or not otp_verified:

        flash(
            "Unauthorized password reset.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    admin = Admin.query.get(admin_id)

    if not admin:

        flash(
            "Administrator not found.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        password = request.form.get("password")

        confirm = request.form.get("confirm_password")

        if password != confirm:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("auth.reset_password")
            )

        admin.set_password(password)

        db.session.commit()

        session.pop("reset_admin_id", None)
        session.pop("otp_verified", None)
        session.pop("otp_started", None)
        session.pop("otp_last_sent", None)

        flash(
            "Password reset successfully.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "reset_password.html"
    )


# ======================================
# LOGOUT
# ======================================

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()
    session.clear()

    return redirect(url_for("auth.login"))


# ======================================
# ADMINISTRATOR MANAGEMENT
# ======================================

@auth_bp.route("/admin")
@login_required
def admin_dashboard():

    if current_user.role != "super_admin":
        flash("Access denied.", "danger")
        return redirect(url_for("log_bp.dashboard"))

    admins = Admin.query.order_by(Admin.id.asc()).all()

    return render_template(
        "admin/list_admins.html",
        admins=admins
    )


# ======================================
# CREATE ADMINISTRATOR
# ======================================

@auth_bp.route("/admin/create", methods=["GET", "POST"])
@login_required
@super_admin_required
def create_admin():

    if request.method == "POST":

        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.create_admin"))

        existing_admin = Admin.query.filter_by(email=email).first()

        if existing_admin:
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.create_admin"))

        new_admin = Admin(
            fullname=fullname,
            email=email,
            role=role
        )

        new_admin.set_password(password)

        db.session.add(new_admin)
        db.session.commit()

        flash("Administrator created successfully.", "success")

        return redirect(url_for("auth.admin_dashboard"))

    return render_template(
        "admin/create_admin.html"
    )

# ======================================
# EDIT ADMINISTRATOR
# ======================================

@auth_bp.route("/admin/edit/<int:admin_id>", methods=["GET", "POST"])
@login_required
@super_admin_required
def edit_admin(admin_id):

    admin = Admin.query.get_or_404(admin_id)

    if request.method == "POST":

        admin.fullname = request.form.get("fullname")
        admin.email = request.form.get("email")
        admin.role = request.form.get("role")

        db.session.commit()

        flash("Administrator updated successfully.", "success")

        return redirect(url_for("auth.admin_dashboard"))

    return render_template(
        "admin/edit_admin.html",
        admin=admin
    )

# ======================================
# ENABLE / DISABLE ADMINISTRATOR
# ======================================

@auth_bp.route("/admin/toggle/<int:admin_id>")
@login_required
@super_admin_required
def toggle_admin(admin_id):

    admin = Admin.query.get_or_404(admin_id)

    # Prevent disabling yourself
    if admin.id == current_user.id:
        flash("You cannot disable your own account.", "danger")
        return redirect(url_for("auth.admin_dashboard"))

    admin.is_active = not admin.is_active

    db.session.commit()

    if admin.is_active:
        flash("Administrator enabled successfully.", "success")
    else:
        flash("Administrator disabled successfully.", "warning")

    return redirect(url_for("auth.admin_dashboard"))

# ======================================
# CHANGE ADMINISTRATOR PASSWORD
# ======================================

@auth_bp.route("/admin/change-password/<int:admin_id>", methods=["GET", "POST"])
@login_required
@super_admin_required
def change_admin_password(admin_id):

    admin = Admin.query.get_or_404(admin_id)

    if request.method == "POST":

        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")


        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for(
                    "auth.change_admin_password",
                    admin_id=admin.id
                )
            )


        admin.set_password(password)

        db.session.commit()


        flash(
            "Administrator password changed successfully.",
            "success"
        )


        return redirect(
            url_for("auth.admin_dashboard")
        )


    return render_template(
        "admin/change_password.html",
        admin=admin
    )


# =========================
# TRUSTED DEVICE MANAGEMENT
# =========================

@auth_bp.route("/trusted-devices")
@login_required
def trusted_devices():

    devices = TrustedDevice.query.filter_by(
        admin_id=current_user.id
    ).order_by(
        TrustedDevice.last_used.desc()
    ).all()

    return render_template(
        "trusted_devices.html",
        devices=devices
    )

@auth_bp.route(
    "/trusted-device/revoke/<int:id>",
    methods=["POST"]
)
@login_required
def revoke_trusted_device(id):

    device = TrustedDevice.query.filter_by(
        id=id,
        admin_id=current_user.id
    ).first()

    if not device:
        flash(
            "Trusted device not found.",
            "danger"
        )
        return redirect(
            url_for("auth.trusted_devices")
        )


    device.is_active = False

    db.session.commit()


    flash(
        "Trusted device revoked successfully.",
        "success"
    )


    return redirect(
        url_for("auth.trusted_devices")
    )


# =========================
# SUPER ADMIN TRUSTED DEVICE MANAGEMENT
# =========================

@auth_bp.route("/admin/trusted-devices")
@login_required
@super_admin_required
def admin_trusted_devices():

    devices = TrustedDevice.query.order_by(
        TrustedDevice.last_used.desc()
    ).all()


    return render_template(
        "admin/trusted_device_management.html",
        devices=devices
    )



@auth_bp.route(
    "/admin/trusted-device/revoke/<int:id>",
    methods=["POST"]
)
@login_required
@super_admin_required
def admin_revoke_trusted_device(id):

    device = TrustedDevice.query.get_or_404(id)


    device.is_active = False

    db.session.commit()


    flash(
        "Trusted device revoked successfully.",
        "success"
    )


    return redirect(
        url_for("auth.admin_trusted_devices")
    )