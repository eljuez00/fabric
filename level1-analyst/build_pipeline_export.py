"""
build_pipeline_export.py
-------------------------
Not part of the Level 1 narrative - this just produces the Excel file that
Level 1 starts from. In real life this would be a report someone exported
from an ATS; here, it's built from the same shared jobs.csv/candidates.csv
used by every level of this demo.

Level 1 is deliberately the simplest cut of the data: candidates joined to
the req they applied to. No SQL, no enrichment lookup, no join reconciliation
- that complexity shows up starting at Level 2. Level 1 is what a human
already has in hand before any of this starts.
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent

jobs = pd.read_csv(ROOT / "jobs.csv")
candidates = pd.read_csv(ROOT / "candidates.csv")

pipeline = candidates.merge(jobs, on="job_id", how="left").rename(
    columns={"title": "job_title"}
)
pipeline = pipeline[
    ["candidate_id", "full_name", "email", "job_id", "job_title", "department", "location", "stage"]
]

output_path = HERE / "candidates.xlsx"
pipeline.to_excel(output_path, index=False, sheet_name="pipeline")
print(f"wrote {output_path.name} ({len(pipeline)} rows)")
