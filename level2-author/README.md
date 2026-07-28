# Level 2 — Author

The model writes code. The human is still the runtime. Where Level 1
reasons over one or more datasets *in the chat*, Level 2 takes that same
kind of input — one dataset, two, or here, three — and instead of
answering directly, produces a Python script to do it. The power isn't
the answer this time; it's having the model develop the code for you.

- **`merge.py`** — reads the shared `jobs.csv`, `candidates.csv`, and
  `enrichment.db` (one directory up), joins all three, prints a
  reconciliation summary, folds in the same pipeline analysis Level 1 did
  by hand, and writes both `merged.html` and `merged.xlsx`.

This came from a spec like: *"Take these two CSVs, merge them with the
SQL (Structured Query Language) data, and produce an HTML and an Excel
file."* The same chat window and the same model that gave you the Level 1
analysis — asked for a tool instead of an answer. See the root
[README](../README.md) and [`presentation.html`](../presentation.html)
for the exact spec.

## Why code, not another chat message

This is the classic *"I have to prepare this report every Monday"*
scenario. Pasting three files into a chat and hoping the model resolves
the same name mismatches the same way, every single week, is Level 1's
failure mode stretched out over time — see the "not recommended" flavor
of Level 1 in [`level1-analyst/prompt.md`](../level1-analyst/prompt.md).
A script doesn't improvise: same three inputs in, same join logic, same
reconciliation, same two files out, every Monday. That determinism —
not a smarter answer — is the entire reason to ask for code instead of
asking the question again.

## Level 1's capability, now inside the automation

Level 1's whole job was reasoning over one table by hand: how are
candidates distributed across stages, and is anything inconsistent.
`merge.py` doesn't drop that when it starts joining sources — it absorbs
it. The same stage-count and on-hold-bottleneck check from
[`analysis.md`](../level1-analyst/analysis.md) now runs as one more step
in the script (step 6b), computed with pandas instead of asked for in a
separate chat message, and written into both output files alongside the
merged view. Nothing about the *reasoning* changed — only who's running it,
and how often.

## Why pandas is doing more than "load two CSVs"

The read/query/merge steps are the small part. What makes this a
reasonable tool to hand off, instead of a one-off script, is what the same
library does in three more lines each:

- **One API, many shapes.** `pd.read_csv`, `pd.read_sql_query`, and
  `pd.read_excel` all return the same kind of object — a DataFrame — so a
  flat file and a live database end up interchangeable once they're loaded.
- **`.merge()` is a real relational join** (inner/left/right/outer) without
  writing SQL by hand once the data's in memory — see step 3 and step 4.
- **Boolean masks filter thousands of rows as fast as one.** `stage.isin([...])`
  or `status == "On Hold"` (step 5, step 6b) replace a manual loop-and-check
  entirely.
- **`.groupby()` turns a tally into one line.** The stage-count breakdown
  that used to be a sentence in `analysis.md` is `value_counts()` here.
- **Output format is a parameter, not a rewrite.** The same DataFrame
  writes to `.to_csv()`, `.to_html()`, `.to_excel()`, or `.to_sql()` —
  swapping formats doesn't touch the logic above it.

## Run it

```bash
pip install pandas openpyxl
python merge.py
```

`merged.html` and `merged.xlsx` are regenerated on every run — they're
build artifacts, not source, and are excluded via `.gitignore`.

## What Level 2 doesn't do

A human still has to run this script, point it at the right files, open
`merged.html` or `merged.xlsx` afterward, and decide what to do with the
result. If the join is wrong or a path is off, the human debugs it — the
model wrote the tool, but it isn't the one operating it. That gap between
"wrote it" and "ran it" is what disappears at [Level 3](../level3-agent/README.md).
