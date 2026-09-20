# Zinsiehe ATS Agent | AI Recruitment & Proof-of-Work Platform

An autonomous, multi-agent Applicant Tracking & Shortlisting System engineered for **Zinsiehe** (Gen AI & Analytics Consultancy). The platform combines **Resume PDF Parsing**, **GitHub Proof-of-Work Auditing**, and an **Autonomous 3-Agent Hiring Committee Debate** with a dedicated **5-6 YOE Culture Fit Evaluation Module**.

---

## 🌟 Key Features

- 📄 **Multi-Format Resume Ingestion**: Parses PDFs, extracts emails, phone numbers, and detects embedded GitHub/portfolio URLs using `pypdf`.
- 💻 **GitHub Proof-of-Work Audit**: Fetches public GitHub profile repositories, total stars, followers, and language breakdown to calculate a verified **Proof-of-Work Score (0-100)**.
- 👥 **Autonomous Hiring Committee Debate**: Spawns 3 specialized AI Agents:
  - 💻 **Tech Lead Agent**: Evaluates technical stack fit, code quality, and GitHub proof-of-work.
  - 🤝 **Culture & Values Agent (5-6 YOE Focus)**: Evaluates **Mentorship**, **Cross-Functional Autonomy (RFCs/specs)**, **Pragmatic Tech Debt Management**, and **Production Ownership**.
  - 🚀 **Growth & Velocity Agent**: Evaluates career progression speed and self-driven project initiative.
- 🛑 **Hard Experience Gate**: Disqualifies 0 YOE / entry-level resumes when evaluating candidates for 5-6 YOE Senior roles.
- ⚡ **Modern Executive Dashboard**: Built with Streamlit featuring a modern dark glassmorphic 2-column layout and immediate `YES` or `NO` decision banners.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    PDF[Candidate Resume PDF] --> Parser[PDF & URL Parser Module]
    GitHub[GitHub API / Portfolio Link] --> Auditor[Proof-of-Work Auditor]
    
    Parser --> Panel[Multi-Agent Hiring Panel]
    Auditor --> Panel
    
    subgraph Panel ["Autonomous Hiring Committee"]
        Panel --> TechLead[Tech Lead Agent]
        Panel --> Culture[5-6 YOE Culture Fit Agent]
        Panel --> Growth[Growth Velocity Agent]
    end
    
    TechLead & Culture & Growth --> Chair[Panel Chair Agent]
    Chair --> Verdict["Direct Verdict: YES (Take Interview) / NO (Do Not Interview)"]
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ats-hybrid-agent.git
cd ats-hybrid-agent

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Running Automated Tests

Run the unit test suite:
```bash
python3 test_ats.py
```

---

## 📦 Project Structure

```
├── app.py                   # Streamlit Executive Glassmorphism UI
├── pdf_parser.py            # PDF resume & URL extractor
├── github_auditor.py        # GitHub API & proof-of-work quality auditor
├── multi_agent_panel.py     # 4-Agent Hiring Board Debate Engine
├── sample_candidates.py     # Sample profiles and Zinsiehe job descriptions
├── test_ats.py              # Automated test suite
├── requirements.txt         # Dependencies
└── README.md                # Documentation & GitHub Deployment Guide
```

---

## 📄 License
MIT License
