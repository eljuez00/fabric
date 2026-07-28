"""
stage_escalation_report.py
----------------------------
A second, more elaborate Level 2 example: a Service Level Agreement (SLA)
escalation report. Every stage a candidate sits in has an implicit clock
- a candidate stuck in Screen for three weeks is a problem whether or not
anyone noticed. This script makes that clock explicit and automatic
instead of something a recruiter has to remember to check.

Inputs:
    ../../candidates.csv   -> the 25 shared candidates (root of the repo)
    ../../jobs.csv         -> the 8 shared reqs, for department context
    stage_aging.csv         -> how many days each candidate has been in
                                their CURRENT stage (synthetic, local to
                                this example - a real ATS exposes this as
                                a timestamp; this stands in for that)

The rule: every stage has a maximum number of days before it counts as
overdue. Offers should move fast; Applied can sit a little longer before
it's a problem. Anyone over their stage's limit gets flagged, ranked by
how far over they are - not just who happens to be oldest in absolute
terms.

Run with:  python stage_escalation_report.py
Requires:  pandas
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

candidates = pd.read_csv(ROOT / "candidates.csv")
jobs = pd.read_csv(ROOT / "jobs.csv")
aging = pd.read_csv(HERE / "stage_aging.csv")

# Business rule: max days allowed in each stage before it's overdue.
SLA_DAYS = {
    "Applied": 5,
    "Screen": 7,
    "Interview": 10,
    "Offer": 3,
}

merged = candidates.merge(jobs, on="job_id", how="left").merge(aging, on="candidate_id", how="left")

merged["sla_days"] = merged["stage"].map(SLA_DAYS)
merged["days_over_sla"] = merged["days_in_current_stage"] - merged["sla_days"]
overdue = merged[merged["days_over_sla"] > 0].sort_values("days_over_sla", ascending=False)

print("=" * 70)
print(f"STAGE ESCALATION REPORT ({len(overdue)} of {len(merged)} candidates over SLA)")
print("=" * 70)
report_cols = [
    "candidate_id", "full_name", "department", "stage",
    "days_in_current_stage", "sla_days", "days_over_sla",
]
print(overdue[report_cols].to_string(index=False))

print("\nOverdue by department:")
print(overdue["department"].value_counts().to_string())

if len(overdue):
    worst = overdue.iloc[0]
    print(
        f"\nMost overdue: {worst['full_name']} ({worst['candidate_id']}) - "
        f"{worst['days_in_current_stage']} days in {worst['stage']}, "
        f"{worst['days_over_sla']} day(s) past the {worst['sla_days']}-day limit."
    )

output_path = HERE / "escalation_report.csv"
overdue[report_cols].to_csv(output_path, index=False)
print(f"\nSaved {len(overdue)} overdue candidates to {output_path.name}")
