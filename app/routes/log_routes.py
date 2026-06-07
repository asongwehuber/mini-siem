from flask import Blueprint, request, jsonify, render_template
from zoneinfo import ZoneInfo
from flask_mail import Message
from app.extensions import db, mail
from app.database.models import Log, Alert, QuarantinedHost
from app.response.quarantine import quarantine_host

from app.detection.detection_engine import (
    detect_brute_force,
    detect_port_scan,
    detect_high_severity_incident
)

# =========================================
# BLUEPRINT
# =========================================
log_bp = Blueprint('log_bp', __name__)


# =========================================
# TIME FORMAT HELPER
# =========================================
def format_time(dt):

    if not dt:
        return None

    return dt.replace(
        tzinfo=ZoneInfo("UTC")
    ).astimezone(
        ZoneInfo("Africa/Douala")
    ).strftime("%Y-%m-%d %H:%M:%S")


# =========================================
# DASHBOARD HOME
# =========================================
@log_bp.route('/')
def dashboard():

    return render_template('dashboard.html')




# =========================================
# SUBMIT LOG
# =========================================
@log_bp.route('/submit-log', methods=['POST'])
def submit_log():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Invalid JSON body"
            }), 400

        required_fields = [
            'source_ip',
            'hostname',
            'event_type',
            'severity',
            'message',
            'destination_port'
        ]

        for field in required_fields:

            if field not in data:

                return jsonify({
                    "error": f"Missing field: {field}"
                }), 400

        # =========================================
        # CREATE LOG
        # =========================================
        new_log = Log(
            source_ip=data['source_ip'],
            hostname=data['hostname'],
            event_type=data['event_type'].strip().lower(),
            severity=data['severity'].strip().lower(),
            destination_port=data['destination_port'],
            message=data['message'],
            raw_log=str(data)
        )

        db.session.add(new_log)
        db.session.commit()

        # DEBUG: confirm log ingestion
        print("[LOG RECEIVED]", new_log.event_type, new_log.severity)

        # =========================================
        # RUN DETECTIONS
        # =========================================
        suspicious_events = [
            'failed_login',
            'port_scan',
            'malware_activity',
            'brute_force'
        ]

        if (
            new_log.event_type in suspicious_events
            or new_log.severity.lower() in ['high', 'critical']
        ):

            detect_brute_force(new_log.source_ip)

            detect_port_scan(new_log.source_ip)

            detect_high_severity_incident(
                new_log.source_ip,
                new_log.hostname
            )

        return jsonify({
            "message": "Log received successfully",
            "source_ip": new_log.source_ip
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET ALL LOGS
# =========================================
@log_bp.route('/logs', methods=['GET'])
def get_logs():

    try:

        logs = Log.query.order_by(
            Log.timestamp.desc()
        ).all()

        return jsonify([

            {
                "id": log.id,
                "timestamp": format_time(log.timestamp),
                "source_ip": log.source_ip,
                "hostname": log.hostname,
                "event_type": log.event_type,
                "severity": log.severity,
                "destination_port": log.destination_port,
                "message": log.message
                
            }

            for log in logs

        ]), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET SINGLE LOG
# =========================================
@log_bp.route('/log/<int:log_id>', methods=['GET'])
def get_single_log(log_id):

    try:

        log = Log.query.get(log_id)

        if not log:

            return jsonify({
                "error": "Log not found"
            }), 404

        return jsonify({
            "id": log.id,
            "timestamp": format_time(log.timestamp),
            "source_ip": log.source_ip,
            "hostname": log.hostname,
            "event_type": log.event_type,
            "severity": log.severity,
            "destination_port": log.destination_port,
            "message": log.message,
            "raw_log": log.raw_log
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET ALERTS
# =========================================
@log_bp.route('/alerts', methods=['GET'])
def get_alerts():

    try:

        alerts = Alert.query.order_by(
            Alert.timestamp.desc()
        ).all()

        return jsonify([

            {
                "id": alert.id,
                "alert_name": alert.alert_name,
                "description": alert.description,
                "severity": alert.severity,
                "source_ip": alert.source_ip,
                "event_count": alert.event_count,
                "status": alert.status,
                "timestamp": format_time(alert.timestamp)
            }

            for alert in alerts

        ]), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# RESOLVE ALERT
# =========================================
@log_bp.route(
    '/resolve-alert/<int:alert_id>',
    methods=['POST']
)
def resolve_alert(alert_id):

    try:

        alert = Alert.query.get(alert_id)

        if not alert:

            return jsonify({
                "error": "Alert not found"
            }), 404

        alert.status = "RESOLVED"

        db.session.commit()

        return jsonify({
            "message": "Alert resolved successfully"
        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# SEARCH LOGS
# =========================================
@log_bp.route('/search', methods=['GET'])
def search_logs():

    try:

        source_ip = request.args.get('source_ip')
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')

        query = Log.query

        if source_ip:
            query = query.filter_by(
                source_ip=source_ip
            )

        if event_type:
            query = query.filter_by(
                event_type=event_type
            )

        if severity:
            query = query.filter_by(
                severity=severity
            )

        logs = query.order_by(
            Log.timestamp.desc()
        ).all()

        return jsonify([

            {
                "id": log.id,
                "timestamp": format_time(log.timestamp),
                "source_ip": log.source_ip,
                "hostname": log.hostname,
                "event_type": log.event_type,
                "severity": log.severity,
                "destination_port": log.destination_port,
                "message": log.message
            }

            for log in logs

        ]), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# TOP ATTACKERS
# =========================================
@log_bp.route('/top-attackers', methods=['GET'])
def top_attackers():

    try:

        from sqlalchemy import func

        results = db.session.query(
            Log.source_ip,
            func.count(Log.id).label('count')
        ).group_by(
            Log.source_ip
        ).order_by(
            func.count(Log.id).desc()
        ).limit(5).all()

        attackers = []

        for ip, count in results:

            attackers.append({
                "source_ip": ip,
                "count": count
            })

        return jsonify(attackers), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
    

#test route


@log_bp.route('/test-email')
def test_email():

    try:

        msg = Message(
            subject="Mini SIEM Test Email",
            recipients=["huber.asongwe@gmail.com"], 
            body="This is a test email from Mini SIEM system."
        )

        mail.send(msg)

        return jsonify({
            "message": "Email sent successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
    

@log_bp.route('/quarantined-hosts', methods=['GET'])
def get_quarantined_hosts():

    hosts = QuarantinedHost.query.filter_by(
        status='quarantined'
    ).order_by(
        QuarantinedHost.quarantined_at.desc()
    ).all()

    total_hosts = len(hosts)

    return jsonify({
        "total_quarantined": total_hosts,
        "hosts": [
            {
                "id": host.id,
                "source_ip": host.source_ip,
                "hostname": host.hostname,
                "reason": host.reason,
                "status": host.status,
                "quarantined_at": format_time(
                    host.quarantined_at
                )
            }
            for host in hosts
        ]
    })


@log_bp.route('/test-quarantine')
def test_quarantine():

    quarantine_host(
        ip="10.10.10.5",
        hostname="TEST-PC",
        reason="Manual Test"
    )

    return jsonify({
        "message": "Host quarantined"
    })

@log_bp.route(
    '/release-host/<int:host_id>',
    methods=['POST']
)
def release_host(host_id):

    try:

        host = QuarantinedHost.query.get(host_id)

        if not host:

            return jsonify({
                "error": "Host not found"
            }), 404

        host.status = "released"

        db.session.commit()

        return jsonify({
            "message": "Host released successfully"
        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500
    



@log_bp.route('/quarantined-hosts-summary')
def get_quarantined_hosts_summary():

    total_hosts = QuarantinedHost.query.filter_by(
        status='quarantined'
    ).count()

    hosts = QuarantinedHost.query.filter_by(
        status='quarantined'
    ).order_by(
        QuarantinedHost.quarantined_at.desc()
    ).limit(3).all()

    return jsonify({
        "total_quarantined": total_hosts,
        "hosts": [
            {
                "id": host.id,
                "source_ip": host.source_ip,
                "hostname": host.hostname,
                "reason": host.reason,
                "status": host.status,
                "quarantined_at": format_time(
                    host.quarantined_at
                )
            }
            for host in hosts
        ]
    })