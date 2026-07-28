"""
merge.py
--------
Level 2 - Author. The model wrote this script from a plain-English spec
(see the root README and presentation.html for the spec that produced it).
It is a TOOL, not an action: a human still has to run it, point it at the
right files, and do something with what comes out the other end.

It reads three shared sources - two flat files and a SQLite database - and
produces one merged view, written out as both an HTML (HyperText Markup
Language) file and an Excel file:

    ../jobs.csv         -> pandas  (a flat file - an exported report)
    ../candidates.csv   -> pandas  (a flat file - an exported report)
    ../enrichment.db     -> SQL     (a live system you could query directly)

Each source gets the tool that fits its shape: pandas for the two CSVs, a
real SQL (Structured Query Language) SELECT for the database. That
recognition is the point, not the Python itself - though pandas is doing
real work here that's worth naming:

    - one library reads three different shapes of data (CSV, SQL, and it
      can just as easily read Excel, JSON, or Parquet)
    - .merge() is a full relational join - inner/left/right/outer - without
      writing SQL by hand once the data is loaded
    - boolean masks (see step 5 and step 6b below) filter and slice
      thousands of rows as fast as one row, with no explicit loop
    - .groupby() turns "how many candidates are in each stage" from a
      manual tally into one line
    - the same DataFrame writes back out to .to_csv(), .to_html(),
      .to_excel(), or .to_sql() - the output format is a parameter, not a
      rewrite

The candidate names in candidates.csv and the profile names in
enrichment.db do not all match cleanly. This script does NOT paper over
that - it computes a reconciliation summary and prints it before it ever
writes the "clean" merged view, so a human can see exactly what matched,
what didn't, and what's left over.

This script also folds in what Level 1 did by hand: the pipeline analysis
a human used to paste into a chat and ask about (stage counts, the
on-hold-but-still-active bottleneck) now runs automatically, every time,
as part of the same pipeline - see step 6b. That's Level 1's capability,
absorbed into Level 2's automation.

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
#    req (requisition), so this half is a clean one-to-one merge on job_id.
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
# 6b. Level 1's analysis, folded into the automation.
#     A human used to paste a pipeline export into a chat and ask "how is
#     this distributed, and is anything inconsistent?" That reasoning is
#     mechanical enough to run every time, unattended - a .groupby() for
#     the stage counts, a boolean mask for the bottleneck check - so it's
#     computed here instead of asked for separately.
# ---------------------------------------------------------------------------
stage_counts = candidates["stage"].value_counts().reindex(
    ["Applied", "Screen", "Interview", "Offer"]
)

active_stages = ["Screen", "Interview", "Offer"]
on_hold_with_movement = candidates_with_jobs[
    (candidates_with_jobs["status"] == "On Hold")
    & (candidates_with_jobs["stage"].isin(active_stages))
]
stalled_reqs = on_hold_with_movement.groupby(["job_id", "title"]).size()

print("\n" + "=" * 60)
print("PIPELINE ANALYSIS (Level 1's reasoning, now automated)")
print("=" * 60)
print(stage_counts.to_string())
if len(stalled_reqs):
    print("\nReqs marked On Hold that still have candidates past Applied:")
    for (job_id, title), count in stalled_reqs.items():
        print(f"    - {job_id} {title}: {count} candidate(s) still moving")
print("=" * 60)

# ---------------------------------------------------------------------------
# 7. Write everything out as BOTH an HTML file and an Excel file - the
#    merged view and the pipeline analysis together. A human still has to
#    run this script and do something with these two files - that's the
#    honest limit of Level 2.
# ---------------------------------------------------------------------------
analysis_df = stage_counts.rename("candidate_count").reset_index().rename(
    columns={"index": "stage"}
)

html_path = HERE / "merged.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write("<h2>Merged talent view</h2>\n")
    f.write(talent_view.to_html(index=False, na_rep=""))
    f.write("\n<h2>Pipeline analysis (Level 1, automated)</h2>\n")
    f.write(analysis_df.to_html(index=False))
print(f"\nSaved HTML view to {html_path.name}")

xlsx_path = HERE / "merged.xlsx"
with pd.ExcelWriter(xlsx_path) as writer:
    talent_view.to_excel(writer, index=False, sheet_name="merged", na_rep="")
    analysis_df.to_excel(writer, index=False, sheet_name="pipeline_analysis")
print(f"Saved Excel view to {xlsx_path.name} (sheets: merged, pipeline_analysis)")
