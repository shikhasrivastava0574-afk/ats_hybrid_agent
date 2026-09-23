"""
Email Automation & Templating Module
Generates personalized interview invites, constructive growth feedback notes, and rejection emails.
"""

import urllib.parse
from typing import Dict, Any, List

def generate_email_templates(
    candidate_name: str,
    candidate_email: str,
    job_title: str,
    direct_decision: str,
    overall_match_score: int,
    key_strengths: List[str] = None,
    areas_to_probe: List[str] = None,
    interview_questions: List[str] = None,
    google_meet_link: str = None
) -> Dict[str, Any]:
    """
    Generates 3 types of candidate emails with pre-filled HTML content and mailto links.
    """
    candidate_email = candidate_email or "candidate@example.com"
    key_strengths = key_strengths or ["Strong engineering foundation", "Demonstrated project initiative"]
    areas_to_probe = areas_to_probe or ["Deep-dive system design", "Automated test coverage"]
    google_meet_link = google_meet_link or "https://meet.google.com/zin-interview"
    
    # TYPE 1: Interview Invitation Email
    invite_subject = f"Interview Invitation: {job_title} role at Zinsiehe"
    invite_body = f"""Hi {candidate_name},

Thank you for applying for the {job_title} position at Zinsiehe!

Our engineering hiring panel reviewed your resume and proof-of-work repositories (Consensus Score: {overall_match_score}/100), and we are excited to invite you for a 45-minute technical interview.

Meeting Details:
• Video Call: Google Meet ({google_meet_link})
• Position: {job_title}

Top Strengths Noted by Panel:
{chr(10).join([f"  • {s}" for s in key_strengths])}

Please confirm your availability for this upcoming week.

Best regards,
Zinsiehe Talent Acquisition Team
https://www.zinsiehe.com/
"""

    # TYPE 2: Constructive Growth Feedback Email (For Silver Medalists)
    feedback_subject = f"Application Update & Feedback: {job_title} role at Zinsiehe"
    feedback_body = f"""Hi {candidate_name},

Thank you for taking the time to apply for the {job_title} position at Zinsiehe.

While we are moving forward with candidates whose current background aligns more closely with our 5-6 YOE consulting requirements, our technical panel wanted to share personalized feedback:

Key Strengths Identified:
{chr(10).join([f"  • {s}" for s in key_strengths])}

Recommended Areas for Growth:
{chr(10).join([f"  • {p}" for p in areas_to_probe])}

We have saved your profile in our talent network for future openings.

Best regards,
Zinsiehe Recruitment Team
"""

    # TYPE 3: Standard Rejection Email
    rejection_subject = f"Application Status: {job_title} at Zinsiehe"
    rejection_body = f"""Dear {candidate_name},

Thank you for your interest in joining Zinsiehe for the {job_title} position.

After careful evaluation, we regret to inform you that we will not be moving forward with your application for this specific position as it requires a minimum of 5-6 years of experience.

We wish you the best in your job search.

Sincerely,
Zinsiehe Hiring Team
"""

    # Create Mailto Links
    invite_mailto = f"mailto:{candidate_email}?subject={urllib.parse.quote(invite_subject)}&body={urllib.parse.quote(invite_body)}"
    feedback_mailto = f"mailto:{candidate_email}?subject={urllib.parse.quote(feedback_subject)}&body={urllib.parse.quote(feedback_body)}"
    rejection_mailto = f"mailto:{candidate_email}?subject={urllib.parse.quote(rejection_subject)}&body={urllib.parse.quote(rejection_body)}"

    return {
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "interview_invite": {
            "subject": invite_subject,
            "body": invite_body,
            "mailto_link": invite_mailto
        },
        "growth_feedback": {
            "subject": feedback_subject,
            "body": feedback_body,
            "mailto_link": feedback_mailto
        },
        "rejection": {
            "subject": rejection_subject,
            "body": rejection_body,
            "mailto_link": rejection_mailto
        }
    }

if __name__ == "__main__":
    res = generate_email_templates("Alex Chen", "alex@example.com", "Senior Full-Stack AI Engineer", "YES", 82)
    print("Generated Email Subject:", res["interview_invite"]["subject"])
