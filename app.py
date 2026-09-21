"""
Hybrid ATS Agent - Multi-Layout Interactive Dashboard with Google Meet Scheduling
Supports 3 distinct UI layout modes and Google Meet interview scheduling.
"""

import os
import streamlit as st
from datetime import datetime, date, time

# Page Configuration
st.set_page_config(
    page_title="Zinsiehe ATS Agent | Multi-Layout & Google Meet Scheduler",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from pdf_parser import parse_resume_pdf, extract_urls_and_contact
from github_auditor import audit_github_profile
from multi_agent_panel import MultiAgentHiringPanel
from sample_candidates import SAMPLE_CANDIDATES, SAMPLE_JOB_DESCRIPTIONS
from google_meet_scheduler import generate_google_calendar_url

# Custom Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .card-yes {
        border-left: 4px solid #10b981;
        background: rgba(16, 185, 129, 0.08);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .card-no {
        border-left: 4px solid #ef4444;
        background: rgba(239, 68, 68, 0.08);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .badge-yes {
        background-color: #10b981;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .badge-no {
        background-color: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .meet-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(37, 99, 235, 0.2) 100%);
        border: 2px solid #3b82f6;
        border-radius: 14px;
        padding: 18px;
        margin-top: 16px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Dashboard Settings")
        
        layout_style = st.radio(
            "🎨 Choose Dashboard Layout:",
            [
                "🚀 Executive Glassmorphism Grid",
                "📋 Kanban Pipeline View",
                "⚡ Compact Command Center"
            ]
        )
        
        st.divider()
        st.subheader("🎯 Job Selection")
        job_choice = st.selectbox(
            "Select Target Job Role:",
            list(SAMPLE_JOB_DESCRIPTIONS.keys()),
            index=len(SAMPLE_JOB_DESCRIPTIONS)-1 if "Zinsiehe" in list(SAMPLE_JOB_DESCRIPTIONS.keys())[-1] else 0
        )
        target_job_title = job_choice
        target_job_desc = SAMPLE_JOB_DESCRIPTIONS[job_choice]
        
        st.divider()
        st.subheader("📄 Candidate Input")
        upload_pdf = st.file_uploader("Upload PDF Resume:", type=["pdf"])
        sample_idx = st.selectbox(
            "Or Pick Sample Candidate:",
            range(len(SAMPLE_CANDIDATES)),
            format_func=lambda i: SAMPLE_CANDIDATES[i]["name"]
        )
        if st.button("Load Sample Profile", use_container_width=True):
            sample = SAMPLE_CANDIDATES[sample_idx]
            st.session_state.current_candidate = {
                "name": sample["name"],
                "email": sample["email"],
                "phone": sample["phone"],
                "github_username": sample["github_username"],
                "raw_text": sample["resume_summary"],
                "source": "Sample Profile"
            }
            st.session_state.github_audit = sample["mock_github"]
            st.session_state.panel_results = None
            
        if upload_pdf is not None:
            parsed = parse_resume_pdf(upload_pdf)
            if parsed["success"]:
                c_info = parsed["contact_info"]
                st.session_state.current_candidate = {
                    "name": parsed["candidate_name"],
                    "email": c_info.get("email", "N/A"),
                    "phone": c_info.get("phone", "N/A"),
                    "github_username": c_info.get("github_username"),
                    "raw_text": parsed["raw_text"],
                    "source": upload_pdf.name
                }
                st.session_state.github_audit = None
                st.session_state.panel_results = None

    # Session State Initialization
    if "current_candidate" not in st.session_state:
        st.session_state.current_candidate = None
    if "github_audit" not in st.session_state:
        st.session_state.github_audit = None
    if "panel_results" not in st.session_state:
        st.session_state.panel_results = None

    if not st.session_state.current_candidate:
        st.title("Zinsiehe ATS Agent")
        st.info("👈 Please load a sample candidate or upload a PDF resume from the sidebar.")
        return

    cand = st.session_state.current_candidate
    gh_username = cand.get("github_username")

    if not st.session_state.github_audit and gh_username:
        st.session_state.github_audit = audit_github_profile(gh_username)

    if not st.session_state.panel_results:
        panel = MultiAgentHiringPanel()
        st.session_state.panel_results = panel.run_panel_debate(
            candidate_name=cand["name"],
            resume_text=cand["raw_text"],
            job_title=target_job_title,
            job_description=target_job_desc,
            github_audit=st.session_state.github_audit or {}
        )

    results = st.session_state.panel_results

    # RENDER SELECTED LAYOUT STYLE
    if "Kanban" in layout_style:
        render_kanban_layout(cand, results, target_job_title)
    elif "Command Center" in layout_style:
        render_command_center_layout(cand, results, target_job_title)
    else:
        render_executive_grid_layout(cand, results, target_job_title)

def render_google_meet_module(cand, results, target_job_title):
    """Render Google Meet & Calendar Scheduling Card for Shortlisted Candidates."""
    is_yes = "YES" in results.get("direct_decision", "").upper()
    if not is_yes:
        return

    st.markdown('<div class="meet-card">', unsafe_allow_html=True)
    st.markdown("### 📅 Schedule Google Meet Interview")
    st.caption("Candidate is shortlisted! Schedule the Google Meet video call directly into Google Calendar.")

    col1, col2 = st.columns([1, 1])
    with col1:
        m_date = st.date_input("Interview Date:", value=date.today())
        m_time = st.time_input("Interview Time (IST):", value=time(14, 0))
    with col2:
        cand_email = st.text_input("Candidate Email Address:", value=cand.get("email") or "")
        
    date_str = m_date.strftime("%Y-%m-%d")
    time_str = m_time.strftime("%H:%M")

    sched_info = generate_google_calendar_url(
        candidate_name=cand["name"],
        candidate_email=cand_email,
        job_title=target_job_title,
        interview_questions=results.get("interview_questions", []),
        match_score=results.get("overall_match_score", 80),
        meeting_date=date_str,
        meeting_time=time_str
    )

    st.markdown(f"**Generated Google Meet Link:** [`{sched_info['google_meet_link']}`]({sched_info['google_meet_link']})")
    
    st.markdown(
        f'<a href="{sched_info["gcal_url"]}" target="_blank" style="display:inline-block; background-color:#2563eb; color:white; padding:10px 20px; border-radius:10px; font-weight:bold; text-decoration:none;">📅 Add Event & Schedule Google Meet Call</a>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# LAYOUT STYLE A: EXECUTIVE GLASSMORPHISM GRID
def render_executive_grid_layout(cand, results, target_job_title):
    st.title("🚀 Zinsiehe Executive Hiring Dashboard")
    st.caption(f"Role: **{target_job_title}** | Candidate: **{cand['name']}**")
    
    is_yes = "YES" in results.get("direct_decision", "").upper()
    badge_color = "#10b981" if is_yes else "#ef4444"
    icon_symbol = "✅" if is_yes else "❌"

    # Top Hero Card
    st.markdown(f"""
    <div style="border: 2px solid {badge_color}; border-radius: 16px; padding: 20px; background: rgba(30, 41, 59, 0.7); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="badge-{'yes' if is_yes else 'no'}">{icon_symbol} DIRECT DECISION: {results.get('direct_decision')}</span>
                <h2 style="margin-top: 10px; margin-bottom: 2px;">Candidate: {cand['name']}</h2>
                <span style="color: #94a3b8;">Target Position: {target_job_title}</span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.85rem; color: #94a3b8;">Match Score</span>
                <div style="font-size: 3rem; font-weight: 800; color: {badge_color};">{results.get('overall_match_score', 0)}/100</div>
            </div>
        </div>
        <hr style="border-top: 1px solid rgba(255,255,255,0.1); margin: 12px 0;"/>
        <p style="margin: 0;"><strong>Verdict Summary:</strong> {results.get('verdict_summary')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Google Meet Module if Shortlisted
    render_google_meet_module(cand, results, target_job_title)

    st.markdown("<br/>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("### 💻 Candidate & Proof-of-Work")
        st.json({
            "Name": cand["name"],
            "Email": cand.get("email"),
            "GitHub": cand.get("github_username") or "Not Provided",
            "Proof-of-Work Score": f"{st.session_state.github_audit.get('proof_of_work_score', 0) if st.session_state.github_audit else 0}/100"
        })
        with st.expander("Preview Resume Text"):
            st.text(cand["raw_text"])

    with c2:
        st.markdown("### 👥 Hiring Committee & Interview Kit")
        for debate in results.get("agent_debates", []):
            st.markdown(f"**{debate['agent']}** (`{debate['score']}/100`): {debate['opinion']}")
            
        st.markdown("#### ❓ Interview Questions")
        for idx, q in enumerate(results.get("interview_questions", []), 1):
            st.markdown(f"**Q{idx}:** {q}")

# LAYOUT STYLE B: KANBAN PIPELINE VIEW
def render_kanban_layout(cand, results, target_job_title):
    st.title("📋 Candidate Pipeline Kanban Board")
    st.caption("Visual stage-by-stage hiring funnel evaluation.")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown("#### 1. Ingestion Stage")
        st.markdown(f"""
        <div class="card-yes">
            <strong>{cand['name']}</strong><br/>
            <span style="font-size:0.8rem; color:#94a3b8;">Email: {cand.get('email')}</span><br/>
            <span style="font-size:0.8rem; color:#38bdf8;">Status: Ingested & Parsed</span>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown("#### 2. GitHub Proof-of-Work")
        audit = st.session_state.github_audit or {}
        pow_score = audit.get("proof_of_work_score", 0) if audit.get("audited") else 0
        st.markdown(f"""
        <div class="card-{'yes' if pow_score > 50 else 'no'}">
            <strong>PoW Score: {pow_score}/100</strong><br/>
            <span style="font-size:0.8rem;">Repos: {audit.get('public_repos', 0)} | Stars: {audit.get('total_stars', 0)}</span><br/>
            <span style="font-size:0.8rem; color:#a5b4fc;">Langs: {', '.join(audit.get('top_languages', ['N/A']))}</span>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown("#### 3. AI Committee Debate")
        for d in results.get("agent_debates", []):
            st.markdown(f"• **{d['agent']}**: {d['score']}/100")

    with k4:
        st.markdown("#### 4. Final Verdict")
        is_yes = "YES" in results.get("direct_decision", "").upper()
        st.markdown(f"""
        <div class="card-{'yes' if is_yes else 'no'}">
            <span class="badge-{'yes' if is_yes else 'no'}">{results.get('direct_decision')}</span><br/><br/>
            <strong>Score: {results.get('overall_match_score')}/100</strong><br/>
            <span style="font-size:0.8rem;">{results.get('verdict_summary')}</span>
        </div>
        """, unsafe_allow_html=True)

    render_google_meet_module(cand, results, target_job_title)

# LAYOUT STYLE C: COMPACT COMMAND CENTER
def render_command_center_layout(cand, results, target_job_title):
    st.title("⚡ Single-Screen Command Center")
    
    is_yes = "YES" in results.get("direct_decision", "").upper()
    badge_color = "#10b981" if is_yes else "#ef4444"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidate Name", cand["name"])
    m2.metric("Target Role", target_job_title)
    m3.metric("Direct Decision", results.get("direct_decision"))
    m4.metric("Consensus Score", f"{results.get('overall_match_score')}/100")

    render_google_meet_module(cand, results, target_job_title)

    st.divider()
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("🔍 Committee Debates")
        for debate in results.get("agent_debates", []):
            with st.expander(f"{debate['agent']} ({debate['score']}/100)"):
                st.write(debate["opinion"])
    with col_b:
        st.subheader("❓ Interview Questions")
        for q in results.get("interview_questions", []):
            st.markdown(f"• {q}")

if __name__ == "__main__":
    main()
