"""
merge.py
--------
Level 2 - Author. The model wrote this script from a plain-English spec
(see the root README and presentation.html for the spec that produced it).
It is a TOOL, not an action: a human still has to run it, point it at the
right files, and do something with what comes out the other end.

It reads three shared sources - two flat files and a SQLite database - and
produces one merged view, written out as both HTML and Excel:

    ../jobs.csv         -> pandas   (a flat file - an exported report)
    ../candidates.csv   -> pandas   (a flat file - an exported report)
    ../enrichment.db     -> SQL      (a live system you could query directly)

Each source gets the tool that fits its shape: pandas for the two CSVs, a
real SQL SELECT for the database. That recognition is the point, not the
Python itself.

The candidate names in candidates.csv and the profile names in
enrichment.db do not all match cleanly. This script does NOT paper over
that - it computes a reconciliation summary and prints it before it ever
writes the "clean" merged view, so a human can see exactly what matched,
what didn't, and what's left over.

Run with:  python merge.py
Requires:  pandas, openpyxl   (sqlite3 is part of the standard library)
"""

import sqlite3
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent

# ---------------------------------------------------------------------------
# 1. Load the two exported reports with pandas.
# ---------------------------------------------------------------------------
jobs = pd.read_csv(ROOT / "jobs.csv")
candidates = pd.read_csv(ROOT / "candidates.csv")

# ---------------------------------------------------------------------------
# 2. Query the live system (enrichment.db) with a real SQL SELECT.
#    This is the "reach into the live system" half of the demo - no export
#    step, no waiting on a scheduled report, just a query.
# ---------------------------------------------------------------------------
SELECT_PROFILES_SQL = """
    SELECT profile_id, name, current_title, current_company, years_experience
    FROM profiles
"""

conn = sqlite3.connect(ROOT / "enrichment.db")
profiles = pd.read_sql_query(SELECT_PROFILES_SQL, conn)
conn.close()

# ---------------------------------------------------------------------------
# 3. Join jobs -> candidates first. Every candidate applied to exactly one
#    req, so this half is a clean one-to-one merge on job_id.
# ---------------------------------------------------------------------------
candidates_with_jobs = candidates.merge(
    jobs, on="job_id", how="left", suffixes=("", "_job")
)

# ---------------------------------------------------------------------------
# 4. Join candidates -> profiles on full name. This is the messy half.
#    Real-world identity data doesn't line up perfectly: "Jon Smith" in the
#    tracker vs "Jonathan Smith" in the profile system, candidates nobody
#    has a profile for, and profiles that don't belong to any candidate.
#    A naive exact-name join surfaces all of that - which is exactly what
#    we want it to do, rather than silently dropping or guessing.
# ---------------------------------------------------------------------------
merged = candidates_with_jobs.merge(
    profiles, left_on="full_name", right_on="name", how="left", suffixes=("", "_profile")
)

# ---------------------------------------------------------------------------
# 5. Reconciliation summary - compute it, don't assume it. This is the
#    number a human has to look at before trusting the merged view below.
# ---------------------------------------------------------------------------
matched_mask = merged["name"].notna()
matched = merged[matched_mask]
unmatched = merged[~matched_mask]

matched_profile_ids = set(matched["profile_id"])
unused_profiles = profiles[~profiles["profile_id"].isin(matched_profile_ids)]

print("=" * 60)
print("RECONCILIATION SUMMARY")
print("=" * 60)
print(f"Candidates total:                    {len(candidates)}")
print(f"Candidates matched to a profile:     {len(matched)}")
print(f"Candidates with NO matching profile: {len(unmatched)}")
if len(unmatched):
    for name in unmatched["full_name"]:
        print(f"    - {name}")
print(f"Profiles on file total:              {len(profiles)}")
print(f"Profiles unused by any candidate:    {len(unused_profiles)}")
if len(unused_profiles):
    for name in unused_profiles["name"]:
        print(f"    - {name}")
print("=" * 60)
print(
    "\nNote: these are close-but-not-identical names (e.g. 'Jon Smith' vs\n"
    "'Jonathan Smith') that an exact-match join won't catch. A fuzzy-match\n"
    "step could close some of this gap, but it would also introduce false\n"
    "positives - which is exactly the kind of judgment call that stays with\n"
    "a human, not the model that wrote this join.\n"
)

# ---------------------------------------------------------------------------
# 6. The payoff: one merged talent view, one row per candidate, with the
#    req they applied to and their profile snapshot (blank where unmatched).
# ---------------------------------------------------------------------------
talent_view = merged[
    [
        "candidate_id",
        "full_name",
        "email",
        "job_id",
        "title",
        "department",
        "location",
        "stage",
        "current_title",
        "current_company",
        "years_experience",
    ]
].rename(columns={"title": "job_title"})

print("MERGED TALENT VIEW")
print("=" * 60)
print(talent_view.to_string(index=False))

# ---------------------------------------------------------------------------
# 7. Write the merged view out as BOTH an HTML file and an Excel file.
#    A human still has to run this script and do something with these two
#    files - that's the honest limit of Level 2.
# ---------------------------------------------------------------------------
html_path = HERE / "merged.html"
talent_view.to_html(html_path, index=False, na_rep="")
print(f"\nSaved HTML view to {html_path.name}")

xlsx_path = HERE / "merged.xlsx"
talent_view.to_excel(xlsx_path, index=False, sheet_name="merged", na_rep="")
print(f"Saved Excel view to {xlsx_path.name}")
