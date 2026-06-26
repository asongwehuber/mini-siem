from app.main import create_app
from app.extensions import db
from app.attack_map.geolocation import init_geoip

app = create_app()

# -----------------------------
# SYSTEM INITIALIZATION
# -----------------------------

print("\n===== SIEM SYSTEM STARTING =====")

# Initialize GeoIP database
init_geoip()
print("[OK] GeoIP service initialized")

# Print routes (debug mode)
print("\n===== REGISTERED ROUTES =====")
print(app.url_map)
print("=============================\n")

# -----------------------------
# DB INIT (optional but recommended)
# -----------------------------
with app.app_context():
    db.create_all()
    print("[OK] Database initialized")

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    print("[OK] SIEM running on http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)