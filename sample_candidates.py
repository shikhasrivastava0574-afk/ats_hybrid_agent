"""
Sample Candidates Data
Pre-loaded candidate profiles for instant testing of the Hybrid ATS Agent system.
"""

SAMPLE_CANDIDATES = [
    {
        "id": "cand_1",
        "name": "Alex Chen",
        "title": "Senior Full-Stack & AI Engineer",
        "email": "alex.chen.dev@example.com",
        "phone": "+1 (555) 234-5678",
        "github_username": "alexchen-ai",
        "github_url": "https://github.com/alexchen-ai",
        "linkedin_url": "https://linkedin.com/in/alexchen-ai",
        "resume_summary": """
        ALEX CHEN
        Senior Full-Stack & AI Systems Engineer
        Email: alex.chen.dev@example.com | GitHub: https://github.com/alexchen-ai
        
        SUMMARY:
        Software Engineer with 6+ years of experience designing scalable distributed microservices, 
        vector search RAG pipelines, and high-performance Python/TypeScript web applications.
        
        TECHNICAL SKILLS:
        - Languages: Python, TypeScript, Go, SQL, HTML/CSS
        - Frameworks: FastAPI, React, Next.js, Node.js, PyTorch, LangChain
        - Cloud & DevOps: AWS (Lambda, ECS, S3), Kubernetes, Docker, Terraform, GitHub Actions
        - Databases: PostgreSQL, Redis, Pinecone, Qdrant
        
        EXPERIENCE:
        Staff AI Engineer | CloudScale Inc. (2023 - Present)
        - Architected multi-agent LLM orchestration platform processing 2M+ daily requests.
        - Reduced vector search query latency by 42% by tuning hybrid BM25 + dense retrieval embeddings.
        - Led a team of 5 engineers to deliver real-time streaming analytics dashboard.
        
        Senior Backend Engineer | DataPulse Labs (2020 - 2023)
        - Built asynchronous REST & gRPC APIs in FastAPI and Go handling 15k RPS.
        - Spearheaded migration from monolithic Django app to Dockerized Kubernetes microservices.
        
        EDUCATION:
        B.S. in Computer Science | University of California, Berkeley (2020)
        """,
        "mock_github": {
            "audited": True,
            "username": "alexchen-ai",
            "profile_url": "https://github.com/alexchen-ai",
            "public_repos": 18,
            "followers": 45,
            "created_year": "2019",
            "total_stars": 128,
            "total_forks": 34,
            "top_languages": ["Python", "TypeScript", "Go", "Docker"],
            "repo_highlights": [
                {
                    "name": "agentic-rag-framework",
                    "description": "Autonomous multi-agent RAG pipeline with tool usage and streaming evaluation.",
                    "language": "Python",
                    "stars": 82,
                    "url": "https://github.com/alexchen-ai/agentic-rag-framework"
                },
                {
                    "name": "fastapi-k8s-boilerplate",
                    "description": "Production-ready FastAPI baseline template with Prometheus monitoring and Helm charts.",
                    "language": "Go",
                    "stars": 36,
                    "url": "https://github.com/alexchen-ai/fastapi-k8s-boilerplate"
                }
            ],
            "proof_of_work_score": 92,
            "quality_rating": "Verified High Quality Output",
            "fallback_used": False
        }
    },
    {
        "id": "cand_2",
        "name": "Sarah Jenkins",
        "title": "Lead DevOps & Infrastructure Specialist",
        "email": "sarah.j.cloud@example.com",
        "phone": "+1 (555) 987-6543",
        "github_username": "sjenkins-ops",
        "github_url": "https://github.com/sjenkins-ops",
        "linkedin_url": "https://linkedin.com/in/sjenkins-ops",
        "resume_summary": """
        SARAH JENKINS
        DevOps & Cloud Infrastructure Lead
        Email: sarah.j.cloud@example.com | GitHub: https://github.com/sjenkins-ops
        
        SUMMARY:
        Infrastructure Specialist with 7 years of expertise in Kubernetes cluster management, 
        GitOps pipelines, infrastructure-as-code (Terraform), and zero-downtime deployment strategies.
        
        SKILLS:
        Kubernetes, Helm, Terraform, AWS (EKS, VPC, IAM, CloudWatch), Python, Bash, CI/CD, Prometheus, Grafana.
        
        EXPERIENCE:
        Lead DevOps Engineer | FinTech Infrastructure Corp (2021 - Present)
        - Managed multi-region EKS clusters serving 5M active fintech users with 99.99% uptime SLA.
        - Automated zero-trust security compliance scanning across 200+ container images.
        """,
        "mock_github": {
            "audited": True,
            "username": "sjenkins-ops",
            "profile_url": "https://github.com/sjenkins-ops",
            "public_repos": 12,
            "followers": 31,
            "created_year": "2020",
            "total_stars": 64,
            "total_forks": 19,
            "top_languages": ["HCL (Terraform)", "Python", "Shell", "Dockerfile"],
            "repo_highlights": [
                {
                    "name": "terraform-aws-eks-ha",
                    "description": "Highly available multi-AZ EKS cluster deployment modules with cluster autoscaler.",
                    "language": "HCL",
                    "stars": 48,
                    "url": "https://github.com/sjenkins-ops/terraform-aws-eks-ha"
                }
            ],
            "proof_of_work_score": 86,
            "quality_rating": "Verified High Quality Infrastructure",
            "fallback_used": False
        }
    }
]

SAMPLE_JOB_DESCRIPTIONS = {
    "Senior Full-Stack AI Engineer": """
    We are seeking a Senior Full-Stack & AI Systems Engineer to lead the development of our next-generation agentic AI platform.
    
    Key Responsibilities:
    - Design and deploy scalable microservices using Python (FastAPI) and TypeScript.
    - Implement low-latency retrieval pipelines using vector databases and LLM APIs.
    - Maintain automated CI/CD pipelines, Docker containers, and Kubernetes deployments.
    - Collaborate closely with product managers and frontend developers to ship intuitive user experiences.
    
    Requirements:
    - 5+ years of experience in backend development (Python/Go/Node.js).
    - Demonstrated proof-of-work in open-source projects or public GitHub repositories.
    - Experience with vector search, prompt engineering, and multi-agent orchestration frameworks.
    """,
    "DevOps & Infrastructure Lead": """
    We are looking for an experienced DevOps Lead to oversee our AWS Kubernetes infrastructure and CI/CD automation.
    
    Requirements:
    - Expertise in AWS, Terraform, Docker, and Kubernetes (EKS).
    - Strong scripting ability in Python or Bash.
    - Experience maintaining high-availability systems with 99.99% uptime SLAs.
    """,
    "Zinsiehe - Senior Gen AI & Analytics Consultant (5-6 YOE)": """
    Zinsiehe is a premier Gen AI and Analytics consultancy (11-50 employees) helping enterprise clients across Retail, Insurance, Banking, Logistics, Telecom, and Media solve complex business challenges.
    
    Role Focus:
    - Deliver end-to-end Gen AI, LLM, Computer Vision, and Cloud Data Platform solutions (LLMops, MLOps, AIOps, BI, Data Warehousing).
    - Client consultancy & architecture leadership for enterprise clients.
    - Mentoring junior data engineers/AI developers and taking end-to-end project ownership.
    
    Target Requirements (5-6 YOE):
    - 5-6 years experience in Python, LLM frameworks (LangChain/LlamaIndex/OpenAI API), Vector DBs, and Cloud Data Platforms (AWS/Snowflake/Databricks).
    - Strong client communication and problem-solving consulting mindset.
    - Verified GitHub / open-source proof-of-work in AI/ML & data engineering.
    """
}
