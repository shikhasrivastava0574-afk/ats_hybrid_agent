"""
FastAPI Production Server for ATS Hybrid Agent
Replaces Streamlit with a high-performance REST API & HTML5/Tailwind CSS Web Application.
"""

import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any

from pdf_parser import parse_resume_pdf
from github_auditor import audit_github_profile
from multi_agent_panel import MultiAgentHiringPanel
from sample_candidates import SAMPLE_CANDIDATES, SAMPLE_JOB_DESCRIPTIONS
from google_meet_scheduler import generate_google_calendar_url

app = FastAPI(
    title="Zinsiehe ATS Agent API",
    description="FastAPI Backend & Interactive Web UI for ATS Hybrid Agent",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init Hiring Panel Engine
panel_engine = MultiAgentHiringPanel()

@app.get("/api/sample_data")
def get_sample_data():
    """Returns sample candidates and Zinsiehe job descriptions."""
    return {
        "sample_candidates": SAMPLE_CANDIDATES,
        "sample_job_descriptions": SAMPLE_JOB_DESCRIPTIONS
    }

@app.post("/api/parse_pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """Upload and parse a candidate resume PDF."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    contents = await file.read()
    import io
    pdf_stream = io.BytesIO(contents)
    
    parsed = parse_resume_pdf(pdf_stream)
    if not parsed["success"]:
        raise HTTPException(status_code=500, detail=parsed.get("error", "Failed to parse PDF"))
        
    return parsed

@app.post("/api/github_audit")
def audit_github(username: str = Form(...)):
    """Audit candidate GitHub profile and repositories."""
    if not username:
        raise HTTPException(status_code=400, detail="GitHub username is required")
    return audit_github_profile(username)

@app.post("/api/evaluate")
def evaluate_candidate(
    candidate_name: str = Form(...),
    resume_text: str = Form(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    github_username: Optional[str] = Form(None)
):
    """Run Multi-Agent Hiring Board Debate & Experience Gate."""
    audit_data = {}
    if github_username:
        audit_data = audit_github_profile(github_username)
        
    results = panel_engine.run_panel_debate(
        candidate_name=candidate_name,
        resume_text=resume_text,
        job_title=job_title,
        job_description=job_description,
        github_audit=audit_data
    )
    results["github_audit"] = audit_data
    return results

@app.post("/api/schedule_meet")
def schedule_meet(
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    job_title: str = Form(...),
    match_score: int = Form(80),
    meeting_date: Optional[str] = Form(None),
    meeting_time: Optional[str] = Form(None)
):
    """Generate pre-filled Google Calendar & Google Meet URLs."""
    return generate_google_calendar_url(
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        job_title=job_title,
        match_score=match_score,
        meeting_date=meeting_date,
        meeting_time=meeting_time
    )

@app.get("/", response_class=HTMLResponse)
def index_page():
    """Serves the main single-page web UI."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "<h1>FastAPI ATS Agent Backend Running! (templates/index.html not found)</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
