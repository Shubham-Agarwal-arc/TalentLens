# TalentLens — AI-Based Resume Matching & Candidate Ranking System

An end-to-end NLP-powered Applicant Tracking & Candidate Ranking prototype that parses Job Descriptions and batch-uploaded resumes (PDF/DOCX), evaluates semantic and structured fit, and produces explainable candidate rankings.

## System Architecture

1. **Frontend (React.js + Tailwind CSS):**
   - **Module 1 (JD Input):** Supports direct text pasting or `.pdf`/`.docx`/`.txt` upload with instant extraction of required skills, experience thresholds, and qualifications.
   - **Module 2 (Batch Resume Upload):** Multi-file uploader supporting 10+ PDF/DOCX resumes simultaneously.
   - **Module 4 & 5 (Ranking Dashboard & Candidate Inspector):** Interactive sortable/filterable leaderboard and a candidate-level modal displaying score breakdowns, skill gaps, experience comparison, and human-readable reasoning.
2. **Backend (Python + FastAPI):**
   - Exposes REST endpoints (`/api/parse-jd`, `/api/match`, `/api/sessions/{id}`) with automated document text extraction (`pypdf` and `python-docx`).
3. **Database (SQLite):**
   - Persists screening sessions and candidate evaluation records for auditability and session retrieval.

---

## Matching Algorithm & Scoring Methodology

To avoid the pitfalls of brittle keyword-only ATS filters while keeping scores transparent for recruiters, the system computes a **Weighted Hybrid Score (0–100)**:

$$\text{Overall Score} = (0.45 \times S_{\text{semantic}}) + (0.35 \times S_{\text{skills}}) + (0.20 \times S_{\text{experience}})$$

### 1. Semantic Contextual Similarity ($S_{\text{semantic}}$ — 45% Weight)
- Both the Job Description and extracted Resume text are encoded into **384-dimensional dense vectors** using `sentence-transformers/all-MiniLM-L6-v2` (a Siamese BERT network optimized for semantic textual similarity).
- We compute the **Cosine Similarity** between the normalized embeddings:
  $$\cos(\theta) = \frac{\mathbf{E}_{\text{JD}} \cdot \mathbf{E}_{\text{Resume}}}{\|\mathbf{E}_{\text{JD}}\| \|\mathbf{E}_{\text{Resume}}\|}$$
- Raw cosine values (typically distributed in $[0.20, 0.85]$ for cross-document text) are min-max calibrated onto a $[0, 100]$ scale so semantically related roles (e.g., *"built containerized REST services"* matching *"Docker & Microservices"*) receive strong scores even without identical phrasing.

### 2. Taxonomy + Semantic Skill Alignment ($S_{\text{skills}}$ — 35% Weight)
- **Canonical Normalization:** Regex word-boundary extraction maps aliases to canonical entities (e.g., `reactjs` $\rightarrow$ `React.js`, `postgres` $\rightarrow$ `PostgreSQL`).
- **Partial Transferable Credit:** For any JD skill missing from a resume, the engine compares its embedding vector against all skills the candidate *does* possess. If cosine similarity $\ge 0.62$ (e.g., candidate has `MySQL` when JD asks for `PostgreSQL`), it awards **0.5 partial credit** and flags it as a transferable skill while still listing the exact skill gap.
  $$S_{\text{skills}} = \min\left(100,\; \frac{|\text{Matched Skills}| + 0.5 \times |\text{Transferable Skills}|}{|\text{JD Required Skills}|} \times 100\right)$$

### 3. Experience Fit ($S_{\text{experience}}$ — 20% Weight)
- Extracts required years from the JD and candidate experience from both explicit statements (`"5.5 years of experience"`) and employment date ranges (`"2020 - Present"`).
- Candidates meeting or exceeding the requirement score **100%**; candidates below the threshold receive proportional scoring $\max(15, \frac{E_{\text{cand}}}{E_{\text{req}}} \times 100)$.

---

## Setup & Running Locally

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_samples.py
uvicorn main:app --reload --port 8000