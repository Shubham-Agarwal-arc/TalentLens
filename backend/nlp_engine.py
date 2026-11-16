import io
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
from pypdf import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer

# Load lightweight, high-accuracy semantic embedding model (384-dim)
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# Curated canonical skill taxonomy & alias normalization map
SKILL_ALIASES: Dict[str, str] = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "c++": "C++",
    "c#": "C#",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "angular": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "sqlite": "SQLite",
    "oracle": "Oracle DB",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "ci/cd": "CI/CD",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "terraform": "Terraform",
    "git": "Git",
    "linux": "Linux",
    "rest api": "REST APIs",
    "restful": "REST APIs",
    "graphql": "GraphQL",
    "microservices": "Microservices",
    "kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "spacy": "spaCy",
    "langchain": "LangChain",
    "llm": "LLMs",
    "rag": "RAG",
    "html": "HTML5",
    "css": "CSS3",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "agile": "Agile/Scrum",
    "scrum": "Agile/Scrum",
    "jira": "Jira",
    "system design": "System Design",
    "unit testing": "Unit Testing",
    "pytest": "Pytest",
    "junit": "JUnit",
}

CANONICAL_SKILLS = sorted(list(set(SKILL_ALIASES.values())))
SKILL_EMBEDDINGS = model.encode(CANONICAL_SKILLS, normalize_embeddings=True)
SKILL_TO_VEC = {skill: emb for skill, emb in zip(CANONICAL_SKILLS, SKILL_EMBEDDINGS)}


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    lower_name = filename.lower()
    text_chunks: List[str] = []

    if lower_name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_chunks.append(extracted)
    elif lower_name.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            if para.text.strip():
                text_chunks.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_chunks.append(row_text)
    elif lower_name.endswith(".txt"):
        text_chunks.append(file_bytes.decode("utf-8", errors="ignore"))
    else:
        raise ValueError(f"Unsupported file format: {filename}")

    raw_text = "\n".join(text_chunks)
    return re.sub(r"[ \t]+", " ", raw_text).strip()


def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found = set()
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(alias) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(canonical)
    return sorted(list(found))


def extract_experience_years(text: str, is_jd: bool = False) -> float:
    text_lower = text.lower()
    explicit_matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+relevant|\s+work|\s+industry|\s+software|\s+experience)?",
        text_lower,
    )
    explicit_vals = [float(x) for x in explicit_matches if 0 < float(x) <= 35]

    if is_jd:
        return max(explicit_vals) if explicit_vals else 0.0

    # Also compute date-range experience, including month ranges such as
    # "Jan 2026 - Apr 2026" and year-only ranges such as "2020 - Present".
    current_year = datetime.now().year
    month_names = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?"
    )
    month_numbers = {
        "jan": 1, "january": 1, "feb": 2, "february": 2,
        "mar": 3, "march": 3, "apr": 4, "april": 4, "may": 5,
        "jun": 6, "june": 6, "jul": 7, "july": 7, "aug": 8,
        "august": 8, "sep": 9, "september": 9, "oct": 10,
        "october": 10, "nov": 11, "november": 11, "dec": 12,
        "december": 12,
    }
    date_ranges = re.findall(
        rf"(?:(?P<start_month>{month_names})\s+)?(?P<start_year>20\d{{2}})"
        rf"\s*[-–—to]+\s*"
        rf"(?:(?P<end_month>{month_names})\s+)?"
        rf"(?P<end_year>20\d{{2}}|present|current|now)",
        text_lower,
    )
    range_years = 0.0
    for start_month, start_str, end_month, end_str in date_ranges:
        start_y = int(start_str)
        end_y = current_year if end_str in {"present", "current", "now"} else int(end_str)
        if 2000 <= start_y <= end_y <= current_year:
            start_m = month_numbers.get(start_month, 1)
            end_m = month_numbers.get(end_month, datetime.now().month if end_str in {"present", "current", "now"} else 12)
            months = ((end_y - start_y) * 12) + (end_m - start_m)
            range_years += max(0.25, round(months / 12, 2))

    candidates = explicit_vals + ([round(range_years, 1)] if range_years > 0 else [])
    return max(candidates) if candidates else 0.0


def extract_education(text: str) -> str:
    edu_patterns = [
        r"(Ph\.?D\.?|Doctorate)[^\n,]*",
        r"(M\.?Tech|M\.?S\.?|Master(?:'s)?(?:\s+of\s+[A-Za-z\s]+)?)[^\n,]*",
        r"(B\.?Tech|B\.?E\.?|B\.?S\.?|B\.?Sc\.?|Bachelor(?:'s)?(?:\s+of\s+[A-Za-z\s]+)?)[^\n,]*",
        r"(MBA|MCA|BCA)[^\n,]*",
    ]
    found_degrees = []
    for pat in edu_patterns:
        match = re.search(pat, text, flags=re.IGNORECASE)
        if match:
            cleaned = re.sub(r"\s+", " ", match.group(0)).strip()
            if len(cleaned) < 85:
                found_degrees.append(cleaned)
    return found_degrees[0] if found_degrees else "Not explicitly specified"


def extract_candidate_metadata(text: str, filename: str) -> Dict[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    skip_headers = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "bio",
        "professional summary",
        "technical skills",
        "experience",
    }
    candidate_name = filename.rsplit(".", 1)[0].replace("_", " ").title()

    for line in lines[:6]:
        if "@" in line or any(char.isdigit() for char in line):
            continue
        # Prefer an all-caps two/three-word name, even when a PDF disclaimer
        # is concatenated directly before it.
        candidates = re.findall(r"\b[A-Z][A-Z'-]+(?:\s+[A-Z][A-Z'-]+){1,2}\b", line)
        for candidate in candidates:
            if candidate.lower() not in skip_headers and not candidate.startswith("FICTIONAL SAMPLE"):
                candidate_name = candidate.title()
                break
        if candidate_name != filename.rsplit(".", 1)[0].replace("_", " ").title():
            break

        clean_line = re.sub(r"[^a-zA-Z\s\.\-]", "", line).strip()
        if 2 <= len(clean_line.split()) <= 4 and clean_line.lower() not in skip_headers:
            candidate_name = clean_line.title()
            break

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(
        r"(?:\+\d{1,3}[-.\s]?)?(?:\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{5}[-.\s]?\d{5})",
        text,
    )

    return {
        "candidate_name": candidate_name,
        "email": email_match.group(0) if email_match else "N/A",
        "phone": phone_match.group(0).strip() if phone_match else "N/A",
    }


def parse_job_description(jd_text: str) -> Dict[str, Any]:
    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
    job_title = lines[0][:80] if lines else "Target Role"
    skills = extract_skills(jd_text)
    min_exp = extract_experience_years(jd_text, is_jd=True)
    education = extract_education(jd_text)

    # Extract bullet-point key requirements
    requirements = [
        re.sub(r"^[-•*▪\d\.\)]+\s*", "", line)
        for line in lines
        if re.match(r"^[-•*▪\d\.\)]+", line) and len(line) > 15
    ][:8]

    return {
        "job_title": job_title,
        "required_skills": skills,
        "min_experience_years": min_exp,
        "education_requirement": education,
        "key_requirements": requirements,
    }


def compute_semantic_similarity(jd_text: str, resume_text: str) -> float:
    embeddings = model.encode([jd_text[:3500], resume_text[:3500]], normalize_embeddings=True)
    raw_cos = float(np.dot(embeddings[0], embeddings[1]))
    # Calibrate raw cosine similarity [0.20, 0.85] -> [0, 100] for realistic differentiation
    calibrated = ((raw_cos - 0.20) / (0.85 - 0.20)) * 100.0
    return round(float(np.clip(calibrated, 0.0, 100.0)), 1)


def evaluate_skills(
    jd_skills: List[str], cand_skills: List[str]
) -> Tuple[float, List[str], List[Dict[str, Any]], List[str]]:
    if not jd_skills:
        return 75.0, cand_skills[:8], [], []

    cand_set = set(cand_skills)
    matched = [s for s in jd_skills if s in cand_set]
    unmatched = [s for s in jd_skills if s not in cand_set]

    related: List[Dict[str, Any]] = []
    missing: List[str] = []
    partial_credit = 0.0

    for req_skill in unmatched:
        best_sim = 0.0
        best_cand_skill = None
        req_vec = SKILL_TO_VEC.get(req_skill)
        if req_vec is not None:
            for c_skill in cand_skills:
                c_vec = SKILL_TO_VEC.get(c_skill)
                if c_vec is not None:
                    sim = float(np.dot(req_vec, c_vec))
                    if sim > best_sim:
                        best_sim = sim
                        best_cand_skill = c_skill

        if best_sim >= 0.62 and best_cand_skill:
            partial_credit += 0.5
            related.append(
                {
                    "required": req_skill,
                    "candidate_has": best_cand_skill,
                    "similarity": round(best_sim * 100, 0),
                }
            )
        else:
            missing.append(req_skill)

    score = ((len(matched) + partial_credit) / len(jd_skills)) * 100.0
    return round(min(score, 100.0), 1), matched, related, missing


def evaluate_experience(req_exp: float, cand_exp: float) -> float:
    if req_exp <= 0:
        return 100.0 if cand_exp > 0 else 75.0
    if cand_exp >= req_exp:
        return 100.0
    return round(max(15.0, (cand_exp / req_exp) * 100.0), 1)


def generate_explanation(
    cand_name: str,
    overall_score: float,
    semantic_score: float,
    skill_score: float,
    exp_score: float,
    matched_skills: List[str],
    related_skills: List[Dict[str, Any]],
    missing_skills: List[str],
    req_exp: float,
    cand_exp: float,
) -> List[str]:
    reasons: List[str] = []

    if semantic_score >= 78:
        reasons.append(
            f"Strong contextual & domain alignment ({semantic_score}% semantic similarity) with the Job Description responsibilities."
        )
    elif semantic_score >= 55:
        reasons.append(
            f"Moderate contextual overlap ({semantic_score}% semantic similarity) with the target role's workflows."
        )
    else:
        reasons.append(
            f"Low contextual similarity ({semantic_score}%) — resume background diverges from the JD's core domain."
        )

    if matched_skills:
        reasons.append(
            f"Directly satisfies {len(matched_skills)} required skill(s): {', '.join(matched_skills[:6])}."
        )
    if related_skills:
        rel_str = ", ".join(
            f"{r['candidate_has']} (~{r['required']})" for r in related_skills[:3]
        )
        reasons.append(f"Demonstrates transferable adjacent technologies: {rel_str}.")
    if missing_skills:
        reasons.append(
            f"Missing {len(missing_skills)} listed skill(s): {', '.join(missing_skills[:6])}."
        )

    if req_exp > 0:
        if cand_exp >= req_exp:
            reasons.append(
                f"Exceeds or meets the {req_exp:g}-year experience benchmark with {cand_exp:g} years detected."
            )
        else:
            reasons.append(
                f"Experience gap: {cand_exp:g} years detected versus {req_exp:g}+ years requested ({exp_score}% experience fit)."
            )

    return reasons


def score_resume_against_jd(
    session_id: str,
    candidate_id: str,
    filename: str,
    resume_text: str,
    jd_text: str,
    parsed_jd: Dict[str, Any],
) -> Dict[str, Any]:
    meta = extract_candidate_metadata(resume_text, filename)
    cand_skills = extract_skills(resume_text)
    cand_exp = extract_experience_years(resume_text, is_jd=False)
    education = extract_education(resume_text)

    semantic_score = compute_semantic_similarity(jd_text, resume_text)
    skill_score, matched, related, missing = evaluate_skills(
        parsed_jd["required_skills"], cand_skills
    )
    exp_score = evaluate_experience(parsed_jd["min_experience_years"], cand_exp)

    # Weighted Hybrid Ranking Formula: 45% Semantic + 35% Skills + 20% Experience
    overall_score = round(
        (0.45 * semantic_score) + (0.35 * skill_score) + (0.20 * exp_score), 1
    )

    reasons = generate_explanation(
        cand_name=meta["candidate_name"],
        overall_score=overall_score,
        semantic_score=semantic_score,
        skill_score=skill_score,
        exp_score=exp_score,
        matched_skills=matched,
        related_skills=related,
        missing_skills=missing,
        req_exp=parsed_jd["min_experience_years"],
        cand_exp=cand_exp,
    )

    clean_summary = " ".join(resume_text.splitlines()[:8])[:420] + "..."

    return {
        "id": candidate_id,
        "session_id": session_id,
        "filename": filename,
        "candidate_name": meta["candidate_name"],
        "email": meta["email"],
        "phone": meta["phone"],
        "education": education,
        "experience_years": cand_exp,
        "overall_score": overall_score,
        "semantic_score": semantic_score,
        "skill_score": skill_score,
        "experience_score": exp_score,
        "matched_skills": matched,
        "related_skills": related,
        "missing_skills": missing,
        "all_extracted_skills": cand_skills,
        "reasons": reasons,
        "resume_summary": clean_summary,
    }