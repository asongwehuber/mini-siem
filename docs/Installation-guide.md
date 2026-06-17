
# Mini-SIEM Installation Guide (Production-Ready Version)

## 1. Introduction

This guide explains how to install, configure, and run the Mini-SIEM system, including environment setup, dependencies, database configuration, and email integration.

The system is built using:

* Flask (backend framework)
* MySQL (relational database)
* Flask-Mail (email alerting system)
* Ollama (AI security assistant)
* python-dotenv (.env configuration management)


## 2. Prerequisites

Ensure the following software is installed:

* Python 3.10 or higher
* MySQL Server
* Git
* Ollama (optional, for AI features)
* Virtualenv (recommended)

Verify installations:

```bash
python --version
mysql --version
git --version
```


## 3. Clone the Repository

```bash
git clone https://github.com/asongwehuber/mini-siem.git
cd mini-siem
```


## 4. Create Virtual Environment

### Linux / WSL

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```


## 5. Install Dependencies

```bash
pip install -r requirements.txt
```


## 6. Environment Configuration (.env)

Create a `.env` file in the project root directory. There is a ".env.example" file to use as reference:

```bash
touch .env
```

Add the following configuration:

```env
# DATABASE CONFIGURATION
DB_USER=siemuser
DB_PASSWORD=StrongPassword123!
DB_HOST=localhost
DB_NAME=mini_siem

# EMAIL CONFIGURATION
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=your_gmail@gmail.com
```

> ⚠️ Ensure that `.env` is excluded from version control using `.gitignore`.


## 7. MySQL Database Setup

Access MySQL:

```bash
mysql -u root -p
```

Create database and user:

```sql
CREATE DATABASE mini_siem;

CREATE USER 'siemuser'@'localhost' IDENTIFIED BY 'StrongPassword123!';

GRANT ALL PRIVILEGES ON mini_siem.* TO 'siemuser'@'localhost';

FLUSH PRIVILEGES;
```

---

## 8. Initialize Database Schema

Run the following commands:

```bash
python
```

```python
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
```

Exit Python:

```bash
exit()
```

---

## 9. Install and Configure Ollama (AI Module)

Download Ollama:

👉 [https://ollama.com](https://ollama.com)

Pull required model:

```bash
ollama pull llama3
```

Start Ollama service:

```bash
ollama serve
```


## 10. Run the Application

```bash
python run.py
```

Expected output:

```text
Running on http://127.0.0.1:5000
```


## 11. Access the System

Open a browser:

```
http://127.0.0.1:5000
```


## 12. System Verification

### Dashboard

* Logs overview
* Active alerts
* Quarantined hosts status


### Test Log Submission

```bash
curl -X POST http://127.0.0.1:5000/submit-log \
-H "Content-Type: application/json" \
-d '{
  "source_ip": "192.168.1.10",
  "event_type": "failed_login",
  "severity": "medium",
  "destination_port": 22,
  "message": "Test log entry"
}'
```

---

### Test Email Alerts

Trigger a brute-force simulation to validate email notifications.

---

### Test AI Module

Access:

```
http://127.0.0.1:5000/ai/chat
```

---

## 13. Troubleshooting

### ❌ Environment variables not loading

Ensure:

```bash
pip install python-dotenv
```

and that `.env` is located in the project root directory.

---

### ❌ MySQL connection failure

Check:

* Database credentials
* MySQL service is running
* Database `mini_siem` exists

---

### ❌ Email alerts not sending

Verify:

* Gmail App Password (not normal password)
* 2-Step Verification enabled
* SMTP configuration is correct

---

## 14. Summary

The Mini-SIEM system is now fully configured using environment variables, improving security, modularity, and production readiness.
