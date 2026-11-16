# AI Resume Matcher

An explainable prototype for comparing a job description with a batch of synthetic PDF/DOCX resumes. It extracts structured candidate information, ranks candidates from 0 to 100, and shows the evidence behind every score.

## Features

- Paste or upload a PDF, DOCX, or TXT job description.
- Upload and process 10+ PDF/DOCX resumes in one request.
- Extract candidate name, email, phone, education, experience, and skills.
- Combine sentence-transformer semantic similarity with canonical skill matching and experience fit.
- Show matched, missing, and transferable skills plus score explanations.
- Persist screening sessions and candidate results in SQLite.
- Generate 12 synthetic resumes for a repeatable demonstration.

## Architecture

- **Frontend:** React 18 and Vite. The UI is a single recruiter workflow with upload panels, filters, a ranking table, and a candidate inspector.
- **Backend:** FastAPI with `pypdf` and `python-docx` document extraction.
- **NLP:** `sentence-transformers/all-MiniLM-L6-v2` embeddings plus a curated skill alias taxonomy.
- **Storage:** SQLite, created at `backend/resume_matcher.db` at runtime.

## Run locally

### One-click demo (Windows)

From the project folder, double-click `Start-AI-Resume-Matcher.bat`, or run:

```powershell
.\start.ps1
```

This starts the FastAPI backend and Vite frontend, waits for both services to be ready, opens `http://localhost:5173` automatically, and stops the child services when you press `Ctrl+C` in the launcher window.

### Backend

Use Python 3.10+ (the included environment is already configured for this project):

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_samples.py
python -m uvicorn main:app --reload --port 8000
```

Using `python -m uvicorn` is intentional on Windows: it guarantees that Uvicorn is launched from the same virtual environment as the backend, even when the standalone `uvicorn` executable is not on PowerShell's `PATH`. If the environment has not been activated, run the equivalent command directly:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

The first NLP run downloads the public `all-MiniLM-L6-v2` model from Hugging Face.

### Frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). The frontend expects the API at `http://localhost:8000`. The one-click launcher handles both terminals and opens this URL automatically.

## Demonstration

1. Click **Load Sample JD**.
2. Select all files under `backend/sample_data` (12 resumes: 6 PDF and 6 DOCX).
3. Click **Analyze & Rank Candidates**.
4. Open a row to inspect the score components, experience comparison, skill gaps, transferable skills, and explanation.

## Matching methodology

Each candidate receives a transparent weighted hybrid score:

```text
overall = 0.45 * semantic_similarity
        + 0.35 * skill_alignment
        + 0.20 * experience_fit
```

- **Semantic similarity (45%):** normalized cosine similarity between the JD and resume embeddings, calibrated to 0-100.
- **Skill alignment (35%):** exact canonical skill matches receive full credit. Missing skills can receive 0.5 credit when their taxonomy embeddings are sufficiently similar to a candidate skill; the original requirement remains visible as a gap.
- **Experience fit (20%):** candidates meeting the minimum receive 100; otherwise the score is proportional to detected years, with a conservative floor.

The score is not a hiring decision. It is a screening aid and should be reviewed alongside the extracted evidence.

## API

- `GET /api/health`
- `POST /api/parse-jd` with multipart field `jd_file`
- `POST /api/match` with form field `jd_text` and repeated multipart field `resumes`
- `GET /api/sessions/{session_id}`

## Submission notes

The sample data is synthetic and contains no real candidate personal information. Do not commit `venv`, `node_modules`, the SQLite database, or generated smoke-test files. For an interview demonstration, explain the weighted formula, the alias normalization, and why transferable skills are shown separately from exact matches.

### GitHub submission

From the project root:

```powershell
git init
git add .
git commit -m "Build explainable AI resume matcher"
git branch -M main
git remote add origin https://github.com/<your-github-username>/ai-resume-matcher.git
git push -u origin main
```

Create the empty GitHub repository first at `https://github.com/new`, using the name `ai-resume-matcher`. Do not initialize it with another README or `.gitignore`, because this project already contains both.
