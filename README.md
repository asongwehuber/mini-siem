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
- Telegram alert notification
- Telegram voice notification for critical alert
- SMS notification for critical alert
- IVR (interactive voice response) for critical alerts



## System Architecture


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


