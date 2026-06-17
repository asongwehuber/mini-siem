
# Mini-SIEM User Guide

## 1. Introduction

The Mini-SIEM system is a Security Information and Event Management platform designed to collect logs, detect threats, generate alerts, and provide AI-assisted security analysis.

It includes:

* Log monitoring
* Alert generation
* Host quarantine
* AI security assistant
* PDF reporting dashboard



## 2. Dashboard Overview

The dashboard provides a real-time security overview of the system.

### Key metrics displayed:

* Total logs collected
* Active security alerts
* Quarantined hosts
* Attack statistics

The dashboard automatically refreshes as new logs are received.



## 3. Log Management

### View Logs

Access all collected logs at:

/logs


Each log contains:

* Source IP
* Event type
* Severity level
* Timestamp



### Submit Logs

Logs are submitted via the following endpoint:

POST /submit-log



### Example Log Simulations

## 🟢 Successful Login (Low Severity)

```bash
for i in {1..2}
do
curl -X POST http://127.0.0.1:5000/submit-log \
-H "Content-Type: application/json" \
-d '{
  "source_ip": "192.168.1.10",
  "hostname": "user-device",
  "event_type": "successful_login",
  "severity": "low",
  "destination_port": 22,
  "message": "User login successful"
}'
done


## 🟡 Failed Login Attempts (Medium Severity)

```bash
for i in {1..5}
do
curl -X POST http://127.0.0.1:5000/submit-log \
-H "Content-Type: application/json" \
-d '{
  "source_ip": "192.168.1.50",
  "hostname": "unknown-host",
  "event_type": "failed_login",
  "severity": "medium",
  "destination_port": 22,
  "message": "Invalid SSH login attempt"
}'
done
```



## 🟠 Suspicious Activity (High Severity)

```bash
for i in {1..3}
do
curl -X POST http://127.0.0.1:5000/submit-log \
-H "Content-Type: application/json" \
-d '{
  "source_ip": "10.0.0.25",
  "hostname": "suspicious-node",
  "event_type": "multiple_failed_logins",
  "severity": "high",
  "destination_port": 22,
  "message": "Multiple authentication failures detected"
}'
done
```



## 🔴 Critical Malware Detection

```bash
for i in {1..2}
do
curl -X POST http://127.0.0.1:5000/submit-log \
-H "Content-Type: application/json" \
-d '{
  "source_ip": "172.16.100.50",
  "hostname": "critical-attacker",
  "event_type": "malware_detected",
  "severity": "critical",
  "destination_port": 445,
  "message": "Critical malware activity detected"
}'
done
```



## 🟣 Port Scan Simulation

```bash
for i in {1..6}
do
curl -X POST http://127.0.0.1:5000/submit-log \
-H "Content-Type: application/json" \
-d '{
  "source_ip": "192.168.1.99",
  "hostname": "scanner-host",
  "event_type": "port_scan",
  "severity": "medium",
  "destination_port": "'$((20 + i))'",
  "message": "Port scanning activity detected"
}'
done
```


## ⚫ Normal Traffic (Baseline Logs)

```bash
for i in {1..3}
do
curl -X POST http://127.0.0.1:5000/submit-log \
-H "Content-Type: application/json" \
-d '{
  "source_ip": "192.168.1.20",
  "hostname": "office-pc",
  "event_type": "file_access",
  "severity": "low",
  "destination_port": 443,
  "message": "User accessed internal file system"
}'
done
```


## 4. Alert System

The system automatically generates alerts when suspicious activity is detected.

### Supported detections:

* Brute Force Attack
* Port Scanning
* High Severity Incident Correlation


### View Alerts

/alerts



### Alert Lifecycle

1. Detection Engine identifies suspicious activity
2. Alert is created and stored in database
3. Email notification is sent automatically
4. Alert remains OPEN until resolved



## 5. Quarantine Module

The system can isolate compromised hosts.

### View quarantined hosts:

/quarantined-hosts


### Features:

* Automatic host quarantine on critical incidents
* Manual release of hosts via dashboard or API



## 6. AI Security Assistant

The AI module provides contextual analysis of alerts.

### Endpoints:

* Explain alert:

/ai/alert/<alert_id>/explain


* Ask security questions:

/ai/ask


* Chat interface:

/ai/chat


### Example questions:

* What caused this brute force alert?
* Summarize today's threats
* Is this IP malicious?



## 7. Reports

The system generates security reports for analysis and documentation.

### Available reports:

* Daily logs report
* PDF security report

### Endpoint:

/report/pdf

### Report includes:

* Attack summary
* Top attackers
* Alert history
* System activity overview


## 8. Alert Notifications

When an alert is triggered:

* Email is sent automatically to administrators
* Severity is assigned (low, medium, high, critical)
* Alert is stored in database


## 9. Severity Levels

* Low → Informational events
* Medium → Suspicious activity
* High → Strong indicators of attack
* Critical → Active threat requiring immediate response



## 10. Best Practices

* Monitor dashboard regularly
* Review alerts before resolving them
* Use AI assistant for investigation
* Generate reports for audits



## 11. Conclusion

The Mini-SIEM system provides real-time monitoring, detection, and response capabilities, improving visibility and incident response within an IT environment.
