def format_quarantine(host):
    return {
        "id": host.id,
        "ip_address": host.source_ip,
        "hostname": host.hostname,
        "reason": host.reason,
        "timestamp": host.quarantined_at
    }