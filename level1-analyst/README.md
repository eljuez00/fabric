# Level 1 — Analyst

The model reasons over data you bring it. Nothing executes. The whole
level is one line: **input → prompt → output.**

- **`candidates.xlsx`** — the input: a pipeline export, 25 candidates
  joined to the requisition (req) they applied to. This is what a human
  already has in hand — pulled from a system, saved locally, ready to
  hand to a model.
- **`prompt.md`** — the prompt: the plain-English ask that produced the
  analysis below, typed into the same chat window the file was attached to.
- **`analysis.md`** — the output: the kind of answer a Large Language
  Model (LLM) gives when you paste a table in and ask "what does this
  say?" Stage counts, a bottleneck, an inconsistency worth flagging. All
  reasoning, no action.

The human still did everything around the reasoning: exported the file,
opened the model, read the answer, and will have to decide what to do
about it themselves. That's the honest baseline the rest of this demo
builds away from — see the [root README](../README.md) for the full
three-level spine.

This example sticks to one table. Just as common — and explicitly *not*
recommended for anything you need to rely on — is pasting two or more
datasets into the same chat and asking the model to reconcile them itself,
in its head. It's a real pattern (a second pair of eyes, or a deeper pass
than you want to do by hand) and it's still Level 1 (nothing executes) —
it's just not repeatable, and there's no file left behind to audit. See
the closing section of [`prompt.md`](prompt.md).

(`build_pipeline_export.py` is a small utility that produced `candidates.xlsx`
from the shared `jobs.csv`/`candidates.csv` — it's not part of the Level 1
story itself, just how the example was assembled.)
