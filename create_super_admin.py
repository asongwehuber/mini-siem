from app.main import create_app
from app.extensions import db
from app.database.models import Admin

app = create_app()

with app.app_context():

    email = "admin@siem.local"

    admin = Admin.query.filter_by(email=email).first()

    if admin:
        print("Super Admin already exists.")

    else:
        admin = Admin(
            fullname="Super Administrator",
            email=email,
            role="super_admin",
            is_active=True,
            otp_enabled=False
        )

        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        print("Super Admin created successfully.")