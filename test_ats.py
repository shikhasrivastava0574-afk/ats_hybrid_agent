"""
Automated Test Suite for ATS Hybrid Agent
"""
import unittest
from pdf_parser import extract_urls_and_contact
from github_auditor import audit_github_profile
from multi_agent_panel import MultiAgentHiringPanel
from sample_candidates import SAMPLE_CANDIDATES, SAMPLE_JOB_DESCRIPTIONS

class TestATSHybridAgent(unittest.TestCase):
    def test_contact_and_url_extraction(self):
        text = """
        John Smith
        Email: john.smith@example.org | Phone: +1 555-999-1234
        GitHub Profile: https://github.com/johnsmith-code
        LinkedIn: https://linkedin.com/in/johnsmith-code
        """
        extracted = extract_urls_and_contact(text)
        self.assertEqual(extracted["email"], "john.smith@example.org")
        self.assertEqual(extracted["github_username"], "johnsmith-code")
        self.assertEqual(extracted["linkedin_url"], "https://linkedin.com/in/johnsmith-code")

    def test_github_audit_fallback(self):
        audit = audit_github_profile("nonexistent-test-user-12345")
        self.assertTrue(audit["audited"])
        self.assertGreater(audit["proof_of_work_score"], 0)

    def test_multi_agent_panel_debate(self):
        sample = SAMPLE_CANDIDATES[0]
        job_title = "Senior Full-Stack AI Engineer"
        job_desc = SAMPLE_JOB_DESCRIPTIONS[job_title]
        
        panel = MultiAgentHiringPanel()
        res = panel.run_panel_debate(
            candidate_name=sample["name"],
            resume_text=sample["resume_summary"],
            job_title=job_title,
            job_description=job_desc,
            github_audit=sample["mock_github"]
        )
        
        self.assertEqual(res["candidate_name"], sample["name"])
        self.assertEqual(len(res["agent_debates"]), 3)
        self.assertGreater(res["overall_match_score"], 50)
        self.assertIn("verdict", res)
        self.assertGreater(len(res["interview_questions"]), 0)

    def test_5_to_6_yoe_culture_fit(self):
        resume_5yoe = """
        Alex Chen - 6 years experience
        Lead Engineer at TechCorp. Mentored 4 junior developers and led weekly code reviews.
        Spearheaded RFC proposals and cross-functional alignment with Product managers.
        Maintained production uptime and refactored core API pipeline to balance technical debt.
        """
        panel = MultiAgentHiringPanel()
        res = panel.run_panel_debate(
            candidate_name="Alex Chen",
            resume_text=resume_5yoe,
            job_title="Senior Engineer (6 YOE)",
            job_description="Seeking engineer with 6 years experience.",
            github_audit={"proof_of_work_score": 85}
        )
        culture_agent = [a for a in res["agent_debates"] if "Culture" in a["agent"]][0]
        self.assertGreaterEqual(culture_agent["score"], 80)
        self.assertIn("Mentorship", culture_agent["opinion"])

    def test_google_meet_scheduler(self):
        from google_meet_scheduler import generate_google_calendar_url
        res = generate_google_calendar_url(
            candidate_name="Alex Chen",
            candidate_email="alex.chen@example.com",
            job_title="Senior Gen AI Engineer"
        )
        self.assertIn("calendar.google.com", res["gcal_url"])
        self.assertIn("meet.google.com", res["google_meet_link"])
        self.assertEqual(res["candidate_email"], "alex.chen@example.com")


if __name__ == "__main__":
    unittest.main()
