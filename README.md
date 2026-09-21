# Zinsiehe ATS Agent | FastAPI & HTML5 / Tailwind CSS Platform

An autonomous, multi-agent Applicant Tracking & Shortlisting System built for **Zinsiehe** (Gen AI & Analytics Consultancy). Powered by **FastAPI**, **HTML5/Tailwind CSS**, **pypdf**, and **GitHub REST API**.

---

## 🚀 Why FastAPI instead of Streamlit?

1. **Lightning Fast Performance**: High-throughput asynchronous REST API endpoints with zero Streamlit iframe re-renders.
2. **Production REST API**: Standard JSON endpoints for PDF parsing, GitHub auditing, Multi-Agent panel debates, and Google Meet interview scheduling.
3. **Custom HTML5 & Tailwind UI**: Modern dark glassmorphism dashboard with Executive Grid and Kanban funnel views.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    Client["HTML5 / Tailwind CSS Web App (index.html)"] <--> REST["FastAPI Production Server (server.py)"]
    
    REST --> Parser["pdf_parser.py (Resume Ingestion)"]
    REST --> Auditor["github_auditor.py (Proof-of-Work API)"]
    REST --> Panel["multi_agent_panel.py (4-Agent Hiring Committee & 5-6 YOE Gate)"]
    REST --> Meet["google_meet_scheduler.py (Google Meet Link Generator)"]
```

---

## ⚙️ REST API Endpoints

- `GET /`: Serves the HTML5/Tailwind CSS interactive web dashboard.
- `GET /api/sample_data`: Returns sample candidate profiles & Zinsiehe job descriptions.
- `POST /api/parse_pdf`: Upload PDF resume file and extract text/contact details.
- `POST /api/github_audit`: Audit public GitHub profile repository metrics.
- `POST /api/evaluate`: Execute 4-Agent Hiring Board Debate & Hard 5-6 YOE Experience Gate.
- `POST /api/schedule_meet`: Generate pre-filled Google Calendar & Google Meet video call links.

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
git clone https://github.com/shikhasrivastava0574-afk/ats_hybrid_agent.git
cd ats_hybrid_agent
pip install -r requirements.txt
```

### 2. Run the FastAPI Web Server
```bash
python3 server.py
# or: uvicorn server:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser.

---

## 🧪 Automated Unit Tests

```bash
python3 test_ats.py
```

---

## 📄 License
MIT License
