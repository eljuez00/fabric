"""
fuzzy_match_suggestions.py
----------------------------
A third Level 2 example, and the most direct payoff of the reconciliation
problem this whole repo is built around: merge.py's exact-name join
leaves 6 candidates unmatched and 5 profiles unused, on purpose, rather
than guess. This script takes that gap and does the one thing a human
would do next by hand - eyeball the leftovers and ask "are any of these
actually the same person, just spelled differently?" - and makes it
repeatable.

It needs no new data. Same two shared sources as merge.py:

    ../../candidates.csv   -> the unmatched candidates
    ../../enrichment.db     -> the unused profiles

For every unmatched candidate, it scores every unused profile by name
similarity using difflib.SequenceMatcher - part of the Python standard
library, no extra dependency - and keeps the best score. Anything above
a threshold gets surfaced as a SUGGESTED match; anything below it is
reported as genuinely unmatched, still.

This does NOT auto-merge anything. A name-similarity score is a hint, not
a fact - "Jon Smith" and "Jonathan Smith" are very likely the same person,
but two different people can share a very similar name too. The output is
a short list for a human to confirm, same as merge.py's reconciliation
summary was - Level 2 makes the comparison, Level 2 does not make the
call.

Run with:  python fuzzy_match_suggestions.py
Requires:  pandas   (difflib and sqlite3 are part of the standard library)
"""

import difflib
import sqlite3
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

# Threshold above which a suggestion is worth a human's time to look at.
# Chosen by looking at real scores from this data: the three genuine
# near-misses score 0.78-0.84, the closest false lead tops out at 0.44 -
# there's a wide, clean gap to sit a threshold in.
SUGGEST_THRESHOLD = 0.6

candidates = pd.read_csv(ROOT / "candidates.csv")
conn = sqlite3.connect(ROOT / "enrichment.db")
profiles = pd.read_sql_query("SELECT profile_id, name FROM profiles", conn)
conn.close()

# Reproduce merge.py's exact-name join just far enough to find the two
# leftover pools: candidates with no profile, profiles nobody claimed.
merged = candidates.merge(profiles, left_on="full_name", right_on="name", how="left")
unmatched = merged[merged["name"].isna()]
matched_profile_ids = set(merged.loc[merged["name"].notna(), "profile_id"])
unused = profiles[~profiles["profile_id"].isin(matched_profile_ids)]


def best_match(name: str):
    """Score `name` against every unused profile, return the closest one."""
    scored = [
        (row["name"], difflib.SequenceMatcher(None, name.lower(), row["name"].lower()).ratio())
        for _, row in unused.iterrows()
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[0]


suggestions = []
for _, candidate in unmatched.iterrows():
    profile_name, score = best_match(candidate["full_name"])
    suggestions.append(
        {
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["full_name"],
            "closest_unused_profile": profile_name,
            "similarity": round(score, 3),
            "suggested": score >= SUGGEST_THRESHOLD,
        }
    )

result = pd.DataFrame(suggestions).sort_values("similarity", ascending=False)

print("=" * 70)
print(f"FUZZY MATCH SUGGESTIONS ({len(unmatched)} unmatched candidates, {len(unused)} unused profiles)")
print("=" * 70)
print(result.to_string(index=False))

suggested = result[result["suggested"]]
print(f"\n{len(suggested)} of {len(result)} unmatched candidates have a suggested match:")
for _, row in suggested.iterrows():
    print(f"    {row['candidate_name']} -> {row['closest_unused_profile']} ({row['similarity']})")
print(
    f"\n{len(result) - len(suggested)} have no match above the {SUGGEST_THRESHOLD} threshold - "
    "still genuinely unmatched, not just unlucky with spelling."
)
print(
    "\nNothing above is applied automatically - these are suggestions for a\n"
    "human recruiter or admin to confirm, the same judgment call merge.py's\n"
    "reconciliation summary already refused to make on its own."
)

output_path = HERE / "fuzzy_match_suggestions.csv"
result.to_csv(output_path, index=False)
print(f"\nSaved {len(result)} rows to {output_path.name}")
