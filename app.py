"""
app.py  –  Job Application Tracker
Flask application with full CRUD for all 4 tables + Job Match feature.
Run:  python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os
import database as db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════

@app.route("/")
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


# ══════════════════════════════════════════════════════════════════
# COMPANIES
# ══════════════════════════════════════════════════════════════════

@app.route("/companies")
def companies():
    all_companies = db.get_all_companies()
    return render_template("companies.html", companies=all_companies)


@app.route("/companies/add", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        db.add_company(
            request.form["name"],
            request.form["industry"],
            request.form["website"],
            request.form["location"],
            request.form["notes"],
        )
        flash("Company added successfully!", "success")
        return redirect(url_for("companies"))
    return render_template("companies.html", form_mode="add", companies=db.get_all_companies())


@app.route("/companies/edit/<int:id>", methods=["GET", "POST"])
def edit_company(id):
    company = db.get_company(id)
    if not company:
        flash("Company not found.", "danger")
        return redirect(url_for("companies"))
    if request.method == "POST":
        db.update_company(
            id,
            request.form["name"],
            request.form["industry"],
            request.form["website"],
            request.form["location"],
            request.form["notes"],
        )
        flash("Company updated!", "success")
        return redirect(url_for("companies"))
    return render_template("companies.html", company=company,
                           form_mode="edit", companies=db.get_all_companies())


@app.route("/companies/delete/<int:id>", methods=["POST"])
def delete_company(id):
    db.delete_company(id)
    flash("Company deleted.", "info")
    return redirect(url_for("companies"))


# ══════════════════════════════════════════════════════════════════
# JOBS
# ══════════════════════════════════════════════════════════════════

@app.route("/jobs")
def jobs():
    all_jobs = db.get_all_jobs()
    return render_template("jobs.html", jobs=all_jobs)


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    companies = db.get_all_companies()
    if request.method == "POST":
        db.add_job(
            request.form["company_id"],
            request.form["title"],
            request.form["description"],
            request.form["required_skills"],
            request.form["salary_range"],
            request.form["location"],
            request.form["posted_date"] or None,
        )
        flash("Job added!", "success")
        return redirect(url_for("jobs"))
    return render_template("jobs.html", companies=companies,
                           form_mode="add", jobs=db.get_all_jobs())


@app.route("/jobs/edit/<int:id>", methods=["GET", "POST"])
def edit_job(id):
    job = db.get_job(id)
    companies = db.get_all_companies()
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("jobs"))
    if request.method == "POST":
        db.update_job(
            id,
            request.form["company_id"],
            request.form["title"],
            request.form["description"],
            request.form["required_skills"],
            request.form["salary_range"],
            request.form["location"],
            request.form["posted_date"] or None,
        )
        flash("Job updated!", "success")
        return redirect(url_for("jobs"))
    return render_template("jobs.html", job=job, companies=companies,
                           form_mode="edit", jobs=db.get_all_jobs())


@app.route("/jobs/delete/<int:id>", methods=["POST"])
def delete_job(id):
    db.delete_job(id)
    flash("Job deleted.", "info")
    return redirect(url_for("jobs"))


# ══════════════════════════════════════════════════════════════════
# APPLICATIONS
# ══════════════════════════════════════════════════════════════════

@app.route("/applications")
def applications():
    all_apps = db.get_all_applications()
    return render_template("applications.html", applications=all_apps)


@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    jobs_list = db.get_all_jobs()
    if request.method == "POST":
        db.add_application(
            request.form["job_id"],
            request.form["applied_date"],
            request.form["status"],
            request.form["resume_version"],
            request.form["cover_letter"],
            request.form["notes"],
        )
        flash("Application logged!", "success")
        return redirect(url_for("applications"))
    return render_template("applications.html", jobs=jobs_list,
                           form_mode="add", applications=db.get_all_applications())


@app.route("/applications/edit/<int:id>", methods=["GET", "POST"])
def edit_application(id):
    app_rec = db.get_application(id)
    jobs_list = db.get_all_jobs()
    if not app_rec:
        flash("Application not found.", "danger")
        return redirect(url_for("applications"))
    if request.method == "POST":
        db.update_application(
            id,
            request.form["job_id"],
            request.form["applied_date"],
            request.form["status"],
            request.form["resume_version"],
            request.form["cover_letter"],
            request.form["notes"],
        )
        flash("Application updated!", "success")
        return redirect(url_for("applications"))
    return render_template("applications.html", application=app_rec,
                           jobs=jobs_list, form_mode="edit",
                           applications=db.get_all_applications())


@app.route("/applications/delete/<int:id>", methods=["POST"])
def delete_application(id):
    db.delete_application(id)
    flash("Application removed.", "info")
    return redirect(url_for("applications"))


# ══════════════════════════════════════════════════════════════════
# CONTACTS
# ══════════════════════════════════════════════════════════════════

@app.route("/contacts")
def contacts():
    all_contacts = db.get_all_contacts()
    return render_template("contacts.html", contacts=all_contacts)


@app.route("/contacts/add", methods=["GET", "POST"])
def add_contact():
    companies = db.get_all_companies()
    if request.method == "POST":
        db.add_contact(
            request.form.get("company_id") or None,
            request.form["name"],
            request.form["role"],
            request.form["email"],
            request.form["phone"],
            request.form["linkedin"],
            request.form["notes"],
        )
        flash("Contact added!", "success")
        return redirect(url_for("contacts"))
    return render_template("contacts.html", companies=companies,
                           form_mode="add", contacts=db.get_all_contacts())


@app.route("/contacts/edit/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    contact = db.get_contact(id)
    companies = db.get_all_companies()
    if not contact:
        flash("Contact not found.", "danger")
        return redirect(url_for("contacts"))
    if request.method == "POST":
        db.update_contact(
            id,
            request.form.get("company_id") or None,
            request.form["name"],
            request.form["role"],
            request.form["email"],
            request.form["phone"],
            request.form["linkedin"],
            request.form["notes"],
        )
        flash("Contact updated!", "success")
        return redirect(url_for("contacts"))
    return render_template("contacts.html", contact=contact,
                           companies=companies, form_mode="edit",
                           contacts=db.get_all_contacts())


@app.route("/contacts/delete/<int:id>", methods=["POST"])
def delete_contact(id):
    db.delete_contact(id)
    flash("Contact removed.", "info")
    return redirect(url_for("contacts"))


# ══════════════════════════════════════════════════════════════════
# JOB MATCH
# ══════════════════════════════════════════════════════════════════

@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    results = []
    user_skills = ""
    if request.method == "POST":
        user_skills = request.form.get("skills", "").strip()
        if user_skills:
            results = db.get_job_matches(user_skills)
        else:
            flash("Please enter at least one skill.", "danger")
    return render_template("job_match.html", results=results, user_skills=user_skills)


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True)
