"""
Bulk Resume Screening & Automated Ranking Engine
Ingests 50-100 resumes, parses text, audits GitHub proof-of-work, runs multi-agent evaluations,
and populates the candidate database with ranked leaderboards.
Uses ThreadPoolExecutor for high-speed parallel processing.
"""

import io
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf_parser import parse_resume_pdf
from github_auditor import audit_github_profile
from multi_agent_panel import MultiAgentHiringPanel
from db import save_candidate_eval, get_all_candidates

class BulkResumeProcessor:
    def __init__(self):
        self.panel_engine = MultiAgentHiringPanel()

    def _process_single_file(
        self,
        filename: str,
        content_bytes: bytes,
        job_title: str,
        job_description: str
    ) -> Dict[str, Any]:
        """Processes a single PDF resume file."""
        try:
            pdf_stream = io.BytesIO(content_bytes)
            parsed = parse_resume_pdf(pdf_stream)

            if not parsed.get("success"):
                return {"success": False, "filename": filename, "error": parsed.get("error")}

            c_info = parsed.get("contact_info", {})
            cand_data = {
                "name": parsed.get("candidate_name") or filename.replace(".pdf", ""),
                "email": c_info.get("email"),
                "phone": c_info.get("phone"),
                "github_username": c_info.get("github_username"),
                "raw_text": parsed.get("raw_text")
            }

            # Audit GitHub
            gh_username = cand_data.get("github_username")
            github_audit = {}
            if gh_username:
                github_audit = audit_github_profile(gh_username)

            # Run Multi-Agent Evaluation
            results = self.panel_engine.run_panel_debate(
                candidate_name=cand_data["name"],
                resume_text=cand_data["raw_text"],
                job_title=job_title,
                job_description=job_description,
                github_audit=github_audit
            )
            results["github_audit"] = github_audit

            # Save Candidate Record to Database
            cand_id = save_candidate_eval(cand_data, results)

            return {
                "success": True,
                "id": cand_id,
                "filename": filename,
                "name": cand_data["name"],
                "email": cand_data["email"],
                "github_username": gh_username,
                "overall_match_score": results.get("overall_match_score", 0),
                "proof_of_work_score": github_audit.get("proof_of_work_score", 0) if github_audit.get("audited") else 0,
                "direct_decision": results.get("direct_decision"),
                "verdict_summary": results.get("verdict_summary")
            }
        except Exception as e:
            return {"success": False, "filename": filename, "error": str(e)}

    def process_bulk_resumes(
        self,
        file_tuples: List[tuple],  # [(filename, bytes_content), ...]
        job_title: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Processes a batch of resume PDFs concurrently using ThreadPoolExecutor.
        Returns a ranked summary of all evaluated candidates.
        """
        processed_candidates = []
        errors = []

        max_workers = min(12, max(2, len(file_tuples)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, fname, content, job_title, job_description): fname
                for fname, content in file_tuples
            }

            for future in as_completed(future_to_file):
                fname = future_to_file[future]
                try:
                    res = future.result()
                    if res.get("success"):
                        processed_candidates.append(res)
                    else:
                        errors.append({"filename": fname, "error": res.get("error")})
                except Exception as e:
                    errors.append({"filename": fname, "error": str(e)})

        # Sort candidates by overall match score (Ranked Leaderboard)
        processed_candidates.sort(key=lambda c: c["overall_match_score"], reverse=True)

        return {
            "total_processed": len(processed_candidates),
            "total_errors": len(errors),
            "leaderboard": processed_candidates,
            "errors": errors
        }

if __name__ == "__main__":
    print("BulkResumeProcessor module ready with multi-threading.")
