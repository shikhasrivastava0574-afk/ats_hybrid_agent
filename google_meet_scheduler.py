"""
Google Meet & Calendar Scheduling Module
Generates pre-filled Google Calendar event URLs and Google Meet interview invitations for shortlisted candidates.
"""

import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any

def generate_google_calendar_url(
    candidate_name: str,
    candidate_email: str,
    job_title: str,
    interview_questions: list = None,
    match_score: int = 80,
    meeting_date: str = None,
    meeting_time: str = None
) -> Dict[str, Any]:
    """
    Generates a pre-populated Google Calendar + Google Meet creation link.
    """
    interview_questions = interview_questions or []
    
    # Title
    title = f"Zinsiehe Technical Interview - {candidate_name} ({job_title})"
    
    # Description Body
    questions_formatted = "\n".join([f"• Q{i+1}: {q}" for i, q in enumerate(interview_questions[:3])])
    description = (
        f"Zinsiehe Candidate Interview Invitation\n"
        f"Candidate Name: {candidate_name}\n"
        f"Target Role: {job_title}\n"
        f"Consensus Match Score: {match_score}/100\n\n"
        f"Suggested Interview Questions:\n{questions_formatted}\n\n"
        f"Note: Click 'Add Google Meet video conferencing' in Google Calendar."
    )
    
    # Pre-filled Date / Time handling
    if meeting_date and meeting_time:
        try:
            start_dt = datetime.strptime(f"{meeting_date} {meeting_time}", "%Y-%m-%d %H:%M")
        except Exception:
            start_dt = datetime.now() + timedelta(days=2)
    else:
        start_dt = datetime.now() + timedelta(days=2)
        start_dt = start_dt.replace(hour=14, minute=0, second=0)

    end_dt = start_dt + timedelta(minutes=45)
    
    # Format YYYYMMDDTHHMMSSZ for Google Calendar
    fmt = "%Y%m%dT%H%M%SZ"
    dates_param = f"{start_dt.strftime(fmt)}/{end_dt.strftime(fmt)}"
    
    params = {
        "action": "TEMPLATE",
        "text": title,
        "details": description,
        "dates": dates_param,
        "add": candidate_email if candidate_email and "@" in candidate_email else ""
    }
    
    gcal_url = "https://calendar.google.com/calendar/render?" + urllib.parse.urlencode(params)
    
    # Create deterministic mock Google Meet link for quick 1-click sharing
    slug = "".join([c.lower() for c in candidate_name if c.isalnum()])[:8]
    mock_meet_link = f"https://meet.google.com/zin-{slug[:3]}-{slug[3:7] or 'interview'}"
    
    return {
        "gcal_url": gcal_url,
        "google_meet_link": mock_meet_link,
        "event_title": title,
        "start_time": start_dt.strftime("%B %d, %Y at %I:%M %p"),
        "candidate_email": candidate_email
    }

if __name__ == "__main__":
    res = generate_google_calendar_url(
        candidate_name="Alex Chen",
        candidate_email="alex.chen@example.com",
        job_title="Senior Gen AI Engineer",
        interview_questions=["How do you build RAG pipelines?"]
    )
    print("Google Calendar URL:", res["gcal_url"])
    print("Google Meet Link:", res["google_meet_link"])
