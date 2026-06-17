# Mini-SIEM with AI-Assisted Threat Analysis

## Overview

Mini-SIEM is a Security Information and Event Management (SIEM) platform developed during an internship. The system collects security logs, detects suspicious activities, generates alerts, provides automated response mechanisms, and integrates artificial intelligence to assist analysts in investigating security incidents.

The objective of the project is to demonstrate the core functionalities of a SIEM solution within a lightweight and educational environment while applying cybersecurity concepts such as log management, threat detection, incident response, and security analytics.


## Features

### Log Management
- Centralized log collection
- Real-time log ingestion
- Log search and filtering
- Individual log inspection

### Threat Detection
- Brute-force login detection
- Port scanning detection
- Suspicious activity correlation
- Severity-based alert generation

### Alert Management
- Alert dashboard
- Alert status tracking
- Alert resolution workflow

### Automated Response
- Host quarantine simulation
- Host release management
- Incident containment tracking

### AI-Powered Security Analysis
- Natural language interaction with security data
- Alert explanation
- Context-aware incident analysis
- Security recommendations

### Reporting
- Daily security reports
- PDF report generation
- Alert statistics and summaries

### Notifications
- Email alert notifications
- Security incident reporting



## System Architecture

```text
+--------------------+
| Log Sources        |
| Endpoints          |
| Security Devices   |
+----------+---------+
           |
           v
+--------------------+
| Flask Log API      |
+----------+---------+
           |
           v
+--------------------+
| Detection Engine   |
+----------+---------+
           |
     +-----+-----+
     |           |
     v           v
+---------+   +---------+
| Alerts  |   | AI      |
+---------+   +---------+
     |
     v
+--------------------+
| Dashboard          |
| Reports            |
| Notifications      |
+--------------------+




###🔌 API Reference

The Mini-SIEM system exposes a RESTful API used for log ingestion, security analytics, alert management, reporting, and AI-assisted investigation.

All responses are returned in JSON format.


### Base URL

```text
http://localhost:5000/
```


## 📥 Log Management

### Submit Log

```http
POST /submit-log
```

**Description:**
Ingests a new security event into the SIEM system.

**Example Request:**

```json
{
  "source": "firewall",
  "event_type": "login_failure",
  "severity": "high",
  "message": "Failed login attempt detected",
  "timestamp": "2026-06-17T10:30:00"
}
```

### Get All Logs

```http
GET /logs
```

**Description:**
Retrieves all stored security logs.

### Filter Logs by Severity

```http
GET /logs?severity=high
```


## 📊 Threat Detection & Analytics

### Failed Login Statistics

```http
GET /logs/stats/failed-logins
```

**Description:**
Returns total number of failed login attempts.


## 🚨 Alert Management

### Get All Alerts

```http
GET /alerts
```

### Update Alert Status

```http
PUT /alerts/<alert_id>
```

**Example Request:**

```json
{
  "status": "resolved"
}
```


## 🤖 AI Security Assistant

### Chat with AI

```http
POST /ai/chat
```

**Example Request:**

```json
{
  "question": "How many failed logins do we have?"
}
```


### AI Log Analysis

```http
POST /ai/analyze
```

**Description:**
Provides intelligent analysis of security logs and detects anomalies.


## 📄 Reporting

### Generate Report

```http
POST /report/generate
```

### Get Report

```http
GET /report/<report_id>
```


## ⚠️ Error Format

```json
{
  "status": "error",
  "message": "Description of the error"
}
```

## 🧠 Notes

* All endpoints return JSON responses
* Timestamps follow ISO 8601 format
* This API is designed for educational and simulation purposes
* AI endpoints enhance analyst decision-making, not replace it
