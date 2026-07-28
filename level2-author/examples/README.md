# More elaborate Level 2 examples

`merge.py` (one directory up) is the spine of the Level 2 story: read
three sources, join them, reconcile the mess, write two files. These two
scripts are here to answer a fair question - "okay, but what else can
Python actually do for us?" - with something closer to what an Applicant
Tracking System (ATS) administrator builds in practice: not another join,
but a small business-rules engine over the data.

Both are additive: they read the shared `jobs.csv`/`candidates.csv` at
the repo root, plus a small synthetic input file local to this folder,
and don't touch or depend on `merge.py`'s output.

## `recruiter_assignment_engine.py`

The motivating case: a requisition (req) opens with no recruiter
assigned yet. Historically, someone picked one by memory - "Nina usually
takes Engineering." This script replaces that memory with a rule cascade
over `recruiter_assignments.csv` (22 historical filled reqs, synthetic):
exact department-and-location match first, then department-only, then
location-only, then whoever's historical load is lightest. Run against
the 7 currently open reqs in the shared `jobs.csv`, it recommends a
recruiter for every one of them and shows which rule fired for each -
see [`recommendation output`](#what-real-output-looks-like) below.

## `stage_escalation_report.py`

The motivating case: a candidate has been sitting in Screen for three
weeks and nobody flagged it. This script applies a Service Level
Agreement (SLA) per stage (Applied: 5 days, Screen: 7, Interview: 10,
Offer: 3) against `stage_aging.csv` (synthetic days-in-stage, standing in
for a real timestamp an ATS would expose) and ranks everyone over their
limit by how far over they are - not just who's been in the pipeline
longest overall.

## Run them

```bash
pip install pandas
python recruiter_assignment_engine.py
python stage_escalation_report.py
```

Each prints its findings and writes a CSV (`recruiter_recommendations.csv`,
`escalation_report.csv`) - both gitignored, regenerated every run.

## What real output looks like

Recruiter engine, run against the real data in this repo: 5 of 7 open
reqs matched on department + location, 1 fell back to department-only,
1 to location-only - the full fallback rule never had to fire this time.

Escalation report: 7 of 25 candidates are over their stage's SLA, topped
by a Customer Success candidate 4 days past the Applied limit and a
Sales candidate 4 days past the Screen limit - spread across seven
different departments, meaning this isn't one team's problem.
