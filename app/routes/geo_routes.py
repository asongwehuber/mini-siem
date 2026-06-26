from flask import Blueprint, jsonify, request
from app.attack_map.geolocation import locate_ip

geo_bp = Blueprint("geo", __name__)

@geo_bp.route("/geoip")
def geoip_lookup():
    ip = request.args.get("ip")

    if not ip:
        return jsonify({"error": "IP required"}), 400

    return jsonify(locate_ip(ip))