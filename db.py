"""
SQLite Candidate Persistence & Audit Log Module
Stores applicants, AI evaluation outputs, recruiter override feedback logs, and interview histories.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "candidates.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Candidates Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        github_username TEXT,
        raw_text TEXT,
        job_title TEXT,
        proof_of_work_score INTEGER DEFAULT 0,
        overall_match_score INTEGER DEFAULT 0,
        direct_decision TEXT,
        recruiter_status TEXT DEFAULT 'Ingested',
        recruiter_override_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Evaluation Details Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_details (
        candidate_id TEXT PRIMARY KEY,
        verdict_summary TEXT,
        agent_debates TEXT,
        chair_synthesis TEXT,
        interview_questions TEXT,
        github_audit_json TEXT,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
    )
    """)
    
    # Recruiter Feedback & AI Override Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recruiter_overrides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        original_ai_decision TEXT,
        new_recruiter_status TEXT,
        override_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
    )
    """)
    
    conn.commit()
    conn.close()

def save_candidate_eval(cand_data: Dict[str, Any], results: Dict[str, Any]) -> str:
    """
    Saves or updates a candidate record along with full evaluation details.
    Returns candidate_id.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Generate unique ID based on email or name
    email = cand_data.get("email") or ""
    name = cand_data.get("name") or "Candidate"
    import hashlib
    cand_id = "cand_" + hashlib.md5(f"{name}_{email}".encode()).hexdigest()[:10]
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    direct_decision = results.get("direct_decision", "NO - DO NOT INTERVIEW")
    recruiter_status = "Shortlisted" if "YES" in direct_decision.upper() else "Rejected"
    
    # Insert or Replace Candidate
    cursor.execute("""
    INSERT INTO candidates (
        id, name, email, phone, github_username, raw_text, job_title,
        proof_of_work_score, overall_match_score, direct_decision, recruiter_status, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name=excluded.name,
        email=excluded.email,
        phone=excluded.phone,
        github_username=excluded.github_username,
        raw_text=excluded.raw_text,
        job_title=excluded.job_title,
        proof_of_work_score=excluded.proof_of_work_score,
        overall_match_score=excluded.overall_match_score,
        direct_decision=excluded.direct_decision,
        recruiter_status=excluded.recruiter_status,
        updated_at=excluded.updated_at
    """, (
        cand_id,
        name,
        email,
        cand_data.get("phone"),
        cand_data.get("github_username"),
        cand_data.get("raw_text"),
        results.get("job_title"),
        results.get("github_audit", {}).get("proof_of_work_score", 0),
        results.get("overall_match_score", 0),
        direct_decision,
        recruiter_status,
        now
    ))
    
    # Save Evaluation Details
    cursor.execute("""
    INSERT INTO evaluation_details (
        candidate_id, verdict_summary, agent_debates, chair_synthesis, interview_questions, github_audit_json
    ) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(candidate_id) DO UPDATE SET
        verdict_summary=excluded.verdict_summary,
        agent_debates=excluded.agent_debates,
        chair_synthesis=excluded.chair_synthesis,
        interview_questions=excluded.interview_questions,
        github_audit_json=excluded.github_audit_json
    """, (
        cand_id,
        results.get("verdict_summary"),
        json.dumps(results.get("agent_debates", [])),
        json.dumps(results.get("chair_synthesis", {})),
        json.dumps(results.get("interview_questions", [])),
        json.dumps(results.get("github_audit", {}))
    ))
    
    conn.commit()
    conn.close()
    return cand_id

def get_all_candidates(search: Optional[str] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all candidates from database with optional filtering."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM candidates WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR email LIKE ? OR job_title LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    if status_filter and status_filter != "All":
        query += " AND recruiter_status = ?"
        params.append(status_filter)
        
    query += " ORDER BY overall_match_score DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    candidates = []
    for r in rows:
        cand = dict(r)
        candidates.append(cand)
        
    conn.close()
    return candidates

def get_candidate_details(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Fetches candidate metadata + full evaluation details by candidate_id."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    c_row = cursor.fetchone()
    if not c_row:
        conn.close()
        return None
        
    cand = dict(c_row)
    
    cursor.execute("SELECT * FROM evaluation_details WHERE candidate_id = ?", (candidate_id,))
    e_row = cursor.fetchone()
    if e_row:
        eval_dict = dict(e_row)
        cand["verdict_summary"] = eval_dict.get("verdict_summary")
        cand["agent_debates"] = json.loads(eval_dict.get("agent_debates") or "[]")
        cand["chair_synthesis"] = json.loads(eval_dict.get("chair_synthesis") or "{}")
        cand["interview_questions"] = json.loads(eval_dict.get("interview_questions") or "[]")
        cand["github_audit"] = json.loads(eval_dict.get("github_audit_json") or "{}")
        
    conn.close()
    return cand

def save_recruiter_override(candidate_id: str, new_status: str, override_reason: str) -> bool:
    """Logs recruiter decision override and updates candidate status."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT direct_decision FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
        
    original_decision = row["direct_decision"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update status & override reason
    cursor.execute("""
    UPDATE candidates SET recruiter_status = ?, recruiter_override_reason = ?, updated_at = ?
    WHERE id = ?
    """, (new_status, override_reason, now, candidate_id))
    
    # Log Override History
    cursor.execute("""
    INSERT INTO recruiter_overrides (candidate_id, original_ai_decision, new_recruiter_status, override_reason)
    VALUES (?, ?, ?, ?)
    """, (candidate_id, original_decision, new_status, override_reason))
    
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
    print("Database initialized at:", DB_PATH)
