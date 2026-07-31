from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.database.models import HeartbeatStatus


heartbeat_bp = Blueprint(
    "heartbeat",
    __name__
)


@heartbeat_bp.route(
    "/submit-heartbeat",
    methods=["POST"]
)
def submit_heartbeat():

    data = request.get_json()

    if not data:

        return jsonify(
            {
                "status": "error",
                "message": "No heartbeat data received."
            }
        ), 400

    generator_id = data.get("generator_id")
    hostname = data.get("hostname")

    if not generator_id or not hostname:

        return jsonify(
            {
                "status": "error",
                "message": "generator_id and hostname are required."
            }
        ), 400

    heartbeat = HeartbeatStatus.query.filter_by(
        generator_id=generator_id
    ).first()

    if heartbeat is None:

        heartbeat = HeartbeatStatus(
            generator_id=generator_id,
            hostname=hostname,
            source_type = data.get(
                "source_type",
                generator_id.split("-")[0].lower()
            ),
            status="online",
            last_heartbeat=datetime.utcnow(),
            last_log=None,
            total_logs=0
        )

        db.session.add(heartbeat)

    else:

        heartbeat.hostname = hostname
        heartbeat.source_type = data.get(
            "source_type",
            generator_id.split("-")[0].lower()
        )
        heartbeat.status = "online"
        heartbeat.last_heartbeat = datetime.utcnow()

    db.session.commit()

    return jsonify(
        {
            "status": "success",
            "generator_id": generator_id
        }
    ), 200