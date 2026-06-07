from app.extensions import db
from app.database.models import QuarantinedHost


def quarantine_host(ip, hostname, reason):

    existing = QuarantinedHost.query.filter_by(
        source_ip=ip
    ).first()

    if existing:
        return False

    host = QuarantinedHost(
        source_ip=ip,
        hostname=hostname,
        reason=reason
        
    )

    db.session.add(host)
    db.session.commit()

    print(f"[QUARANTINE] Host {ip} quarantined")

    return {
        "id": host.id,
        "ip_address": host.source_ip,
        "hostname": host.hostname,
        "reason": host.reason,
        "timestamp": host.quarantined_at
    }