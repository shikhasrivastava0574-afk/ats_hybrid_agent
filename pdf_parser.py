"""
Resume PDF Parser Module
Extracts plain text, contact details, embedded links (GitHub, LinkedIn, Portfolios),
and structured information from candidate resume PDFs.
"""

import re
import pypdf
from typing import Dict, Any, List

def extract_urls_and_contact(text: str, pdf_reader: pypdf.PdfReader = None) -> Dict[str, Any]:
    """Extract emails, phone numbers, GitHub links, LinkedIn links, and general URLs."""
    # Email regex
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    
    # Phone regex
    phones = re.findall(r'\(?\+?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{0,4}', text)
    phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10]

    # GitHub regex
    github_links = re.findall(r'https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?', text, re.IGNORECASE)
    github_handles = re.findall(r'github\.com/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    
    # LinkedIn regex
    linkedin_links = re.findall(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?', text, re.IGNORECASE)
    
    # Portfolio / Web links regex
    all_urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    
    # Check PDF annotations for clickable hyperlinks if pdf_reader is provided
    if pdf_reader:
        try:
            for page in pdf_reader.pages:
                if '/Annots' in page:
                    for annot in page['/Annots']:
                        obj = annot.get_object()
                        if '/A' in obj and '/URI' in obj['/A']:
                            uri = obj['/A']['/URI']
                            all_urls.append(uri)
                            if 'github.com' in uri.lower():
                                github_links.append(uri)
                                match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', uri, re.IGNORECASE)
                                if match:
                                    github_handles.append(match.group(1))
                            elif 'linkedin.com' in uri.lower():
                                linkedin_links.append(uri)
        except Exception:
            pass

    # Clean and deduplicate lists
    github_links = list(dict.fromkeys(github_links))
    github_handles = list(dict.fromkeys(github_handles))
    linkedin_links = list(dict.fromkeys(linkedin_links))
    all_urls = list(dict.fromkeys(all_urls))
    
    # Filter out common false positives for github handles
    reserved_github_words = {'site', 'org', 'features', 'pricing', 'about', 'join', 'login', 'signup', 'settings'}
    github_handles = [h for h in github_handles if h.lower() not in reserved_github_words]

    primary_github = github_links[0] if github_links else (f"https://github.com/{github_handles[0]}" if github_handles else None)
    github_username = github_handles[0] if github_handles else (re.search(r'github\.com/([a-zA-Z0-9_-]+)', primary_github).group(1) if primary_github and 'github.com/' in primary_github else None)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "github_url": primary_github,
        "github_username": github_username,
        "linkedin_url": linkedin_links[0] if linkedin_links else None,
        "all_urls": all_urls
    }

def parse_resume_pdf(pdf_file_source) -> Dict[str, Any]:
    """
    Parses a PDF file (path or file-like object / BytesIO).
    Returns raw text, extracted contact info, and detected URLs.
    """
    try:
        reader = pypdf.PdfReader(pdf_file_source)
        text_pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_pages.append(t)
        
        full_text = "\n\n".join(text_pages)
        contact_info = extract_urls_and_contact(full_text, reader)
        
        # Estimate candidate name from first few lines if possible
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        candidate_name = lines[0] if lines else "Candidate"
        if len(candidate_name.split()) > 4 or "@" in candidate_name or "http" in candidate_name:
            candidate_name = "Candidate"
            
        return {
            "success": True,
            "candidate_name": candidate_name,
            "raw_text": full_text,
            "page_count": len(reader.pages),
            "contact_info": contact_info,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "candidate_name": "Candidate",
            "raw_text": "",
            "page_count": 0,
            "contact_info": {},
            "error": str(e)
        }

if __name__ == "__main__":
    # Self-test
    sample_text = """
    Jane Doe
    Senior Software Engineer
    Email: jane.doe@example.com | Phone: +1 555-019-2831
    GitHub: https://github.com/janedoe-dev
    LinkedIn: https://linkedin.com/in/janedoe-dev
    
    Experience:
    - Built high-throughput microservices using Go and Python.
    - Managed Kubernetes clusters and Terraform infrastructure.
    """
    res = extract_urls_and_contact(sample_text)
    print("Parsed Contact Info:", res)
