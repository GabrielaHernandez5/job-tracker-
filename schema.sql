-- ============================================================
-- Job Application Tracker - Database Schema
-- Run: mysql -u root -p job_tracker < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS job_tracker;
USE job_tracker;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;

-- ── 1. Companies ──────────────────────────────────────────────
CREATE TABLE companies (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    industry    VARCHAR(100),
    website     VARCHAR(255),
    location    VARCHAR(150),
    notes       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── 2. Jobs ───────────────────────────────────────────────────
CREATE TABLE jobs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    company_id      INT NOT NULL,
    title           VARCHAR(150) NOT NULL,
    description     TEXT,
    required_skills TEXT,
    salary_range    VARCHAR(100),
    location        VARCHAR(150),
    posted_date     DATE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- ── 3. Applications ───────────────────────────────────────────
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

-- ── 4. Contacts ───────────────────────────────────────────────
CREATE TABLE contacts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    company_id  INT,
    name        VARCHAR(150) NOT NULL,
    role        VARCHAR(100),
    email       VARCHAR(150),
    phone       VARCHAR(30),
    linkedin    VARCHAR(255),
    notes       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL
);

-- ── Seed data for testing ──────────────────────────────────────
INSERT INTO companies (name, industry, website, location, notes) VALUES
('Google', 'Technology', 'https://careers.google.com', 'Mountain View, CA', 'Dream company'),
('Microsoft', 'Technology', 'https://careers.microsoft.com', 'Redmond, WA', 'Great benefits'),
('Shopify', 'E-Commerce', 'https://www.shopify.com/careers', 'Ottawa, Canada', 'Remote-friendly');

INSERT INTO jobs (company_id, title, description, required_skills, salary_range, location, posted_date) VALUES
(1, 'Backend Engineer', 'Build scalable APIs', 'Python, MySQL, Flask, REST', '$120k-$150k', 'Remote', CURDATE()),
(2, 'Full Stack Developer', 'Build web applications', 'Python, HTML, CSS, JavaScript, MySQL', '$110k-$140k', 'Redmond, WA', CURDATE()),
(3, 'Software Developer', 'Work on e-commerce platform', 'Python, Flask, MySQL, HTML', '$100k-$130k', 'Remote', CURDATE());

INSERT INTO applications (job_id, applied_date, status, resume_version, notes) VALUES
(1, CURDATE(), 'Applied', 'v2.1', 'Applied through LinkedIn'),
(2, CURDATE(), 'Interview', 'v2.0', 'Phone screen scheduled');

INSERT INTO contacts (company_id, name, role, email, phone, linkedin, notes) VALUES
(1, 'Jane Smith', 'Recruiter', 'jane@google.com', '555-0101', 'linkedin.com/in/janesmith', 'Very responsive'),
(2, 'Bob Johnson', 'Engineering Manager', 'bob@microsoft.com', '555-0202', 'linkedin.com/in/bobjohnson', 'Met at career fair');
