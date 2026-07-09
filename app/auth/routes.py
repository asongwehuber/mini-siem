from datetime import datetime

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


# ======================================
# LOGIN
# ======================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

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

        login_user(user, remember=False)

        session.permanent = True

        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()

        db.session.commit()

        print("LOGIN SUCCESS - USER LOGGED IN:", user.email)

        return redirect(url_for("log_bp.dashboard"))

    return render_template("login.html")


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