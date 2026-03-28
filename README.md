# Job Application Tracker

A full-stack web application to track job applications, companies, contacts, and job matches.

**Stack:** Python 3 + Flask | MySQL | HTML/CSS

## Demo Video

<video src="Job%20Tracker%20.mp4" controls="controls" width="100%">
</video>

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/job-tracker.git
cd job-tracker
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the database
Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=job_tracker
SECRET_KEY=any-random-string
```

### 5. Create the database and tables
```bash
mysql -u root -p job_tracker < schema.sql
```

### 6. Run the application
```bash
python app.py
```

Open your browser at: **http://localhost**

---

## Features

- **Dashboard** — Statistics overview of all tables
- **Companies** — Full CRUD (Create, Read, Update, Delete)
- **Jobs** — Full CRUD with company association
- **Applications** — Full CRUD with status tracking
- **Contacts** — Full CRUD with company association
- **Job Match** — Enter your skills and get jobs ranked by match percentage

## Project Structure

```
job_tracker/
├── app.py               # Flask routes
├── database.py          # DB helper functions
├── schema.sql           # Database creation script
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── AI_USAGE.md          # GenAI documentation
├── .env                 # Credentials (not in git)
├── .gitignore
├── templates/           # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── companies.html
│   ├── jobs.html
│   ├── applications.html
│   ├── contacts.html
│   └── job_match.html
└── static/
    └── style.css
```
