# Pipeline analysis — candidates.xlsx

*This is the kind of response an LLM gives when you paste in a table and
ask "what does this say?" Nothing ran. Nobody's filesystem was touched.
The model reasoned over 25 rows of data and handed back an answer — the
human still had to export the file, open it, read this, and decide what
to do about it.*

## Overview

25 candidates across 8 open requisitions.

| Stage | Count | Share |
|---|---|---|
| Applied | 11 | 44% |
| Screen | 8 | 32% |
| Interview | 4 | 16% |
| Offer | 2 | 8% |

## Observations

- **The funnel is front-loaded.** Almost half of all candidates (11 of 25)
  are still sitting in Applied. Only 2 have reached Offer. If nothing else
  changes, that's the bottleneck worth a recruiter's attention first.

- **No engineering offers yet.** Both current offers (Product Manager,
  UX Designer) are outside Engineering, even though two Engineering reqs
  (Software Engineer, DevOps Engineer) have candidates as far along as
  Interview. Worth asking whether that's a hiring-manager bandwidth issue
  or a genuinely weaker slate.

- **A req marked "On Hold" still has active candidates.** DevOps Engineer
  (J007) shows `status = On Hold` in jobs.csv, but has 2 candidates already
  past Applied — one in Screen, one in Interview. Someone is still moving
  this pipeline forward even though the req itself isn't open. That's the
  kind of inconsistency worth flagging back to a human, not silently
  resolving one way or the other.

- **Most even distribution:** Data Analyst (J003) and Product Manager
  (J002) each have candidates spread across three different stages —
  the healthiest-looking pipelines in the set.

- **Thinnest pipeline:** DevOps Engineer (J007) has only 2 candidates
  total, the fewest of any req — consistent with it being on hold.

## What this level does and doesn't do

This is analysis only. It doesn't touch a database, it doesn't merge in
the profile data from `enrichment.db`, and it doesn't write any file back
out. Everything here came from reasoning over the one table it was given.
That combination — and completeness — of automation is what changes at
the next level.
