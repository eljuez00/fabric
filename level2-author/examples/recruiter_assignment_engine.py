"""
recruiter_assignment_engine.py
-------------------------------
A more elaborate Level 2 example: a rules-based engine that reads how
past requisitions were staffed and recommends a recruiter for each
currently open requisition that hasn't been assigned one yet.

This is the shape of automation an Applicant Tracking System (ATS)
administrator builds constantly: not a machine-learning model, just a
deterministic cascade of "if this, then that" business rules over
historical data - the kind of thing that's tedious to redo by hand every
time a new req opens, and exactly the kind of thing Level 2 is for.

Inputs:
    ../../jobs.csv                -> the 8 shared reqs (root of the repo)
    recruiter_assignments.csv     -> ~22 historical FILLED reqs, each
                                      already staffed by a recruiter
                                      (synthetic, local to this example)

The rule cascade, tried in order for each open req until one produces a
recommendation:

    1. Exact match: same department AND same location have been staffed
       before -> recommend whoever handled the most of those.
    2. Department-only match: same department, any location -> recommend
       whoever handles that department most.
    3. Location-only match: same location, any department -> recommend
       whoever works that location most.
    4. Fallback: no history at all for this department or location ->
       recommend whoever has the lightest historical load overall, on
       the theory that they have the most bandwidth.

Run with:  python recruiter_assignment_engine.py
Requires:  pandas
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

jobs = pd.read_csv(ROOT / "jobs.csv")
history = pd.read_csv(HERE / "recruiter_assignments.csv")

# Only truly open reqs need a recruiter - a req that's On Hold doesn't.
open_reqs = jobs[jobs["status"] == "Open"].copy()

# Recruiter with the lightest historical load overall - the rule-4
# fallback for a department/location combination with zero history.
overall_counts = history["recruiter"].value_counts()
least_loaded = overall_counts.idxmin()


def recommend(department: str, location: str):
    """Walk the rule cascade for one req and return (recruiter, rule, n)."""
    exact = history[(history["department"] == department) & (history["location"] == location)]
    if len(exact):
        top = exact["recruiter"].value_counts()
        return top.idxmax(), "1: department + location match", int(top.max())

    dept_only = history[history["department"] == department]
    if len(dept_only):
        top = dept_only["recruiter"].value_counts()
        return top.idxmax(), "2: department-only match", int(top.max())

    location_only = history[history["location"] == location]
    if len(location_only):
        top = location_only["recruiter"].value_counts()
        return top.idxmax(), "3: location-only match", int(top.max())

    return least_loaded, "4: fallback - lightest overall load", int(overall_counts.min())


recommendations = []
for _, req in open_reqs.iterrows():
    recruiter, rule, support = recommend(req["department"], req["location"])
    recommendations.append(
        {
            "job_id": req["job_id"],
            "title": req["title"],
            "department": req["department"],
            "location": req["location"],
            "recommended_recruiter": recruiter,
            "rule_applied": rule,
            "supporting_assignments": support,
        }
    )

result = pd.DataFrame(recommendations)

print("=" * 70)
print(f"RECRUITER ASSIGNMENT RECOMMENDATIONS ({len(result)} open reqs, {len(history)} historical assignments)")
print("=" * 70)
print(result.to_string(index=False))

rule_counts = result["rule_applied"].value_counts().sort_index()
print("\nRule usage this run:")
for rule, count in rule_counts.items():
    print(f"    {rule}: {count} req(s)")
never_needed = {"1", "2", "3", "4"} - {r[0] for r in result["rule_applied"]}
if never_needed:
    print(f"Rules never triggered this run: {sorted(never_needed)}")

output_path = HERE / "recruiter_recommendations.csv"
result.to_csv(output_path, index=False)
print(f"\nSaved {len(result)} recommendations to {output_path.name}")
