"""
Hybrid ATS Agent - Modern Glassmorphism Dashboard Layout
Comprehensive AI Recruitment Platform with Proof-of-Work GitHub Auditing & Multi-Agent Hiring Board.
"""

import os
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Zinsiehe ATS Agent | AI Hiring Board",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from pdf_parser import parse_resume_pdf, extract_urls_and_contact
from github_auditor import audit_github_profile
from multi_agent_panel import MultiAgentHiringPanel
from sample_candidates import SAMPLE_CANDIDATES, SAMPLE_JOB_DESCRIPTIONS

# Custom Modern Executive CSS Styling
st.markdown("""
<style>
    /* Dark Glassmorphism Theme */
    .stApp {
        background: #0f172a;
        color: #f8fafc;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .decision-banner-yes {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.25) 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }
    .decision-banner-no {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.25) 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
    }
    .agent-pill {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .stat-badge {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Top Executive Navbar
    nav_col1, nav_col2 = st.columns([3, 1])
    with nav_col1:
        st.markdown('<div class="main-title">Zinsiehe AI Recruitment Platform</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94a3b8; font-size: 0.95rem; margin-top: -4px;">Proof-of-Work Code Auditor & Multi-Agent Hiring Committee (5-6 YOE Evaluation Engine)</p>', unsafe_allow_html=True)
    with nav_col2:
        st.markdown('<div style="text-align: right; margin-top: 10px;"><span class="agent-pill">🟢 Multi-Agent Panel Active</span></div>', unsafe_allow_html=True)

    st.divider()

    # Session State Setup
    if "current_candidate" not in st.session_state:
        st.session_state.current_candidate = None
    if "github_audit" not in st.session_state:
        st.session_state.github_audit = None
    if "panel_results" not in st.session_state:
        st.session_state.panel_results = None

    # Control Bar Card: Candidate Input & Target Role Selection
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        
        with c1:
            job_choice = st.selectbox(
                "🎯 Select Target Job Role:",
                list(SAMPLE_JOB_DESCRIPTIONS.keys()),
                index=len(SAMPLE_JOB_DESCRIPTIONS)-1 if "Zinsiehe" in list(SAMPLE_JOB_DESCRIPTIONS.keys())[-1] else 0
            )
            target_job_title = job_choice
            target_job_desc = SAMPLE_JOB_DESCRIPTIONS[job_choice]

        with c2:
            upload_pdf = st.file_uploader("📄 Upload Candidate PDF Resume:", type=["pdf"])
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

        with c3:
            st.markdown("<br/>", unsafe_allow_html=True)
            sample_select = st.selectbox(
                "Or Test Sample:",
                range(len(SAMPLE_CANDIDATES)),
                format_func=lambda i: SAMPLE_CANDIDATES[i]["name"]
            )
            if st.button("Load Sample Candidate", use_container_width=True):
                sample = SAMPLE_CANDIDATES[sample_select]
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
                
        st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.current_candidate:
        st.info("👆 Please select a target job role and load or upload a candidate resume to begin.")
        return

    cand = st.session_state.current_candidate
    gh_username = cand.get("github_username")

    # Run GitHub Audit automatically if username present
    if not st.session_state.github_audit and gh_username:
        st.session_state.github_audit = audit_github_profile(gh_username)

    # Trigger Multi-Agent Panel Debate
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
    is_yes = "YES" in results.get("direct_decision", "").upper()

    # Executive Verdict Banner Card (Top Center)
    banner_class = "decision-banner-yes" if is_yes else "decision-banner-no"
    decision_badge = "#10b981" if is_yes else "#ef4444"
    icon_symbol = "✅" if is_yes else "❌"

    st.markdown(f"""
    <div class="{banner_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <span style="background-color: {decision_badge}; color: white; padding: 6px 18px; border-radius: 20px; font-weight: 800; font-size: 1.05rem;">
                    {icon_symbol} DIRECT DECISION: {results.get('direct_decision', 'PENDING')}
                </span>
                <h2 style="margin-top: 14px; margin-bottom: 2px; font-size: 2.0rem; font-weight: 800; color: #f8fafc;">
                    Candidate: {cand['name']}
                </h2>
                <p style="color: #cbd5e1; font-size: 0.95rem; margin: 0;">Target Role: <strong>{target_job_title}</strong></p>
            </div>
            <div style="text-align: right; background: rgba(0,0,0,0.2); padding: 14px 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                <span style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Consensus Match Score</span>
                <div style="font-size: 3.4rem; font-weight: 900; color: {decision_badge}; line-height: 1;">
                    {results.get('overall_match_score', 0)}<span style="font-size: 1.2rem; color: #94a3b8;">/100</span>
                </div>
            </div>
        </div>
        <hr style="border-top: 1px solid rgba(255,255,255,0.15); margin: 16px 0;"/>
        <p style="font-size: 1.0rem; color: #f1f5f9; margin: 0; line-height: 1.5;">
            <strong>Panel Chair Verdict Summary:</strong> {results.get('verdict_summary')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # MAIN SPLIT GRID LAYOUT (Left Column: Candidate & GitHub Audit | Right Column: 3 Agents & Interview Kit)
    col_left, col_right = st.columns([1, 1], gap="large")

    # LEFT COLUMN: Candidate Intelligence & Proof-of-Work
    with col_left:
        st.markdown("### 👤 Candidate & Proof-of-Work Profile")
        
        # Candidate Info Card
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Candidate Details")
            mc1, mc2 = st.columns(2)
            mc1.markdown(f"**Email:** `{cand.get('email', 'N/A')}`")
            mc1.markdown(f"**GitHub Username:** `@`**{cand.get('github_username') or 'Not Found'}**")
            mc2.markdown(f"**Source:** {cand.get('source')}")
            mc2.markdown(f"**Target Role:** {target_job_title}")
            
            with st.expander("📄 View Parsed Resume Text"):
                st.text(cand["raw_text"])
            st.markdown('</div>', unsafe_allow_html=True)

        # GitHub Audit Card
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 💻 GitHub Proof-of-Work Code Audit")
            
            audit = st.session_state.github_audit or {}
            
            if audit.get("audited"):
                s1, s2, s3, s4 = st.columns(4)
                s1.markdown(f'<div class="stat-badge"><span style="font-size:0.75rem; color:#94a3b8;">PoW Score</span><br/><strong style="font-size:1.2rem; color:#38bdf8;">{audit.get("proof_of_work_score", 0)}/100</strong></div>', unsafe_allow_html=True)
                s2.markdown(f'<div class="stat-badge"><span style="font-size:0.75rem; color:#94a3b8;">Public Repos</span><br/><strong style="font-size:1.2rem;">{audit.get("public_repos", 0)}</strong></div>', unsafe_allow_html=True)
                s3.markdown(f'<div class="stat-badge"><span style="font-size:0.75rem; color:#94a3b8;">Stars ⭐</span><br/><strong style="font-size:1.2rem;">{audit.get("total_stars", 0)}</strong></div>', unsafe_allow_html=True)
                s4.markdown(f'<div class="stat-badge"><span style="font-size:0.75rem; color:#94a3b8;">Followers</span><br/><strong style="font-size:1.2rem;">{audit.get("followers", 0)}</strong></div>', unsafe_allow_html=True)
                
                st.markdown("<br/>", unsafe_allow_html=True)
                st.markdown("**Top Verified Programming Languages:**")
                langs = audit.get("top_languages", [])
                if langs:
                    st.write(", ".join([f"`{l}`" for l in langs]))
                else:
                    st.caption("No languages extracted.")
                    
                st.markdown("<br/>", unsafe_allow_html=True)
                st.markdown("**Repository Highlights:**")
                for repo in audit.get("repo_highlights", []):
                    st.markdown(f"• **{repo['name']}** ({repo['language']}) — ⭐ {repo['stars']} stars<br/><span style='font-size:0.85rem; color:#94a3b8;'>{repo['description']}</span>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No GitHub handle verified. Proof-of-Work Score evaluated at 0/100.")
                
            st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT COLUMN: Multi-Agent Hiring Board Debate & Interview Questions
    with col_right:
        st.markdown("### 👥 Autonomous Hiring Committee & Interview Kit")

        # 3 AI Agent Debate Cards
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Autonomous Hiring Committee Opinions")
            
            for debate in results.get("agent_debates", []):
                score = debate['score']
                score_color = "#10b981" if score >= 70 else ("#f59e0b" if score >= 50 else "#ef4444")
                
                st.markdown(f"""
                <div style="border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 14px; margin-bottom: 12px; background: rgba(15, 23, 42, 0.5);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 1.0rem; color: #f8fafc;">{debate['agent']}</span>
                        <span style="font-weight: 800; color: {score_color}; font-size: 1.05rem;">Score: {score}/100</span>
                    </div>
                    <p style="font-size: 0.9rem; color: #cbd5e1; margin-top: 6px; margin-bottom: 0;">"{debate['opinion']}"</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)

        # Key Strengths & Areas to Probe Card
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Key Strengths & Areas to Probe")
            
            k1, k2 = st.columns(2)
            with k1:
                st.markdown("##### 🌟 Key Strengths")
                for s in results.get("chair_synthesis", {}).get("key_strengths", []):
                    st.markdown(f"• {s}")
            with k2:
                st.markdown("##### 🔍 Areas to Probe")
                for p in results.get("chair_synthesis", {}).get("areas_to_probe", []):
                    st.markdown(f"⚠️ {p}")
                    
            st.markdown('</div>', unsafe_allow_html=True)

        # Custom Interview Questions Card
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### ❓ Custom Generated Interview Questions")
            for idx, q in enumerate(results.get("interview_questions", []), 1):
                st.markdown(f"**Q{idx}:** {q}")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
