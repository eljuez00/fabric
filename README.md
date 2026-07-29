# fabric

> Synthetic data, built to illustrate a concept for a talk. Every name,
> email, company, and record in this repo is invented. Nothing here
> refers to a real person, employer, or product.

A demo for a talk about **agentic development**, using a talent-acquisition
scenario as the vehicle. Three levels of what a Large Language Model (LLM)
can be asked to do, on the same dataset — see [`presentation.html`](presentation.html)
for the full talk.

**Nothing runs live and no model is called at presentation time.** Every
script was written and run once during the build; its real output is
what's checked in and shown on the slides.

## The spine

| Level | Role | Model now owns | You still own |
|---|---|---|---|
| [1 — Analyst](level1-analyst/) | reasons over your data | the thinking | get the data in, act on the answer |
| [2 — Author](level2-author/) | writes the code too | thinking + **code** | run it: feed files, execute, debug |
| [3 — Agent](level3-agent/) | runs it too, full agentic access | thinking + code + **execution** | — |

Levels 1 and 2 are the same chat, same model — only the *ask* changes
(an answer vs. a tool). Level 3 changes *access*: the model lives in your
environment instead of a chat box, and can skip the export step entirely
via a direct WSDL/SOAP call — see [`level3-agent/`](level3-agent/).

## Shared data

`jobs.csv`, `candidates.csv`, and `enrichment.db` (repo root) feed every
level. The two CSVs stand in for exported reports; `enrichment.db` stands
in for a live system (a generic ATS/CRM/HRIS). The join between them is
deliberately imperfect — some names don't match cleanly, some candidates
have no profile, some profiles match nobody — and `level2-author/merge.py`
surfaces that instead of hiding it. `generate_sample_data.py` is how the
three files were generated; you don't need to run it.

## Run it

```bash
pip install pandas openpyxl
python level2-author/merge.py
```

Prints a reconciliation summary (19/25 matched, 6 unmatched, 5 profiles
unused) and the merged table, then writes `merged.html` + `merged.xlsx`
into `level2-author/` (gitignored — regenerated each run).

For more than a join, see [`level2-author/examples/`](level2-author/examples/) —
a recruiter assignment rules engine and a fuzzy-match suggester for the
reconciliation gap above, both real runs against this repo's data.

## Bonus

The deeper win beyond Level 3: skip the export/report step entirely by
calling the source system's WSDL/SOAP endpoint directly. See
[`level3-agent/bonus-direct-wsdl.md`](level3-agent/bonus-direct-wsdl.md).

## License

MIT — see [`LICENSE`](LICENSE).
