# The agent's workspace

Not a build artifact — this folder exists to show the *shape* of what a
Level 3 agent is actually given, versus what it's shown here.

```
workspace/
├── inputs/          <- read-only: jobs.csv, candidates.csv, enrichment.db
│                        (copies, not the repo's originals)
├── scratch/          <- read-write: wherever the agent writes the scripts
│                        it authors and re-runs while iterating
└── output/           <- read-write: the merged view it produces -
                         the same merged.html / merged.xlsx shape as Level 2
```

A few things worth noticing about this shape, not just its contents:

- **It's scoped, not open.** The agent can't wander the rest of the
  filesystem looking for "the candidate data" — it's handed exactly the
  three files it needs, and nowhere else to look.
- **It's disposable.** Nothing in here is precious. If the agent's first
  attempt at the merge is wrong, the fix is to inspect `scratch/`, correct
  it, and re-run — not to worry about what else might have been touched.
- **Read and write are separated on purpose.** `inputs/` never gets
  written to. Whatever the agent builds lives in `scratch/` and `output/`
  instead, so a bad run can't corrupt the source data it started from.

This is deliberately not populated with fabricated agent-run output - see
the root README: nothing in this repo runs live, and pretending an agent
produced files here would misrepresent that. The shape above is the
point; `../README.md` and `../bonus-direct-wsdl.md` cover what such an
agent would actually do inside it.
