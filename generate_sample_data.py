"""
generate_sample_data.py
------------------------
One-time data generator for the fabric demo.

Everything here is invented for a talk: names, companies, emails, ids.
Nothing in this file (or anywhere in this repo) refers to a real person,
employer, or vendor.

Running this script writes the three "source" files shared across all
three levels of the demo:

    jobs.csv         - open requisitions      (an exported report)
    candidates.csv   - applicant tracker rows (an exported report)
    enrichment.db     - a small SQLite table of "profiles on file"
                         (stands in for a live system you'd query directly)

The join between candidates.csv and enrichment.db is deliberately messy on
purpose - a few names match cleanly, a few are close-but-not-identical
("Jon Smith" vs "Jonathan Smith"), a few candidates have no profile at all,
and a couple of profiles belong to nobody in candidates.csv. That mess is
the whole point of level2-author/merge.py - see the README.

You do not need to run this yourself. jobs.csv, candidates.csv, and
enrichment.db are already committed to the repo. This script is included
so the data generation itself is transparent and reproducible.
"""

import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. Open requisitions (jobs.csv) - the kind of report a recruiting team
#    might export from their ATS once a week.
# ---------------------------------------------------------------------------
JOBS = [
    ("J001", "Software Engineer", "Engineering", "Remote", "Open"),
    ("J002", "Product Manager", "Product", "Austin, TX", "Open"),
    ("J003", "Data Analyst", "Analytics", "Remote", "Open"),
    ("J004", "Recruiter", "People", "Chicago, IL", "Open"),
    ("J005", "UX Designer", "Design", "Remote", "Open"),
    ("J006", "Sales Development Rep", "Sales", "New York, NY", "Open"),
    ("J007", "DevOps Engineer", "Engineering", "Remote", "On Hold"),
    ("J008", "Customer Success Manager", "Customer Success", "Austin, TX", "Open"),
]

# ---------------------------------------------------------------------------
# 2. Candidates (candidates.csv) - another exported report, one row per
#    applicant. Names are intentionally silly/placeholder-style so nobody
#    mistakes this for real people.
# ---------------------------------------------------------------------------
CANDIDATES = [
    ("C001", "Avery Example", "J001", "Applied"),
    ("C002", "Jordan Sample", "J001", "Screen"),
    ("C003", "Jon Smith", "J001", "Interview"),
    ("C004", "Casey Test", "J002", "Applied"),
    ("C005", "Riley Demo", "J002", "Screen"),
    ("C006", "Morgan Fake", "J002", "Offer"),
    ("C007", "Cate Nguyen", "J003", "Applied"),
    ("C008", "Drew Placeholder", "J003", "Screen"),
    ("C009", "Sam Synthetic", "J003", "Interview"),
    ("C010", "Taylor Mock", "J004", "Applied"),
    ("C011", "Rob Diaz", "J004", "Screen"),
    ("C012", "Jamie Sample", "J004", "Applied"),
    ("C013", "Quinn Example", "J005", "Interview"),
    ("C014", "Alex Test", "J005", "Applied"),
    ("C015", "Bailey Demo", "J005", "Offer"),
    ("C016", "Skyler Fake", "J006", "Applied"),
    ("C017", "Reese Placeholder", "J006", "Screen"),
    ("C018", "Harper Synthetic", "J006", "Applied"),
    ("C019", "Emerson Mock", "J007", "Screen"),
    ("C020", "Finley Sample", "J007", "Interview"),
    ("C021", "Dana Example", "J008", "Applied"),
    ("C022", "Micah Test", "J008", "Screen"),
    ("C023", "Jess Nolan", "J008", "Applied"),
    ("C024", "Toby Grant", "J002", "Applied"),
    ("C025", "Wynn Osei", "J003", "Screen"),
]


def make_email(full_name: str) -> str:
    """first.last@example.com - every address in this repo is @example.com."""
    first, last = full_name.lower().split(" ", 1)
    last = last.replace(" ", "")
    return f"{first}.{last}@example.com"


# ---------------------------------------------------------------------------
# 3. Profiles on file (enrichment.db) - a generic "profiles" table in a
#    SQLite database, standing in for a live system an agent could query
#    directly instead of waiting on someone to export a report.
#
#    Three deliberate mismatches with candidates.csv:
#      Jon Smith        (candidate) vs Jonathan Smith  (profile)
#      Cate Nguyen      (candidate) vs Catherine Nguyen (profile)
#      Rob Diaz         (candidate) vs Robert Diaz     (profile)
#
#    Six candidates with no profile at all:
#      Jon Smith, Cate Nguyen, Rob Diaz, Jess Nolan, Toby Grant, Wynn Osei
#
#    Five profiles that match no candidate (the three name variants above,
#    plus two that simply belong to nobody in candidates.csv):
#      Jonathan Smith, Catherine Nguyen, Robert Diaz, Priya Chen, Malik Owens
# ---------------------------------------------------------------------------
PROFILES = [
    ("P001", "Avery Example", "Software Engineer II", "Acme Corp", 4),
    ("P002", "Jordan Sample", "Senior Product Analyst", "Globex", 6),
    ("P003", "Jonathan Smith", "Software Engineer", "Initech", 5),
    ("P004", "Casey Test", "Product Manager", "Acme Corp", 7),
    ("P005", "Riley Demo", "Associate Product Manager", "Globex", 3),
    ("P006", "Morgan Fake", "Senior Product Manager", "Initech", 8),
    ("P007", "Catherine Nguyen", "Data Analyst", "Acme Corp", 4),
    ("P008", "Drew Placeholder", "Business Intelligence Analyst", "Globex", 5),
    ("P009", "Sam Synthetic", "Data Analyst II", "Initech", 3),
    ("P010", "Taylor Mock", "Technical Recruiter", "Acme Corp", 6),
    ("P011", "Robert Diaz", "Senior Recruiter", "Globex", 9),
    ("P012", "Jamie Sample", "Recruiting Coordinator", "Initech", 2),
    ("P013", "Quinn Example", "Senior UX Designer", "Acme Corp", 7),
    ("P014", "Alex Test", "UX Designer", "Globex", 3),
    ("P015", "Bailey Demo", "Product Designer", "Initech", 5),
    ("P016", "Skyler Fake", "Sales Development Rep", "Acme Corp", 2),
    ("P017", "Reese Placeholder", "Account Executive", "Globex", 4),
    ("P018", "Emerson Mock", "DevOps Engineer", "Initech", 6),
    ("P019", "Finley Sample", "Site Reliability Engineer", "Acme Corp", 5),
    ("P020", "Harper Synthetic", "Sales Development Rep", "Initech", 3),
    ("P021", "Dana Example", "Customer Success Manager", "Acme Corp", 5),
    ("P022", "Micah Test", "Customer Success Associate", "Globex", 2),
    ("P023", "Priya Chen", "Customer Success Manager", "Globex", 4),
    ("P024", "Malik Owens", "Software Engineer", "Initech", 8),
]


def write_jobs_csv():
    path = HERE / "jobs.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["job_id", "title", "department", "location", "status"])
        writer.writerows(JOBS)
    print(f"wrote {path.name} ({len(JOBS)} rows)")


def write_candidates_csv():
    path = HERE / "candidates.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "full_name", "email", "job_id", "stage"])
        for candidate_id, full_name, job_id, stage in CANDIDATES:
            writer.writerow([candidate_id, full_name, make_email(full_name), job_id, stage])
    print(f"wrote {path.name} ({len(CANDIDATES)} rows)")


def write_enrichment_db():
    path = HERE / "enrichment.db"
    if path.exists():
        path.unlink()  # start clean each time this generator runs
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE profiles (
            profile_id       TEXT PRIMARY KEY,
            name              TEXT NOT NULL,
            current_title     TEXT,
            current_company   TEXT,
            years_experience  INTEGER
        )
        """
    )
    conn.executemany(
        "INSERT INTO profiles VALUES (?, ?, ?, ?, ?)",
        PROFILES,
    )
    conn.commit()
    conn.close()
    print(f"wrote {path.name} ({len(PROFILES)} rows in table 'profiles')")


if __name__ == "__main__":
    write_jobs_csv()
    write_candidates_csv()
    write_enrichment_db()
    print("\nSample data generated.")
    print("Next: build level1-analyst/candidates.xlsx, then run level2-author/merge.py")
