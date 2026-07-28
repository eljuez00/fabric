# Level 2 — Author

The model writes code. The human is still the runtime.

- **`merge.py`** — reads the shared `jobs.csv`, `candidates.csv`, and
  `enrichment.db` (one directory up), joins all three, prints a
  reconciliation summary, and writes the merged view out as both
  `merged.html` and `merged.xlsx`.

This came from a spec like: *"Take these two CSVs, merge them with the
SQL data, and produce an HTML and an Excel file."* The same chat window
and the same model that gave you the Level 1 analysis — asked for a tool
instead of an answer. See the root [README](../README.md) and
[`presentation.html`](../presentation.html) for the exact spec.

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
