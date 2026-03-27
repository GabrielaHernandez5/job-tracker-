# AI Usage Documentation — Job Application Tracker

**Developer:** Sam
**AI Tools Used:** Claude (claude.ai) — primary co-developer | ChatGPT — secondary debugging
**Methodology:** Iterative co-development. AI was used as a pair programmer — not to generate entire features blindly, but to reason through problems, validate approaches, accelerate boilerplate, and diagnose bugs. Every AI output was reviewed, tested, and adapted.

---

## How I Used AI in This Project

Rather than asking AI to "build this app for me," I treated it as a senior developer I was pairing with. My prompts explained **what I was trying to accomplish and why**, described the **constraints** I was working within, and asked AI to reason through the trade-offs with me. The examples below document that process faithfully.

---

## Iteration 1 — Database Schema Design

### Problem I was thinking through
I knew I needed 4 tables but wasn't sure how to handle the relationships correctly. Specifically: should a Contact belong to a Company or to a Job? And what happens to Applications if someone deletes a Job — should they cascade or be preserved?

### Prompt I used
> "I'm building a job application tracker with 4 tables: companies, jobs, applications, and contacts. A job belongs to a company. An application tracks when I applied to a specific job (not a company directly). A contact is a person I met — they may or may not be linked to a company. I need proper MySQL foreign keys.
>
> My concern: if I delete a company, I don't want orphaned jobs silently sitting in the database. But if I delete a company contact, I want to keep the contact row because they might move companies. How should I handle ON DELETE for each relationship?"

### What AI explained (and I verified)
Claude explained the distinction between `ON DELETE CASCADE` (delete children when parent is deleted) and `ON DELETE SET NULL` (orphan the row but keep it). It reasoned:
- `jobs.company_id` → `ON DELETE CASCADE` — a job without a company is meaningless
- `applications.job_id` → `ON DELETE CASCADE` — an application without a job loses all context
- `contacts.company_id` → `ON DELETE SET NULL` — a contact is a person, not a property of a company; they might change jobs

This matched my intuition but I hadn't known the exact SQL syntax. AI generated the schema and I ran it manually in MySQL Workbench to verify the constraints worked before adding it to `schema.sql`.

### Code generated (with my edits)
```sql
-- AI generated the structure; I added the ENUM for status
-- and the seed data INSERT statements for testing
CREATE TABLE applications (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    job_id          INT NOT NULL,
    applied_date    DATE NOT NULL,
    status          ENUM('Applied','Interview','Offer','Rejected','Withdrawn') DEFAULT 'Applied',
    resume_version  VARCHAR(100),
    cover_letter    TEXT,
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);
```
**My modification:** The original AI output used `VARCHAR(50)` for status. I changed it to an ENUM so the database enforces valid values at the data layer — not just at the form layer. This prevents bad data if someone ever inserts directly via SQL.

---

## Iteration 2 — Separating DB Logic from Routes

### Problem I was thinking through
I'd seen tutorials where all SQL is written directly inside Flask route functions. I knew that would get messy fast with 4 tables × 4 operations = 16+ SQL queries scattered through `app.py`. I wanted a cleaner architecture but wasn't sure of the right pattern for a project this size.

### Prompt I used
> "I'm structuring a Flask app with 4 database tables. I've seen two patterns:
>
> Pattern A: Write SQL directly in each route function
> Pattern B: Put all SQL in a separate `database.py` module and import functions into `app.py`
>
> The project has 4 tables (companies, jobs, applications, contacts) each needing full CRUD. At this scale, which pattern is better and why? What does Pattern B look like for a `get_connection()` helper and a `get_all_companies()` function using `mysql-connector-python`?"

### What AI reasoned
Claude argued for Pattern B: it separates concerns (routing logic vs. data access), makes each function independently testable, and means `app.py` reads like a description of the app's behavior rather than a mess of SQL strings. It also pointed out that if I later switch databases, I only change `database.py`.

### Code generated
```python
# AI generated this pattern; I adopted it for all 4 tables
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

def get_all_companies():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # returns rows as dicts, not tuples
    cursor.execute("SELECT * FROM companies ORDER BY name")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows
```
**My modification:** AI's first version didn't use `dictionary=True` on the cursor. Without it, rows come back as tuples (indexed by position), which breaks Jinja2 templates that reference columns by name like `{{ c.name }}`. I noticed this when my first template threw a `TypeError` and asked Claude why — it immediately identified the missing flag.

---

## Iteration 3 — CRUD Route Structure & Flash Messages

### Problem I was thinking through
I wasn't sure how to handle both GET (show the form) and POST (submit the form) in a single Flask route cleanly. I also wanted user feedback after every action (e.g., "Company added!" after saving) but didn't know how Flask's `flash()` system worked.

### Prompt I used
> "In Flask, I want a single route `/companies/add` that handles both showing an empty form (GET) and processing the submitted form (POST). After a successful POST, I want to redirect to `/companies` and show a success message to the user without storing it in the URL. What's the pattern for this, and how does Flask's `flash()` + `get_flashed_messages()` work? Show me a complete example."

### What AI explained
Claude walked me through the POST/Redirect/GET pattern — why you always redirect after a POST (to prevent duplicate submissions on page refresh), and how Flask's flash system stores a one-time message in the session that gets consumed on the next page render.

### Code generated
```python
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
        return redirect(url_for("companies"))  # POST → Redirect → GET
    return render_template("companies.html", form_mode="add", companies=db.get_all_companies())
```
**My modification:** AI's initial version returned a plain `redirect("/companies")` (hardcoded string). I changed it to `url_for("companies")` — which generates the URL from the function name. This is safer because if I ever change the route path, `url_for` still works without hunting down every redirect.

---

## Iteration 4 — Debugging: `None` values crashing the app

### Bug I encountered
After deploying the form, submitting a new company with the "Website" field left blank crashed the app with:
```
mysql.connector.errors.ProgrammingError: Not enough parameters for the SQL statement
```

### Prompt I used
> "My Flask form has optional fields (website, notes). When a user leaves them blank, `request.form['website']` returns an empty string `''`. I'm passing this to a MySQL INSERT with `%s` placeholders. Is there a difference between storing `''` (empty string) and `NULL` in MySQL? Should I convert empty strings to None before passing to the DB, and how do I do that cleanly in Python?"

### What AI explained
Claude clarified: in MySQL, `''` and `NULL` are different — `NULL` means "no value exists," while `''` is a legitimate (empty) string. For optional fields like website and notes, `NULL` is semantically correct and allows `IS NULL` queries later. It suggested this conversion pattern:

```python
# AI suggested this one-liner pattern
website = request.form.get("website") or None
# If the field is empty string '', `or None` converts it to NULL
```

**What I changed:** I adopted this pattern for all optional fields across all 4 tables. I also switched from `request.form['field']` (raises KeyError if field missing) to `request.form.get('field')` (returns None safely) for all non-required fields.

---

## Iteration 5 — Job Match Algorithm

### Problem I was thinking through
The spec said "calculate skill match percentages" but gave no algorithm. I had to design this myself. My instinct was: split both skill strings by comma, compare them, count how many overlap. But I wasn't sure about the math or how to handle case sensitivity and whitespace.

### Prompt I used
> "I need a skill match algorithm for a job tracker. Each job in my database has a `required_skills` column storing a comma-separated string like `'Python, MySQL, Flask, HTML'`. A user enters their skills the same way. I want to calculate what percentage of a job's required skills the user has.
>
> My thinking: convert both strings to sets, intersect them, divide by the job's skill count. Does this approach have issues? How do I handle: (1) case sensitivity (Python vs python), (2) extra whitespace around commas, (3) jobs with no skills listed (division by zero), (4) showing which skills matched and which are missing?"

### What AI confirmed and extended
Claude confirmed the set-intersection approach is correct and O(n+m) — efficient for this scale. It handled all 4 edge cases I described:

```python
def get_job_matches(user_skills_str):
    # Normalise: lowercase + strip whitespace before building the set
    user_skills = set(
        s.strip().lower() for s in user_skills_str.split(",") if s.strip()
    )
    jobs = get_all_jobs()
    results = []
    for job in jobs:
        required = job.get("required_skills") or ""  # handles NULL from DB
        job_skills = set(s.strip().lower() for s in required.split(",") if s.strip())

        if not job_skills:          # guard against division by zero
            pct = 0.0
            matched = set()
        else:
            matched = user_skills & job_skills
            pct = round(len(matched) / len(job_skills) * 100, 1)

        results.append({
            **job,
            "match_pct": pct,
            "matched_skills": ", ".join(sorted(matched)),         # I added sorted()
            "missing_skills": ", ".join(sorted(job_skills - user_skills)),  # I added this
        })

    results.sort(key=lambda x: x["match_pct"], reverse=True)
    return results
```
**My additions:** AI's first version only returned `match_pct` and `matched_skills`. I added `missing_skills` (the skills a user is lacking) because I wanted to show that in the UI — it's more useful to a job seeker than just the match number. I also added `sorted()` on both sets so the output is alphabetically consistent rather than random set order.

---

## Iteration 6 — Jinja2 Template Logic for Edit Forms

### Problem I was thinking through
For the edit form, I needed to pre-populate input fields with the existing database values. But I was reusing the same template for both Add (empty form) and Edit (pre-populated). I didn't want two separate HTML files for essentially the same form.

### Prompt I used
> "In Jinja2, I'm reusing the same HTML template for both 'add' and 'edit' forms. The Flask route passes a `form_mode` variable ('add' or 'edit') and optionally a `company` dict with existing values. How do I write the `value` attribute of an input so it pre-populates on edit but stays empty on add? Also how do I set the correct `selected` option in a `<select>` dropdown when editing?"

### What AI generated
```html
<!-- For text inputs -->
<input type="text" name="name"
       value="{{ company.name if company else '' }}" />

<!-- For select dropdowns — checks current value against each option -->
{% for c in companies %}
<option value="{{ c.id }}"
        {{ 'selected' if job and job.company_id == c.id }}>
  {{ c.name }}
</option>
{% endfor %}
```
**My modification:** AI used `company.get('name', '')` (dict-style). Since `cursor(dictionary=True)` returns proper Python dicts, this works — but I noticed `company.name` (attribute-style) also works in Jinja2 for dicts. I kept the `if company else ''` guard which is the critical safety check, ensuring the template doesn't crash when `company` is `None` (on the Add route).

---

## Iteration 7 — Dashboard Stats Query

### Problem I was thinking through
The dashboard needed total counts for all 4 tables plus a breakdown of applications by status. I could have done 5 separate queries. But I wanted to understand if there was a more efficient approach.

### Prompt I used
> "My dashboard needs: (1) total count from each of 4 tables, (2) count of applications grouped by status. I'm using mysql-connector-python. Is it better to run 5 separate SELECT COUNT(*) queries, or is there a smarter approach? What does the GROUP BY query look like for the status breakdown?"

### What AI reasoned
Claude explained that for 4 small COUNT(*) queries on indexed primary keys, the performance difference is negligible — the overhead of 4 round trips vs. 1 complex query is trivial at this data scale. It suggested keeping them simple and readable rather than over-engineering a single complex query. For the status breakdown:

```python
cursor.execute(
    "SELECT status, COUNT(*) AS cnt FROM applications GROUP BY status ORDER BY cnt DESC"
)
stats["by_status"] = cursor.fetchall()
```
**My addition:** I added a 5th query for the 5 most recent applications (used in the dashboard's "Recent Applications" panel and the Kanban board). AI didn't suggest this — it came from my own design decision to make the dashboard feel live and dynamic.

---

## Debugging Sessions (AI as Diagnostic Partner)

### Bug 1 — Template rendering wrong route as active
**Error:** Every nav link showed as "active" simultaneously because `'job' in request.endpoint` matched both the Jobs page and the Job Match page.

**Prompt:** *"My Jinja2 nav check `'job' in request.endpoint` is marking both `/jobs` and `/job-match` as active simultaneously. How do I fix the condition?"*

**Fix AI suggested (which I applied):**
```html
class="{{ 'active' if 'job' in request.endpoint and 'match' not in request.endpoint }}"
```

### Bug 2 — DELETE route returning 405 Method Not Allowed
**Error:** Clicking Delete caused a `405 Method Not Allowed` error.

**Prompt:** *"My delete route is decorated with `@app.route('/companies/delete/<int:id>', methods=['POST'])`. When I click the delete button I get 405. The button is inside a `<form>` — what am I missing?"*

**Fix:** The form was missing `method="POST"` — it was defaulting to GET. AI caught this immediately.

### Bug 3 — mysql-connector leaving connections open
**Symptom:** After running the app for a while, MySQL started refusing connections with "Too many connections."

**Prompt:** *"I'm opening a new MySQL connection in every database function and calling `cursor.close(); conn.close()` at the end. Is this correct, or do I need a connection pool? Could there be cases where the connection doesn't close properly if an exception is raised mid-function?"*

**What I learned:** AI explained that if an exception occurs between opening the connection and closing it, the `close()` calls never run. The proper fix is a `try/finally` block or a context manager. For this project's scale, the simple open/close pattern is fine, but AI suggested adding basic error handling around DB calls if I expand the project.

---

## Summary

| Feature | AI Contribution | My Contribution |
|---|---|---|
| Database schema | Generated structure and FK logic | ENUM for status, seed data, tested in MySQL |
| `database.py` architecture | Suggested Pattern B (separation of concerns) | Adopted it, fixed `dictionary=True` cursor bug |
| CRUD routes | Generated POST/Redirect/GET pattern | Added `url_for()`, safety redirects for missing records |
| Form edge cases | Explained `''` vs `NULL` distinction | Applied `or None` pattern across all 4 tables |
| Job Match algorithm | Confirmed set-intersection, handled 4 edge cases | Added `missing_skills`, `sorted()`, integrated into UI |
| Jinja2 edit forms | Generated conditional value/selected syntax | Applied guard for `None` company on Add route |
| Dashboard query | Explained GROUP BY, advised against over-engineering | Added recent applications query independently |
| Debugging | Identified root causes for all 3 bugs above | Caught symptoms, formed precise diagnostic prompts |

## Key Takeaway

The most valuable thing AI did in this project wasn't writing code — it was **explaining why** a certain approach is correct so I could make informed decisions. I never accepted output without running it, reading it line by line, and asking follow-up questions when something wasn't clear. AI accelerated development significantly, but the design decisions, the bug reports, and the final call on every piece of code were mine.
