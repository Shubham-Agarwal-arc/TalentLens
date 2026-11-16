import os
import uuid
import json
from typing import Any, Dict, List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from database import (
    get_connection,
    get_session_candidates,
    init_db,
    save_candidate_result,
    save_session,
)
from nlp_engine import (
    extract_text_from_file,
    parse_job_description,
    score_resume_against_jd,
)

MAX_JD_BYTES = 5 * 1024 * 1024
MAX_RESUME_BYTES = 10 * 1024 * 1024
SUPPORTED_JD_EXTENSIONS = {".pdf", ".docx", ".txt"}
SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".docx"}

app = FastAPI(
    title="AI Resume Matcher API",
    version="1.0.0",
    description="Explainable resume-to-job-description matching API.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


def _extension(filename: str) -> str:
    return os.path.splitext(filename or "")[1].lower()


async def _read_upload(upload: UploadFile, max_bytes: int) -> bytes:
    content = await upload.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"{upload.filename or 'Uploaded file'} exceeds the {max_bytes // (1024 * 1024)} MB limit.",
        )
    return content


def _extract_or_reject(filename: str, content: bytes) -> str:
    try:
        text = extract_text_from_file(filename, content)
    except Exception as exc:
        raise ValueError(f"Could not parse document: {exc}") from exc
    if not text.strip():
        raise ValueError("No readable text was found in the document.")
    return text


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/parse-jd")
async def parse_jd(jd_file: UploadFile = File(...)) -> Dict[str, Any]:
    extension = _extension(jd_file.filename)
    if extension not in SUPPORTED_JD_EXTENSIONS:
        raise HTTPException(status_code=415, detail="JD must be a PDF, DOCX, or TXT file.")
    content = await _read_upload(jd_file, MAX_JD_BYTES)
    try:
        jd_text = _extract_or_reject(jd_file.filename or "job-description", content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"jd_text": jd_text, "parsed_jd": parse_job_description(jd_text)}


@app.post("/api/match")
async def match_resumes(
    jd_text: str = Form(...),
    resumes: List[UploadFile] = File(...),
) -> Dict[str, Any]:
    if not jd_text.strip():
        raise HTTPException(status_code=422, detail="Job Description cannot be empty.")
    if not resumes:
        raise HTTPException(status_code=422, detail="Upload at least one resume.")

    parsed_jd = parse_job_description(jd_text)
    session_id = str(uuid.uuid4())
    save_session(session_id, parsed_jd["job_title"], jd_text, parsed_jd)

    candidates: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for upload in resumes:
        filename = upload.filename or "unnamed-resume"
        if _extension(filename) not in SUPPORTED_RESUME_EXTENSIONS:
            errors.append({"filename": filename, "error": "Only PDF and DOCX resumes are supported."})
            continue
        try:
            content = await _read_upload(upload, MAX_RESUME_BYTES)
            resume_text = _extract_or_reject(filename, content)
            candidate = score_resume_against_jd(
                session_id=session_id,
                candidate_id=str(uuid.uuid4()),
                filename=filename,
                resume_text=resume_text,
                jd_text=jd_text,
                parsed_jd=parsed_jd,
            )
            save_candidate_result(candidate)
            candidates.append(candidate)
        except HTTPException as exc:
            errors.append({"filename": filename, "error": str(exc.detail)})
        except Exception as exc:
            errors.append({"filename": filename, "error": str(exc)})

    if not candidates:
        raise HTTPException(
            status_code=422,
            detail={"message": "No resumes could be parsed.", "errors": errors},
        )
    candidates.sort(key=lambda candidate: candidate["overall_score"], reverse=True)
    return {
        "session_id": session_id,
        "parsed_jd": parsed_jd,
        "candidates": candidates,
        "errors": errors,
    }


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> Dict[str, Any]:
    connection = get_connection()
    session = connection.execute(
        "SELECT id, job_title, jd_text, extracted_jd, created_at FROM screening_sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    connection.close()
    if session is None:
        raise HTTPException(status_code=404, detail="Screening session not found.")

    return {
        "session": {
            "id": session["id"],
            "job_title": session["job_title"],
            "jd_text": session["jd_text"],
            "parsed_jd": json.loads(session["extracted_jd"]),
            "created_at": session["created_at"],
        },
        "candidates": get_session_candidates(session_id),
    }
