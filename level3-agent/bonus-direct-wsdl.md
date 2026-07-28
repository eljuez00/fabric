# Bonus: skipping the export entirely (direct WSDL/SOAP access)

> Placeholder for an existing writeup - see the block below for where it goes.

Level 2 still starts from an export: a CSV someone pulled and handed over,
or a database you're allowed to query directly. Both are one step removed
from the system of record. The deeper Level 3 win is skipping that step
entirely: instead of waiting on a scheduled report or an admin-granted read
replica, an agent with local access reads the source system's Web Services
Description Language (WSDL) file - its machine-readable service
description - understands the Simple Object Access Protocol (SOAP)
operations it exposes, and calls the endpoint directly to pull the same
data live - no export, no email, no intermediate file, and no human
running a script in the middle. This is meaningfully harder than a CSV
join: the agent is writing real integration code - request envelopes,
authentication, pagination - against a contract most humans wouldn't
hand-write from scratch. It is also exactly the kind of data-movement path
a governance/admin review needs eyes on (see the closing slide of
`../presentation.html`). All endpoints and URLs below are redacted to
`example.com` - swap in the real writeup for your own environment.

Example of the shape (redacted, illustrative only):

```
WSDL:      https://api.example.com/services/CandidateService?wsdl
Operation: GetCandidateProfile
Transport: SOAP 1.1 over HTTPS
Auth:      WS-Security username token
```

## Small bonus: WSDL instead of building a custom report

Applicant Tracking Systems (ATS) typically ship an admin console where
someone can build a custom analytics or reporting extract by hand -
picking fields, saving a report definition, scheduling it, downloading the
result. That's still a human-maintained export, just one built inside the
vendor's UI instead of outside it. An agent that can read the same
system's WSDL doesn't need that report to exist at all - it calls the
SOAP endpoint for the fields it needs directly, which means no report
definition to build, maintain, or re-run when a field changes upstream.

<!-- PASTE EXISTING WRITEUP HERE -->
