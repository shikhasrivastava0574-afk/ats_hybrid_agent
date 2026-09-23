"""
FastAPI Production Server for Zinsiehe Enterprise ATS Suite
Provides REST API endpoints for single/bulk resume screening, candidate database persistence,
recruiter AI decision overrides, email automation, and Google Meet scheduling.
"""

import os
import io
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List

from pdf_parser import parse_resume_pdf
from github_auditor import audit_github_profile
from multi_agent_panel import MultiAgentHiringPanel
from sample_candidates import SAMPLE_CANDIDATES, SAMPLE_JOB_DESCRIPTIONS
from google_meet_scheduler import generate_google_calendar_url
from db import init_db, save_candidate_eval, get_all_candidates, get_candidate_details, save_recruiter_override
from bulk_processor import BulkResumeProcessor
from email_automation import generate_email_templates

app = FastAPI(
    title="Zinsiehe Enterprise ATS Suite API",
    description="FastAPI Backend & Interactive Web UI for Bulk ATS Screening, Database Persistence, and AI Overrides",
    version="3.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database & Engines
init_db()
panel_engine = MultiAgentHiringPanel()
bulk_engine = BulkResumeProcessor()

@app.get("/api/sample_data")
def get_sample_data():
    """Returns sample candidates and Zinsiehe job descriptions."""
    return {
        "sample_candidates": SAMPLE_CANDIDATES,
        "sample_job_descriptions": SAMPLE_JOB_DESCRIPTIONS
    }

@app.post("/api/parse_pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """Upload and parse a single candidate resume PDF."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    contents = await file.read()
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
    """Run Multi-Agent Hiring Board Debate & Experience Gate, saving to SQLite database."""
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
    
    # Save Candidate to Persistent Database
    cand_data = {
        "name": candidate_name,
        "raw_text": resume_text,
        "github_username": github_username
    }
    cand_id = save_candidate_eval(cand_data, results)
    results["candidate_id"] = cand_id
    
    return results

@app.post("/api/bulk_upload")
async def bulk_upload(
    files: List[UploadFile] = File(...),
    job_title: str = Form(...),
    job_description: str = Form(...)
):
    """
    Bulk resume screening endpoint for 50-100 resumes.
    Parses, audits GitHub, evaluates AI hiring board, and ranks candidates into a leaderboard.
    """
    file_tuples = []
    for f in files:
        if f.filename.endswith(".pdf"):
            content = await f.read()
            file_tuples.append((f.filename, content))
            
    if not file_tuples:
        raise HTTPException(status_code=400, detail="No valid PDF resumes uploaded.")
        
    summary = bulk_engine.process_bulk_resumes(file_tuples, job_title, job_description)
    return summary

@app.get("/api/candidates")
def list_candidates(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query("All")
):
    """Fetch stored candidate applicants from SQLite database."""
    return get_all_candidates(search_query=search, status_filter=status)

@app.get("/api/candidate_details/{candidate_id}")
def candidate_details(candidate_id: str):
    """Fetch detailed evaluation logs and information for a candidate."""
    cand = get_candidate_details(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return cand

@app.post("/api/recruiter_override")
def recruiter_override(
    candidate_id: str = Form(...),
    new_status: str = Form(...),
    override_reason: str = Form(...)
):
    """Log recruiter manual decision override and feedback rationale for AI calibration."""
    success = save_recruiter_override(candidate_id, new_status, override_reason)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "success", "message": "Recruiter override recorded successfully"}

@app.post("/api/generate_email")
def generate_email(
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    job_title: str = Form(...),
    direct_decision: str = Form("YES"),
    overall_match_score: int = Form(80),
    google_meet_link: Optional[str] = Form(None)
):
    """Generate pre-filled personalized candidate emails (Invite, Growth Feedback, Rejection)."""
    return generate_email_templates(
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        job_title=job_title,
        direct_decision=direct_decision,
        overall_match_score=overall_match_score,
        google_meet_link=google_meet_link
    )

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
    """Serves the main HTML5/Tailwind CSS interactive Web UI."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "<h1>FastAPI ATS Agent Backend Running! (templates/index.html not found)</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
