import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = str(Path(__file__).resolve().parent / "resume_matcher.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screening_sessions (
            id TEXT PRIMARY KEY,
            job_title TEXT,
            jd_text TEXT,
            extracted_jd TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_results (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            filename TEXT,
            candidate_name TEXT,
            email TEXT,
            phone TEXT,
            education TEXT,
            experience_years REAL,
            overall_score REAL,
            semantic_score REAL,
            skill_score REAL,
            experience_score REAL,
            matched_skills TEXT,
            related_skills TEXT,
            missing_skills TEXT,
            all_extracted_skills TEXT,
            reasons TEXT,
            resume_summary TEXT,
            FOREIGN KEY(session_id) REFERENCES screening_sessions(id)
        )
    """)
    conn.commit()
    conn.close()


def save_session(session_id: str, job_title: str, jd_text: str, extracted_jd: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO screening_sessions (id, job_title, jd_text, extracted_jd, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session_id, job_title, jd_text, json.dumps(extracted_jd), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def save_candidate_result(candidate: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO candidate_results (
            id, session_id, filename, candidate_name, email, phone, education,
            experience_years, overall_score, semantic_score, skill_score, experience_score,
            matched_skills, related_skills, missing_skills, all_extracted_skills,
            reasons, resume_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate["id"],
            candidate["session_id"],
            candidate["filename"],
            candidate["candidate_name"],
            candidate["email"],
            candidate["phone"],
            candidate["education"],
            candidate["experience_years"],
            candidate["overall_score"],
            candidate["semantic_score"],
            candidate["skill_score"],
            candidate["experience_score"],
            json.dumps(candidate["matched_skills"]),
            json.dumps(candidate["related_skills"]),
            json.dumps(candidate["missing_skills"]),
            json.dumps(candidate["all_extracted_skills"]),
            json.dumps(candidate["reasons"]),
            candidate["resume_summary"],
        ),
    )
    conn.commit()
    conn.close()


def get_session_candidates(session_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM candidate_results WHERE session_id = ? ORDER BY overall_score DESC",
        (session_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        item = dict(row)
        for field in ["matched_skills", "related_skills", "missing_skills", "all_extracted_skills", "reasons"]:
            item[field] = json.loads(item[field])
        results.append(item)
    return results