# Level 3 — Agent

The model has **local access**: it writes *and runs* the code, touches
the filesystem, iterates on its own errors, and calls external services.
This is a different kind of thing from Levels 1 and 2 — not because the
model got smarter, but because what changed is **access**. It now lives
in your environment (via a CLI or its parent app) instead of a chat box.

Concretely, for this dataset, a Level 3 agent would:

1. Read the same three sources Level 2 reads by hand-run script.
2. Reach the **same merged outcome** as `../level2-author/merge.py` — but
   instead of a human exporting files and running the script, the agent
   fetches what it needs and runs the whole pipeline itself.
3. Go one step further than Level 2 can: skip the export step entirely by
   calling the source system directly. See **[`bonus-direct-wsdl.md`](bonus-direct-wsdl.md)**
   — an agent that reads a system's WSDL and calls its SOAP endpoint
   directly, with no export, no email, no intermediate file.

That collapses the human's job down to two things: **describe intent**,
**verify output**. Everything in between — writing the code, running it,
fixing what breaks, fetching the data — is no longer on the human.

## Why the governance flag lives here, and nowhere else

At Level 1 you can judge the analysis before acting on it. At Level 2 you
can read the code before you run it. At Level 3, by the time you're
looking at anything, the agent has **already acted** — it already reached
into a system and moved data. That's not a reason to avoid Level 3. It's
the reason it needs a governance eye that Levels 1 and 2 don't: scoped
access, an audit trail, and a human sign-off on what's allowed to move
where. See the closing slide of [`../presentation.html`](../presentation.html).
