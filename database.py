"""
database.py  –  All MySQL helper functions for Job Application Tracker
Every route in app.py calls one of these functions; no raw SQL in app.py.
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    """Return a fresh MySQL connection using credentials from .env"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_tracker"),
    )


# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════

def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    stats = {}
    for table in ["companies", "jobs", "applications", "contacts"]:
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
        stats[table] = cursor.fetchone()["cnt"]
    cursor.execute(
        "SELECT status, COUNT(*) AS cnt FROM applications GROUP BY status ORDER BY cnt DESC"
    )
    stats["by_status"] = cursor.fetchall()
    # Recent applications (last 5)
    cursor.execute(
        """SELECT a.id, j.title AS job_title, c.name AS company_name,
                  a.applied_date, a.status
           FROM applications a
           JOIN jobs j ON a.job_id = j.id
           JOIN companies c ON j.company_id = c.id
           ORDER BY a.applied_date DESC LIMIT 5"""
    )
    stats["recent"] = cursor.fetchall()
    cursor.close()
    conn.close()
    return stats


# ══════════════════════════════════════════════════════════════════
# COMPANIES
# ══════════════════════════════════════════════════════════════════

def get_all_companies():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM companies ORDER BY name")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def get_company(company_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return row


def add_company(name, industry, website, location, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO companies (name, industry, website, location, notes) VALUES (%s,%s,%s,%s,%s)",
        (name, industry, website, location, notes),
    )
    conn.commit()
    cursor.close(); conn.close()


def update_company(company_id, name, industry, website, location, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE companies SET name=%s, industry=%s, website=%s, location=%s, notes=%s WHERE id=%s",
        (name, industry, website, location, notes, company_id),
    )
    conn.commit()
    cursor.close(); conn.close()


def delete_company(company_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE id = %s", (company_id,))
    conn.commit()
    cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════
# JOBS
# ══════════════════════════════════════════════════════════════════

def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT j.*, c.name AS company_name
           FROM jobs j
           JOIN companies c ON j.company_id = c.id
           ORDER BY j.posted_date DESC"""
    )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def get_job(job_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return row


def add_job(company_id, title, description, required_skills, salary_range, location, posted_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO jobs (company_id, title, description, required_skills,
                             salary_range, location, posted_date)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (company_id, title, description, required_skills, salary_range, location, posted_date),
    )
    conn.commit()
    cursor.close(); conn.close()


def update_job(job_id, company_id, title, description, required_skills,
               salary_range, location, posted_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE jobs SET company_id=%s, title=%s, description=%s, required_skills=%s,
                          salary_range=%s, location=%s, posted_date=%s
           WHERE id=%s""",
        (company_id, title, description, required_skills,
         salary_range, location, posted_date, job_id),
    )
    conn.commit()
    cursor.close(); conn.close()


def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
    conn.commit()
    cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════
# APPLICATIONS
# ══════════════════════════════════════════════════════════════════

def get_all_applications():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT a.*, j.title AS job_title, c.name AS company_name
           FROM applications a
           JOIN jobs j ON a.job_id = j.id
           JOIN companies c ON j.company_id = c.id
           ORDER BY a.applied_date DESC"""
    )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def get_application(app_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM applications WHERE id = %s", (app_id,))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return row


def add_application(job_id, applied_date, status, resume_version, cover_letter, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO applications (job_id, applied_date, status,
                                     resume_version, cover_letter, notes)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (job_id, applied_date, status, resume_version, cover_letter, notes),
    )
    conn.commit()
    cursor.close(); conn.close()


def update_application(app_id, job_id, applied_date, status,
                       resume_version, cover_letter, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE applications SET job_id=%s, applied_date=%s, status=%s,
                                   resume_version=%s, cover_letter=%s, notes=%s
           WHERE id=%s""",
        (job_id, applied_date, status, resume_version, cover_letter, notes, app_id),
    )
    conn.commit()
    cursor.close(); conn.close()


def delete_application(app_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id = %s", (app_id,))
    conn.commit()
    cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════
# CONTACTS
# ══════════════════════════════════════════════════════════════════

def get_all_contacts():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT ct.*, c.name AS company_name
           FROM contacts ct
           LEFT JOIN companies c ON ct.company_id = c.id
           ORDER BY ct.name"""
    )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def get_contact(contact_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return row


def add_contact(company_id, name, role, email, phone, linkedin, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO contacts (company_id, name, role, email, phone, linkedin, notes)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (company_id or None, name, role, email, phone, linkedin, notes),
    )
    conn.commit()
    cursor.close(); conn.close()


def update_contact(contact_id, company_id, name, role, email, phone, linkedin, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE contacts SET company_id=%s, name=%s, role=%s, email=%s,
                               phone=%s, linkedin=%s, notes=%s
           WHERE id=%s""",
        (company_id or None, name, role, email, phone, linkedin, notes, contact_id),
    )
    conn.commit()
    cursor.close(); conn.close()


def delete_contact(contact_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
    conn.commit()
    cursor.close(); conn.close()


# ══════════════════════════════════════════════════════════════════
# JOB MATCH
# ══════════════════════════════════════════════════════════════════

def get_job_matches(user_skills_str):
    """
    Given a comma-separated string of user skills,
    return all jobs ranked by skill match percentage.
    """
    user_skills = set(
        s.strip().lower() for s in user_skills_str.split(",") if s.strip()
    )
    jobs = get_all_jobs()
    results = []
    for job in jobs:
        required = job.get("required_skills") or ""
        job_skills = set(s.strip().lower() for s in required.split(",") if s.strip())
        if not job_skills:
            pct = 0.0
            matched = set()
        else:
            matched = user_skills & job_skills
            pct = round(len(matched) / len(job_skills) * 100, 1)
        results.append({
            **job,
            "match_pct": pct,
            "matched_skills": ", ".join(sorted(matched)),
            "missing_skills": ", ".join(sorted(job_skills - user_skills)),
        })
    results.sort(key=lambda x: x["match_pct"], reverse=True)
    return results
