from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from zoneinfo import ZoneInfo
from flask_mail import Message
from app.extensions import db, mail
from app.database.models import Log, Alert, QuarantinedHost
from app.response.quarantine import quarantine_host
from flask_login import login_required, current_user
from app.database.trusted_device import TrustedDevice
from app.utils.time_filters import get_time_range
from datetime import datetime


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
    ).strftime("%d-%m-%y %H:%M:%S")




# =========================================
# HOME
# =========================================
@log_bp.route('/')
def home():

    # Already logged in
    if current_user.is_authenticated:
        return redirect(url_for('log_bp.dashboard'))

    # Not logged in
    return redirect(url_for('auth.login'))

# =========================================
# dashboard
# =========================================
@log_bp.route('/dashboard')
@login_required
def dashboard():

    trusted_count = TrustedDevice.query.filter_by(
        admin_id=current_user.id,
        is_active=True
    ).count()

    return render_template(
        'dashboard.html',
        trusted_count=trusted_count
    )



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
# GET ALL LOGS (PAGINATED)
# =========================================
@log_bp.route('/logs', methods=['GET'])
@login_required
def get_logs():

    try:

        page = request.args.get(
            "page",
            1,
            type=int
        )

        per_page = 50


        pagination = Log.query.order_by(
            Log.timestamp.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


        logs = pagination.items


        return jsonify({

            "logs": [

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

            ],

            "page": pagination.page,

            "pages": pagination.pages,

            "total": pagination.total

        }), 200


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# GET SINGLE LOG
# =========================================
@log_bp.route('/log/<int:log_id>', methods=['GET'])
@login_required
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
@login_required
def get_alerts():

    try:

        page = request.args.get(
            "page",
            1,
            type=int
        )

        per_page = 50


        pagination = Alert.query.order_by(
            Alert.timestamp.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


        alerts = pagination.items


        return jsonify({

            "alerts": [

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

            ],

            "page": pagination.page,

            "pages": pagination.pages,

            "total": pagination.total

        }), 200


    except Exception as e:


        return jsonify({
            "error": str(e)
        }), 500



# =========================================
# GET SINGLE ALERT
# =========================================

@log_bp.route('/alert/<int:alert_id>', methods=['GET'])
@login_required
def get_single_alert(alert_id):

    try:

        alert = Alert.query.get(alert_id)

        if not alert:

            return jsonify({

                "error": "Alert not found"

            }), 404


        return jsonify({

            "id": alert.id,

            "alert_name": alert.alert_name,

            "description": alert.description,

            "severity": alert.severity,

            "source_ip": alert.source_ip,

            "event_count": alert.event_count,

            "status": alert.status,

            "timestamp": format_time(
                alert.timestamp
            )

        }), 200


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
@login_required
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
@login_required
def search_logs():

    try:

        source_ip = request.args.get('source_ip')
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        period = request.args.get('period')

        start_time = request.args.get('start_time')

        end_time = request.args.get('end_time')


        page = request.args.get(
            "page",
            1,
            type=int
        )

        per_page = 50

        query = Log.query

        # Quick time filters


        # predefined periods
        if period and period != "custom":

            start, end = get_time_range(period)

            if start and end:

                query = query.filter(
                    Log.timestamp >= start,
                    Log.timestamp <= end
                )


        # custom date range
        if period == "custom" and start_time and end_time:

            start = datetime.fromisoformat(
                start_time
            )

            end = datetime.fromisoformat(
                end_time
            )


            query = query.filter(
                Log.timestamp >= start,
                Log.timestamp <= end
            )


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


        pagination = query.order_by(
            Log.timestamp.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


        logs = pagination.items


        return jsonify({

            "logs": [

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

            ],

            "page": pagination.page,

            "pages": pagination.pages,

            ""
            ""
            "total": pagination.total

        }), 200


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================
# SEARCH ALERTS
# =========================================

@log_bp.route('/alerts/search', methods=['GET'])
@login_required
def search_alerts():

    try:

        source_ip = request.args.get("source_ip")

        severity = request.args.get("severity")

        status = request.args.get("status")

        period = request.args.get("period")

        start_time = request.args.get("start_time")

        end_time = request.args.get("end_time")

        page = request.args.get(
            "page",
            1,
            type=int
        )

        per_page = 50

        query = Alert.query

        if period:

            start, end = get_time_range(period)

            if start:

                query = query.filter(
                    Alert.timestamp >= start,
                    Alert.timestamp <= end
                )


        if start_time and end_time:

            start = datetime.fromisoformat(
                start_time
            )

            end = datetime.fromisoformat(
                end_time
            )


            query = query.filter(
                Alert.timestamp >= start,
                Alert.timestamp <= end
            )



        if source_ip:

            query = query.filter_by(
                source_ip=source_ip
            )


        if severity:

            query = query.filter_by(
                severity=severity
            )


        if status:

            query = query.filter_by(
                status=status
            )


        pagination = query.order_by(

            Alert.timestamp.desc()

        ).paginate(

            page=page,

            per_page=per_page,

            error_out=False

        )


        alerts = pagination.items


        return jsonify({

            "alerts":[

                {

                    "id": alert.id,

                    "alert_name": alert.alert_name,

                    "description": alert.description,

                    "severity": alert.severity,

                    "source_ip": alert.source_ip,

                    "event_count": alert.event_count,

                    "status": alert.status,

                    "timestamp": format_time(
                        alert.timestamp
                    )

                }

                for alert in alerts

            ],

            "page": pagination.page,

            "pages": pagination.pages,

            "total": pagination.total

        })


    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500


# =========================================
# TOP ATTACKERS
# =========================================
@log_bp.route('/top-attackers', methods=['GET'])
@login_required
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
@login_required
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
    

# =========================================
# GET QUARANTINED HOSTS (PAGINATED)
# =========================================
@log_bp.route('/quarantined-hosts', methods=['GET'])
@login_required
def get_quarantined_hosts():

    try:

        page = request.args.get(
            "page",
            1,
            type=int
        )

        per_page = 50



        query = QuarantinedHost.query.filter_by(
            status='quarantined'
        )


        period = request.args.get("period")

        start_time = request.args.get("start_time")

        end_time = request.args.get("end_time")


        if period:

            start, end = get_time_range(period)


            if start:

                query = query.filter(
                    QuarantinedHost.quarantined_at >= start,
                    QuarantinedHost.quarantined_at <= end
                )


        if period == "custom" and start_time and end_time:


            start = datetime.fromisoformat(
                start_time
            )


            end = datetime.fromisoformat(
                end_time
            )


            query = query.filter(
                QuarantinedHost.quarantined_at >= start,
                QuarantinedHost.quarantined_at <= end
            )



        pagination = query.order_by(
            QuarantinedHost.quarantined_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


        hosts = pagination.items


        return jsonify({

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

            ],

            "page": pagination.page,

            "pages": pagination.pages,

            "total": pagination.total

        }), 200


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

@log_bp.route('/test-quarantine')
@login_required
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
@login_required
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
@login_required
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
# =========================================
# LOGS EXPLORER PAGE
# =========================================
@log_bp.route('/logs/explorer')
@login_required
def logs_explorer():

    return render_template(
        'logs/explorer.html',
        trusted_count=TrustedDevice.query.filter_by(
            admin_id=current_user.id,
            is_active=True
        ).count()
    )


# =========================================
# ALERTS MANAGEMENT PAGE
# =========================================

@log_bp.route('/alerts/management')
@login_required
def alerts_management():

    trusted_count = TrustedDevice.query.filter_by(
        admin_id=current_user.id,
        is_active=True
    ).count()


    return render_template(
        'alerts/management.html',
        trusted_count=trusted_count
    )



# =========================================
# QUARANTINE HOSTS PAGE
# =========================================

@log_bp.route('/quarantine/hosts')
@login_required
def quarantine_hosts_page():

    trusted_count = TrustedDevice.query.filter_by(
        admin_id=current_user.id,
        is_active=True
    ).count()


    return render_template(
        'quarantine/hosts.html',
        trusted_count=trusted_count
    )