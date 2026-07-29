# More elaborate Level 2 examples

`merge.py` (one directory up) is the spine of the Level 2 story: read
three sources, join them, reconcile the mess, write two files. These two
scripts are here to answer a fair question - "okay, but what else can
Python actually do for us?" - with something closer to what an Applicant
Tracking System (ATS) administrator builds in practice: not another join,
but a small business-rules engine over the data.

Both are additive: they read the shared `jobs.csv`/`candidates.csv`/
`enrichment.db` at the repo root, plus - for the recruiter engine only -
one small synthetic input file local to this folder. Neither touches or
depends on `merge.py`'s output.

## `recruiter_assignment_engine.py`

The motivating case: a requisition (req) opens with no recruiter
assigned yet. Historically, someone picked one by memory - "Nina usually
takes Engineering." This script replaces that memory with a rule cascade
over `recruiter_assignments.csv` (22 historical filled reqs, synthetic):
exact department-and-location match first, then department-only, then
location-only, then whoever's historical load is lightest. Run against
the 7 currently open reqs in the shared `jobs.csv`, it recommends a
recruiter for every one of them and shows which rule fired for each.

## `fuzzy_match_suggestions.py`

The motivating case is the one this whole repo is already built around:
`merge.py`'s exact-name join leaves 6 candidates unmatched and 5 profiles
unused, on purpose, rather than guess at a join. This script picks that
gap back up and does what a human would do next by hand - eyeball the
leftovers for a likely typo - using `difflib.SequenceMatcher` (Python's
standard library, no new dependency) to score every unmatched candidate
against every unused profile. It needs no new data: same two shared
sources as `merge.py`. Anything above a similarity threshold gets
surfaced as a suggestion; nothing is merged automatically - a human still
confirms, the same judgment call the reconciliation summary already
refused to make on its own.

## Run them

```bash
pip install pandas
python recruiter_assignment_engine.py
python fuzzy_match_suggestions.py
```

Each prints its findings and writes a CSV (`recruiter_recommendations.csv`,
`fuzzy_match_suggestions.csv`) - both gitignored, regenerated every run.

## What real output looks like

Recruiter engine, run against the real data in this repo: 5 of 7 open
reqs matched on department + location, 1 fell back to department-only,
1 to location-only - the full fallback rule never had to fire this time.

Fuzzy match suggestions: of the 6 unmatched candidates, 3 score
0.78-0.84 against an unused profile - `Jon Smith` / `Jonathan Smith`,
`Cate Nguyen` / `Catherine Nguyen`, `Rob Diaz` / `Robert Diaz` - a clean
gap above the closest false lead, which tops out at 0.44. The other 3
unmatched candidates score below the threshold against everything:
genuinely no profile on file, not just an unlucky spelling.
