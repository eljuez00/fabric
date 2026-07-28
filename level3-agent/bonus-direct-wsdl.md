# Bonus: skipping the export entirely (direct WSDL/SOAP access)

> Placeholder for an existing writeup - see the block below for where it goes.

Level 2 still starts from an export: a CSV someone pulled and handed over,
or a database you're allowed to query directly. Both are one step removed
from the system of record. The deeper Level 3 win is skipping that step
entirely: instead of waiting on a scheduled report or an admin-granted read
replica, an agent with local access reads the source system's WSDL (its
machine-readable service description), understands the SOAP operations it
exposes, and calls the endpoint directly to pull the same data live - no
export, no email, no intermediate file, and no human running a script in
the middle. This is meaningfully harder than a CSV join: the agent is
writing real integration code - request envelopes, auth, pagination -
against a contract most humans wouldn't hand-write from scratch. It is
also exactly the kind of data-movement path a governance/admin review
needs eyes on (see the closing slide of `../presentation.html`). All
endpoints and URLs below are redacted to `example.com` - swap in the real
writeup for your own environment.

Example of the shape (redacted, illustrative only):

```
WSDL:      https://api.example.com/services/CandidateService?wsdl
Operation: GetCandidateProfile
Transport: SOAP 1.1 over HTTPS
Auth:      WS-Security username token
```

<!-- PASTE EXISTING WRITEUP HERE -->
