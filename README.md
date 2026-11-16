# TalentLens

## Architecture

TalentLens is an explainable AI-based resume matching and candidate ranking prototype. It compares one job description with a batch of PDF/DOCX resumes, extracts structured evidence, calculates a transparent 0–100 match score, and presents the ranked candidates in a recruiter-focused dashboard.

### System overview

```text
Recruiter
   |
   v
React + Vite frontend
   |
   | HTTP / JSON + multipart uploads
   v
FastAPI backend
   |
   +--> PDF/DOCX/TXT text extraction
   +--> Job description and resume information extraction
   +--> Sentence Transformer semantic similarity
   +--> Canonical skill and transferable-skill analysis
   +--> Experience-fit calculation
   |
   v
SQLite session and candidate-result storage
```

### Frontend

The frontend is implemented with React 18 and Vite. It provides a single end-to-end recruiter workflow:

1. Paste a job description or upload a PDF, DOCX, or TXT job-description file.
2. Select a batch of PDF/DOCX resumes.
3. Submit the role and resumes for analysis.
4. Review the ranked candidate table.
5. Open an individual candidate for detailed analysis.

The interface includes:

- Job-description input with sample JD loading.
- Batch resume selection with file count and file-size visibility.
- Status messages for parsing, validation, connection, and analysis states.
- Candidate ranking with search and minimum-score filtering.
- Summary metrics for candidates analyzed, average score, top candidate, and detected requirements.
- Candidate-level analysis showing contact details, education, score components, experience comparison, matched skills, missing skills, transferable skills, and score reasoning.
- Responsive styling with locally bundled Tailwind CSS, so the production build does not depend on the Tailwind CDN.

The frontend sends requests to `http://localhost:8000/api` by default. This is intentionally kept simple for the local assignment demonstration.

### Backend

The backend is a FastAPI application located in `backend/main.py`. It exposes the following endpoints:

- `GET /api/health` — confirms that the API is running.
- `POST /api/parse-jd` — accepts a multipart `jd_file` and returns extracted JD text and parsed requirements.
- `POST /api/match` — accepts form field `jd_text` and repeated multipart `resumes` fields, then returns ranked candidates.
- `GET /api/sessions/{session_id}` — retrieves a previously stored screening session and its candidates.

The API validates file extensions and upload sizes before processing:

- Job descriptions: PDF, DOCX, or TXT; maximum 5 MB.
- Resumes: PDF or DOCX; maximum 10 MB per file.

Each resume is handled independently. If one file is unsupported, unreadable, empty, or too large, the API reports that file in the response errors while continuing with valid resumes. If no resume can be processed, the API returns a clear validation error instead of a false success response.

### Document extraction

The extraction layer in `backend/nlp_engine.py` uses:

- `pypdf` for text-based PDF extraction.
- `python-docx` for DOCX paragraph and table extraction.
- UTF-8 decoding for TXT job descriptions.

The parser extracts:

- Candidate name.
- Email address.
- Phone number.
- Education or degree.
- Experience in years.
- Skills detected from the supported taxonomy.
- A short resume summary for the candidate inspector.

Experience detection supports both explicit statements such as `5 years of experience` and date ranges such as `2020 - Present`. The current prototype expects text-based PDFs; image-only scanned PDFs would require an OCR layer in a future production version.

### Matching pipeline

For each candidate, TalentLens performs the following steps:

1. Extract text from the uploaded resume.
2. Parse the job description into a title, required skills, minimum experience, education requirement, and key requirements.
3. Normalize detected skill aliases to canonical names.
4. Compute semantic similarity between the JD and resume.
5. Compare required and candidate skills.
6. Calculate experience fit.
7. Combine the sub-scores into one overall score.
8. Generate human-readable reasons explaining the result.
9. Persist the session and candidate result in SQLite.
10. Sort candidates by descending overall score.

The weighted score is:

```text
overall_score =
    0.45 * semantic_score
  + 0.35 * skill_score
  + 0.20 * experience_score
```

#### Semantic score

The backend uses `sentence-transformers/all-MiniLM-L6-v2` to encode the job description and resume into normalized embeddings. Their cosine similarity is calibrated to a 0–100 range. This allows related wording and context to contribute even when the candidate and JD do not use exactly the same phrases.

#### Skill score

The engine uses a curated alias map. Examples include:

```text
reactjs       -> React.js
postgres      -> PostgreSQL
springboot    -> Spring Boot
k8s           -> Kubernetes
restful       -> REST APIs
```

Exact canonical matches receive full credit. If a required skill is not found exactly, the engine compares its taxonomy embedding with the candidate’s detected skills. A sufficiently similar skill can receive partial transferable credit, while the original required skill remains visible as missing. This makes the result more useful than a binary keyword filter.

#### Experience score

Candidates meeting or exceeding the JD’s minimum experience receive 100. Candidates below the requirement receive a proportional score with a conservative minimum floor. If a JD does not specify experience, the engine does not penalize candidates for the missing requirement.

### Persistence

SQLite is used for the assignment prototype so the application can run without an external database service. The database is created at:

```text
backend/resume_matcher.db
```

The database stores:

- Screening session ID, job title, original JD text, parsed JD, and creation time.
- Candidate filename and extracted metadata.
- Overall, semantic, skill, and experience scores.
- Matched, related, missing, and all extracted skills.
- Explanation reasons and resume summary.

The runtime database is excluded from Git by `.gitignore`.

### Project structure

```text
TalentLens/
├── backend/
│   ├── main.py                 FastAPI application and API routes
│   ├── nlp_engine.py           Extraction, embeddings, scoring, explanations
│   ├── database.py             SQLite schema and persistence helpers
│   ├── generate_samples.py     Synthetic PDF/DOCX demo-data generator
│   ├── requirements.txt        Python dependencies
│   └── sample_data/            Synthetic JD and 12 sample resumes
├── frontend/
│   ├── src/App.jsx             React application and recruiter workflow
│   ├── src/main.jsx            React entry point
│   ├── src/styles.css          Locally bundled Tailwind entry styles
│   ├── package.json            Frontend dependencies and scripts
│   ├── vite.config.js          Vite configuration
│   ├── tailwind.config.js      Tailwind content configuration
│   └── postcss.config.js       Tailwind/PostCSS configuration
├── start.ps1                   One-command Windows launcher
├── Start-AI-Resume-Matcher.bat Double-click launcher for Windows
└── .gitignore                  Local environment and runtime exclusions
```

## Setup

### Requirements

Install or have access to:

- Windows PowerShell.
- Python 3.10 or newer.
- Node.js 18 or newer with npm.
- Git, if the project is being submitted to GitHub.
- Internet access for the first download of the Sentence Transformer model.

The repository may be run with the included local Python environment if it already exists, but virtual environments and generated runtime files are intentionally excluded from the submission.

### Recommended one-click startup

From the project root:

```powershell
cd D:\ai-resume-matcher
.\start.ps1
```

Alternatively, double-click:

```text
Start-AI-Resume-Matcher.bat
```

The launcher:

1. Checks that `backend\venv\Scripts\python.exe` exists.
2. Starts FastAPI on `http://127.0.0.1:8000`.
3. Starts Vite on `http://127.0.0.1:5173`.
4. Polls both services until they respond.
5. Opens `http://localhost:5173` in the default browser.
6. Keeps the services running until `Ctrl+C` is pressed in the launcher window.
7. Stops the child processes during cleanup.

This is the preferred method for a technical interview demonstration because it avoids separate terminals and avoids the Windows PATH issue where `uvicorn.exe` may not be discoverable.

### Backend setup manually

Open PowerShell in the project root:

```powershell
cd D:\ai-resume-matcher\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_samples.py
python -m uvicorn main:app --reload --port 8000
```

If PowerShell script execution is restricted, use the virtual-environment interpreter without activating it:

```powershell
cd D:\ai-resume-matcher\backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe generate_samples.py
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

Verify the backend:

```powershell
curl.exe http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

On the first matching request, `sentence-transformers` downloads the public `all-MiniLM-L6-v2` model. This may take longer than subsequent requests.

### Frontend setup manually

Open a second PowerShell window:

```powershell
cd D:\ai-resume-matcher\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

For a production-build check:

```powershell
npm run build
```

The generated `frontend/dist` directory is local build output and is excluded from Git.

### Demonstration setup

The repository includes synthetic data with no real candidate personal information:

- `backend/sample_data/sample_jd.txt`
- 12 synthetic resumes.
- 6 PDF resumes.
- 6 DOCX resumes.

To demonstrate the complete workflow:

1. Start TalentLens using `.\start.ps1`.
2. Click **Load Sample JD**.
3. Select all PDF and DOCX files in `backend\sample_data`.
4. Click **Analyze & Rank Candidates**.
5. Review the ranked table and summary metrics.
6. Open a candidate row to inspect the score breakdown and explanation.

### GitHub setup

The local repository is already initialized with a `main` branch and excludes virtual environments, `node_modules`, build output, the SQLite database, and cache files.

Create an empty GitHub repository named `TalentLens`, then connect and push:

```powershell
cd D:\ai-resume-matcher
git remote add origin https://github.com/<your-github-username>/TalentLens.git
git push -u origin main
```

If the remote is already configured:

```powershell
git remote -v
git push -u origin main
```

Do not initialize the GitHub repository with another README, `.gitignore`, or license because the project already contains the required setup documentation and ignore rules.

### Troubleshooting

**`uvicorn` is not recognized**

Use the project interpreter explicitly:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

**The frontend says the backend is unavailable**

Confirm that the API responds:

```powershell
curl.exe http://127.0.0.1:8000/api/health
```

Then reload `http://localhost:5173`. The one-click launcher normally prevents this issue by waiting for the API before opening the browser.

**The model download is slow or unavailable**

Ensure the machine has internet access and retry the request. The model is cached locally after the first successful download.

**A resume is skipped**

Check that it is a PDF or DOCX file with readable embedded text and is below the 10 MB per-file limit. Scanned image-only PDFs require OCR, which is outside this prototype’s current scope.
