# The prompt behind analysis.md

Level 1 in one line: **input → prompt → output.** Nothing executes in
between — the model reads a table and reasons over it, in the same chat
window you're already using.

## Input

`candidates.xlsx` — a 25-row pipeline export, attached to the chat.

## Prompt

```
I'm attaching a pipeline export: 25 candidates across 8 open
requisitions, one row per candidate, with their current stage
(Applied / Screen / Interview / Offer).

Look at this table and tell me what it says:
- How is the pipeline distributed across stages?
- Where's the bottleneck?
- Is there anything inconsistent in here I should double-check
  against the requisitions themselves?

Don't merge in any other data source - just reason over what's
in this one table.
```

## Output

`analysis.md` — a written analysis: the stage breakdown, the
front-loaded-funnel bottleneck, and a flagged inconsistency (an "On Hold"
requisition that still has active candidates moving through it) that the
model caught by cross-referencing two columns in the same table, not by
touching any other system.

That's the whole of Level 1: one table in, one paragraph-shaped answer
out. The human still has to act on it.
