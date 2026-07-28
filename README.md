# fabric

> Synthetic data, built to illustrate a concept for a talk. Every name,
> email, company, and record in this repo is invented. Nothing here
> refers to a real person, employer, or product.

`fabric` is a small, self-contained demo for a talk about **agentic
development**. It uses a talent-acquisition scenario as the concrete
vehicle, but the point isn't recruiting software — it's a journey across
three levels of what an LLM can be asked to do, and how much of the work
the human still has to do at each one.

**Nothing in this repo runs live during the talk and no model is called
at presentation time.** Every script here was written once, run once
during the build, and its real output — the numbers, the tables, the
files — is what's checked in and shown on the slides. See
[`presentation.html`](presentation.html) for the full walkthrough.

## The spine: three levels, one thing handed over at each

The through-line of the talk: at each level, the human hands over one
more thing, and does less of the surrounding lifting.

| Level | Role | What's handed over | What the human still does |
|---|---|---|---|
| [1 — Analyst](level1-analyst/) | reasons over data you bring it | analysis | pulls the data, reads the answer, decides what to do |
| [2 — Author](level2-author/) | writes code from a spec | the code-writing | runs the tool, feeds it files, moves the output, debugs errors |
| [3 — Agent](level3-agent/) | writes **and runs** code, with local access | the doing | describes intent, verifies output |

**Levels 1 and 2 happen in the same chat window, with the same model** —
what changes between them is only what you asked *for*: an answer, or a
tool. Level 3 is a different kind of thing, because what changes is
**access** — the agent now lives in your environment (a CLI, its parent
app) instead of a chat box. That shift from *request* to *access* is the
chapter break of the talk.

Two things worth noticing once you've seen all three:

- **Levels 2 and 3 reach the same outcome two different ways.** Level 2:
  you export files and hand them to a script. Level 3: an agent fetches
  the same data itself (see the WSDL bonus below) and runs the whole
  pipeline unassisted. Same destination — the human's workload is what
  collapses between them.
- **Trust escalates faster than oversight does.** You can judge the
  analysis at Level 1. You can read the code before running it at Level 2.
  By Level 3, the agent has already *acted* before you get to check. That's
  exactly why the governance flag in this repo lives at Level 3, and
  nowhere else — it's the cost of the autonomy.

## What's in each folder

- **[`level1-analyst/`](level1-analyst/)** — `candidates.xlsx` (a pipeline
  export) and `analysis.md` (the written analysis an LLM gives back).
  Nothing executes.
- **[`level2-author/`](level2-author/)** — `merge.py`: reads the shared
  `jobs.csv`, `candidates.csv`, and `enrichment.db`, joins them, and writes
  `merged.html` + `merged.xlsx`. A tool the human still has to run.
- **[`level3-agent/`](level3-agent/)** — `bonus-direct-wsdl.md`: the same
  merged outcome as Level 2, reached with the human removed from the loop
  — the agent pulls the data itself via a direct WSDL/SOAP call instead of
  waiting on an export.

## Shared data

`jobs.csv`, `candidates.csv`, and `enrichment.db` live at the repo root
and are used by every level. The two CSVs stand in for reports a
recruiting team **exports** on some cadence. `enrichment.db` stands in for
a **live system** (a generic ATS/CRM/HRIS) — something an agent could
query directly instead of waiting for the next export.

The join between `candidates.csv` and `enrichment.db` is deliberately
imperfect: a plain exact-match on name, on purpose. A few candidates and
profiles refer to the same person under slightly different names
(`Jon Smith` vs. `Jonathan Smith`), a few candidates have no profile at
all, and a couple of profiles belong to nobody in `candidates.csv`.
`level2-author/merge.py` surfaces all of that instead of hiding it — see
its printed reconciliation summary.

`generate_sample_data.py` (repo root) is the script that produced the
three shared files in the first place. You don't need to run it — it's
included only for transparency.

## How to run it

Requires Python 3, pandas, and openpyxl.

```bash
pip install pandas openpyxl
python level2-author/merge.py
```

`jobs.csv`, `candidates.csv`, and `enrichment.db` are already committed,
so this is all `merge.py` needs. Expected output: a reconciliation summary
printed to the console (19 of 25 candidates matched to a profile, 6
unmatched, 5 profiles unused), followed by the full merged table, then
`merged.html` and `merged.xlsx` written into `level2-author/` (not
committed — they're build artifacts, regenerated each run).

## The bonus: skipping the export entirely

Levels 1 and 2 both still start from an export or a directly-queryable
replica. The deeper agentic-development win is going one step further: an
agent that reads a source system's WSDL and calls its SOAP endpoint
directly, with no export step at all. See
[`level3-agent/bonus-direct-wsdl.md`](level3-agent/bonus-direct-wsdl.md) —
and the closing slide of `presentation.html` for why that's also exactly
the kind of data-movement pattern that needs a governance eye on it.

## License

MIT — see [`LICENSE`](LICENSE).
