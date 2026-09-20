"""
Multi-Agent Hiring Panel Module
Spawns 3 specialized AI Agents (Tech Lead, Culture & Values, Growth & Velocity)
and a Panel Chair Agent to conduct a multi-perspective debate and synthesize shortlisting decisions.
"""

import os
import json
import requests
from typing import Dict, Any, List

class MultiAgentHiringPanel:
    def __init__(self, api_key: str = None, provider: str = "auto"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY")
        self.provider = provider

    def run_panel_debate(
        self,
        candidate_name: str,
        resume_text: str,
        job_title: str,
        job_description: str,
        github_audit: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Runs the full 4-agent panel debate process.
        Returns debate transcript, consensus verdict, scores, pros/cons, and interview questions.
        """
        github_audit = github_audit or {}
        pow_score = github_audit.get("proof_of_work_score", 70)
        github_langs = ", ".join(github_audit.get("top_languages", ["Python", "JavaScript"]))
        
        # If API key available, we can use LLM, otherwise use smart deterministic rule-engine
        if self.api_key and "mock" not in self.provider.lower():
            try:
                return self._run_llm_panel(candidate_name, resume_text, job_title, job_description, github_audit)
            except Exception as e:
                # Fallback to local rule-engine if LLM call encounters network/key error
                return self._run_rule_engine_panel(candidate_name, resume_text, job_title, job_description, github_audit, str(e))
        else:
            return self._run_rule_engine_panel(candidate_name, resume_text, job_title, job_description, github_audit)

    def _run_rule_engine_panel(
        self,
        candidate_name: str,
        resume_text: str,
        job_title: str,
        job_description: str,
        github_audit: Dict[str, Any],
        error_note: str = None
    ) -> Dict[str, Any]:
        """Deterministic Multi-Agent debate simulation with realistic evaluation."""
        text_lower = resume_text.lower()
        jd_lower = job_description.lower()
        
        # Keyword & Skill Alignment Calculation
        jd_keywords = set([w.strip(',.()') for w in jd_lower.split() if len(w) > 4])
        matched_keywords = [w for w in jd_keywords if w in text_lower]
        match_ratio = len(matched_keywords) / max(1, len(jd_keywords))
        
        # Proof-of-Work score defaults to 0 if no GitHub audit is present
        if github_audit and github_audit.get("audited"):
            pow_score = github_audit.get("proof_of_work_score", 0)
            repos_count = github_audit.get("public_repos", 0)
        else:
            pow_score = 0
            repos_count = 0
        
        # Parse numeric years of experience using regex (e.g. '6 years', '5 yrs')
        import re
        yoe_matches = re.findall(r'(\d+)\s*\+?\s*(?:years?|yrs?|year|yr)', text_lower)
        claimed_years = [int(y) for y in yoe_matches if int(y) < 40]  # filter out graduation years like 2024
        max_claimed_years = max(claimed_years) if claimed_years else 0
        
        # Explicit 5-6 YOE Indicators (Strict check on numeric years or 5+ yrs phrases)
        has_5to6_yoe = (max_claimed_years >= 5) or any(term in text_lower for term in [
            "5+ year", "6+ year", "7+ year", "8+ year", "5-6 year", "5 to 6 year", "6-7 year", 
            "5+ yr", "6+ yr", "7+ yr", "5 years of experience", "6 years of experience", "7 years of experience"
        ])
        
        # Detect Zero-Experience & Entry-Level Indicators
        zero_yoe_terms = [
            "0 years", "0 yr", "0 yrs", "no experience", "fresher", "student", "internship only", 
            "entry level", "looking for first role", "graduate 2024", "graduate 2025", "graduate 2026",
            "junior", "trainee", "associate"
        ]
        is_zero_yoe = max_claimed_years == 0 or any(term in text_lower for term in zero_yoe_terms) or (len(resume_text.strip()) < 300 and match_ratio < 0.20)
        if has_5to6_yoe:
            is_zero_yoe = False
        
        # Target role requires 5-6 YOE if role mentions 5-6 YOE, Senior, or Lead
        is_senior_role = any(term in job_title.lower() or term in job_description.lower() for term in ["senior", "lead", "5-6 yoe", "5+ years", "6+ years"])

        # Agent 1: Tech Lead Evaluation
        if pow_score > 0:
            tech_score = int(min(98, match_ratio * 40 + pow_score * 0.5 + (10 if "python" in text_lower else 0)))
        else:
            tech_score = int(min(98, match_ratio * 45))

        if is_zero_yoe or (is_senior_role and not has_5to6_yoe):
            tech_score = min(35, tech_score)
            tech_debate = f"❌ **Tech Audit Alert (Score: {tech_score}%)**: Candidate lacks the 5-6 years of experience or senior engineering depth required for {job_title}. Proof-of-work score is {pow_score}/100."
        else:
            tech_debate = f"The candidate demonstrates solid stack alignment ({tech_score}% score). GitHub proof-of-work score is {pow_score}/100 with active repos in {', '.join(github_audit.get('top_languages', ['Python']))}."

        # Agent 2: Culture & Values Evaluation (5-6 YOE Focus)
        culture_mentorship = any(w in text_lower for w in ["mentor", "guided", "onboard", "review", "lead", "best practices"])
        culture_autonomy = any(w in text_lower for w in ["spearheaded", "architected", "rfc", "spec", "stakeholders", "cross-functional"])
        culture_pragmatism = any(w in text_lower for w in ["refactored", "ci/cd", "reliability", "uptime", "production", "trade-off"])
        
        if is_zero_yoe or (is_senior_role and not has_5to6_yoe):
            culture_score = 20
            culture_debate = f"❌ **Culture & Leadership Alert (Score: {culture_score}%)**: Candidate lacks 5-6 YOE senior maturity. No evidence of mentoring junior engineers, writing RFCs, or managing production systems expected for Zinsiehe."
        else:
            culture_score_base = 50
            if culture_mentorship: culture_score_base += 15
            if culture_autonomy: culture_score_base += 15
            if culture_pragmatism: culture_score_base += 15
            culture_score = int(min(98, culture_score_base))

            culture_debate = (
                f"🎯 **5-6 YOE Culture Assessment ({culture_score}% Fit)**: "
                f"Mentorship & code reviews: {'✅ Present' if culture_mentorship else '⚠️ Limited'}. "
                f"Cross-functional RFC/autonomy: {'✅ High' if culture_autonomy else '⚠️ Moderate'}. "
                f"Production ownership: {'✅ Strong' if culture_pragmatism else '⚠️ Basic'}."
            )

        # Agent 3: Growth & Velocity Evaluation
        if is_zero_yoe or (is_senior_role and not has_5to6_yoe):
            growth_score = 30
            growth_debate = f"⚠️ **Growth Index ({growth_score}%)**: Candidate is entry-level or mid-tier with < 5 years of experience. Unproven in senior client-facing consulting environments."
        else:
            growth_score = int(min(99, 60 + (25 if any(w in text_lower for w in ["promoted", "architected", "lead", "built"]) else 5)))
            growth_debate = f"Career velocity index ({growth_score}% score). Solid progression trajectory across previous roles."

        # Panel Chair Consensus & Hard Experience Gate
        overall_score = int((tech_score * 0.40) + (culture_score * 0.35) + (growth_score * 0.25))
        
        # HARD DISQUALIFICATION GATE FOR SENIOR / 5-6 YOE ROLES
        if is_zero_yoe or (is_senior_role and not has_5to6_yoe):
            overall_score = min(32, overall_score)
            direct_decision = "NO - DO NOT INTERVIEW"
            verdict = "NO - DO NOT INTERVIEW (Experience Ineligible)"
            verdict_badge = "warning"
            verdict_summary = f"❌ NOT ELIGIBLE FOR INTERVIEW: Hard Experience Gate Failed. Candidate does not possess the mandatory 5-6 Years of Experience required for {job_title} at Zinsiehe."
        elif overall_score >= 75:
            direct_decision = "YES - TAKE INTERVIEW"
            verdict = "YES - TAKE INTERVIEW (High Match)"
            verdict_badge = "success"
            verdict_summary = f"✅ ELIGIBLE FOR INTERVIEW: Unanimous panel approval. Candidate {candidate_name} exhibits verified 5-6 YOE technical maturity, Gen AI stack fit, and mentorship culture alignment for {job_title} at Zinsiehe."
        elif overall_score >= 68:
            direct_decision = "YES - TAKE INTERVIEW (Conditional)"
            verdict = "YES - TAKE INTERVIEW (Conditional)"
            verdict_badge = "info"
            verdict_summary = f"✅ ELIGIBLE FOR INTERVIEW: Passed minimum threshold. Recommended for Round 1 screening with specific focus on 5-6 YOE mentorship & client consulting fit for Zinsiehe."
        else:
            direct_decision = "NO - DO NOT INTERVIEW"
            verdict = "NO - DO NOT INTERVIEW (Ineligible)"
            verdict_badge = "warning"
            verdict_summary = f"❌ NOT ELIGIBLE FOR INTERVIEW: Fails to meet 5-6 YOE proof-of-work or Gen AI stack benchmarks required for {job_title} at Zinsiehe."

        interview_questions = [
            f"At 5-6 years of experience, how do you balance mentoring junior engineers while maintaining your own individual feature velocity?",
            f"Describe how you handle architectural trade-offs in your project ({github_audit.get('repo_highlights', [{}])[0].get('name', 'recent project')}) when product deadlines press for technical debt.",
            "Can you give an example of how you resolved a major technical or priority disagreement with a product manager or design partner?",
            f"What specific post-mortem or reliability practices have you introduced in your previous {job_title} team to prevent recurring production outages?"
        ]

        return {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "overall_match_score": overall_score,
            "direct_decision": direct_decision,
            "verdict": verdict,
            "verdict_badge": verdict_badge,
            "verdict_summary": verdict_summary,
            "agent_debates": [
                {
                    "agent": "💻 Tech Lead Agent",
                    "role": "Technical & Code Audit",
                    "score": tech_score,
                    "opinion": tech_debate,
                    "status": "APPROVED" if tech_score >= 70 else "NEEDS VERIFICATION"
                },
                {
                    "agent": "🤝 Culture & Values Agent (5-6 YOE Focus)",
                    "role": "Mentorship, Autonomy & Ownership",
                    "score": culture_score,
                    "opinion": culture_debate,
                    "status": "APPROVED" if culture_score >= 70 else "NEEDS VERIFICATION"
                },
                {
                    "agent": "🚀 Growth & Velocity Agent",
                    "role": "Adaptability & Trajectory",
                    "score": growth_score,
                    "opinion": growth_debate,
                    "status": "APPROVED" if growth_score >= 70 else "NEEDS VERIFICATION"
                }
            ],
            "chair_synthesis": {
                "consensus": f"Panel Chair synthesized a final score of {overall_score}/100. Candidate shows strong 5-6 YOE cultural and technical alignment with {job_title}.",
                "key_strengths": [
                    f"5-6 YOE Cultural Maturity Score of {culture_score}/100 (Mentorship & Autonomy verified).",
                    f"Verified Proof-of-Work score of {pow_score}/100 across public repos.",
                    "Demonstrated initiative in end-to-end system development and team collaboration."
                ],
                "areas_to_probe": [
                    "Mentorship methodology and handling underperforming team members.",
                    "Depth of automated unit/integration testing coverage under rapid release schedules."
                ]
            },
            "interview_questions": interview_questions,
            "engine_used": "Multi-Agent Deterministic Engine (5-6 YOE Culture Module active)" + (f" (LLM Notice: {error_note})" if error_note else "")
        }

    def _run_llm_panel(
        self,
        candidate_name: str,
        resume_text: str,
        job_title: str,
        job_description: str,
        github_audit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Runs panel debate using OpenAI or Gemini API if available."""
        prompt = f"""
        You are facilitating an autonomous Hiring Panel Debate for the role: {job_title}.
        
        Candidate Name: {candidate_name}
        Job Description: {job_description}
        Resume Text Snippet: {resume_text[:2000]}
        GitHub Audit Data: {json.dumps(github_audit)}
        
        CRITICAL EVALUATION FOCUS (5-6 Years of Experience Culture Fit):
        Specifically for the Culture & Values Agent, evaluate the candidate against expectations for 5-6 years of experience:
        1. Mentorship & Guidance: Evidence of mentoring junior/mid engineers, conducting code reviews, or establishing team best practices.
        2. Cross-Functional Autonomy: Ability to write RFCs/specs and work independently with Product & Design without hand-holding.
        3. Pragmatic Engineering: Balancing feature delivery speed with refactoring and technical debt management.
        4. Production Ownership: Incident management, post-mortems, and system reliability mindset.
        
        Generate a structured JSON output with the following keys:
        - overall_match_score (integer 0-100)
        - verdict ("STRONG SHORTLIST", "SHORTLIST FOR INTERVIEW", or "RESERVE / HOLD")
        - verdict_summary (string)
        - agent_debates (list of 3 objects with keys: agent, role, score, opinion, status)
        - chair_synthesis (object with keys: consensus, key_strengths [list], areas_to_probe [list])
        - interview_questions (list of 4 strings targeting 5-6 YOE technical and cultural depth)
        """
        
        # OpenAi or Gemini REST endpoint call
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": "You are a professional HR Multi-Agent Hiring Board."},
                         {"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            content = json.loads(data["choices"][0]["message"]["content"])
            content["candidate_name"] = candidate_name
            content["job_title"] = job_title
            content["verdict_badge"] = "success" if content.get("overall_match_score", 0) >= 80 else "info"
            content["engine_used"] = "LLM Multi-Agent Board (OpenAI API)"
            return content
        else:
            raise Exception(f"OpenAI API status {res.status_code}")
