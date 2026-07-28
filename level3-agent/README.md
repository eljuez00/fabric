# Level 3 — Agent

Full agentic access to the local workspace — or, scoped further out, the
machine itself: the model writes *and runs* the code, touches the
filesystem, iterates on its own errors, and calls external services. This
is a different kind of thing from Levels 1 and 2 — not because the model
got smarter, but because what changed is **access**. It now lives in your
environment (via a Command-Line Interface, or CLI, or its parent app)
instead of a chat box.

## The workspace, not just the script

Level 2 is one script a human runs by hand. Level 3 isn't "the agent
runs `merge.py` for you" — it's the agent given a small, scoped
**workspace**: a directory it can read from and write to, containing
nothing but what this demo needs (the three shared source files, room to
write its own scripts, room to write its own output). See
[`workspace/README.md`](workspace/README.md) for what that looks like.

Inside that workspace, a Level 3 agent can rebuild what Levels 1 and 2 did
as steps in one run, not two separate hand-offs:

1. Read `jobs.csv`, `candidates.csv`, and `enrichment.db` itself.
2. Write the equivalent of `merge.py` — or reuse it — and **run it**,
   the way a human would have had to at Level 2.
3. Read its own output, catch an error, fix it, and re-run — the
   debugging loop that was the human's job in Level 2 is now the agent's.
4. Reach the same merged talent view Level 2 produces, with the human
   removed from every step in between.
5. Go one step further than Level 2 ever could: skip the export step
   entirely, by reading the source system's Web Services Description
   Language (WSDL) file and calling its Simple Object Access Protocol
   (SOAP) endpoint directly — and do the development that takes, not just
   the calling. A SOAP response comes back as XML, not a table: the agent
   has to write the client code (envelopes, auth, pagination) *and* the
   data wrangling to reshape that response into the same rows `merge.py`
   produces, before the join logic even runs. See
   [`bonus-direct-wsdl.md`](bonus-direct-wsdl.md).

That's the honest version of "a lot of the lifting from Level 2 gets
absorbed by the agent" — not a smarter merge, the same merge, minus the
human running it by hand.

## Agentic safety: what local access actually costs

Local access is the whole point of Level 3 — and the whole reason it
needs guardrails Levels 1 and 2 never did:

- **Scope the workspace.** The agent should only be able to read and
  write inside a directory built for this, not the rest of the
  filesystem. A small, disposable workspace is a control, not a
  convenience.
- **Everything it touches should be logged.** At Levels 1 and 2, a human
  read the output before anything happened. At Level 3, the agent has
  already read files, run code, and possibly called an external service
  by the time a human looks — an audit trail is the only way to
  reconstruct what happened after the fact.
- **Network access is a separate decision from filesystem access.**
  Being allowed to write a script is not the same as being allowed to
  call a live system's SOAP endpoint. Grant those separately, and review
  the second one harder than the first.

See the closing slide of [`../presentation.html`](../presentation.html)
for why this is exactly the kind of data-movement pattern an admin has to
be able to see and control — not a reason to avoid Level 3, but the cost
of the autonomy it buys you.
