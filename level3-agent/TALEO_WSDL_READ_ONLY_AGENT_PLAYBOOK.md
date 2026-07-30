# Oracle Taleo Enterprise WSDL Read-Only Extraction Playbook

## Purpose

This document is a reusable, instance-independent guide and AI-agent prompt for discovering and exporting data from Oracle Taleo Enterprise Edition through SOAP/WSDL interfaces.

It is designed for migration discovery, reconciliation, audit extracts, and data profiling. It deliberately excludes all operations that create, import, merge, update, or delete Taleo data.

The guide uses placeholders rather than organization-specific values. Every Taleo zone has its own enabled products, mapping version, custom fields, permissions, and data model. The agent must inspect the authenticated WSDL and data dictionary instead of assuming that a field or relation exists.

## Non-negotiable safety contract

The agent must obey all of the following rules:

1. Treat the Taleo account as capable of writes even when the task is read-only.
2. Never invoke an import service or an import action.
3. Never call create, merge, update, delete, import, terminate, start-process, or submit-task operations.
4. Never use `submitDocument` with an action other than the Taleo export action.
5. Do not call `submitLargeDocument` unless a separately reviewed, read-only use has been proven necessary.
6. Do not test permissions by attempting a write.
7. Start with an authenticated WSDL retrieval, followed by one exact-filter, one-field, one-row read.
8. Use the smallest necessary projection and the narrowest defensible filter.
9. Escape every user-supplied value before inserting it into XML.
10. Never print, log, save, or return passwords, authorization headers, session tokens, or raw `.env` contents.
11. Store outputs containing candidate, employee, offer, or onboarding data only in an approved restricted location.
12. Stop if the WSDL, endpoint, product path, mapping version, entity, field path, or operation cannot be verified.

### Read-only operation allowlist

The following operations are permitted when exposed by the authenticated WSDL:

- Authenticated HTTP `GET` of a WSDL.
- `FindService`:
  - `exportCSVRows`
  - `findPartialEntities`
  - `findEntities`, only when required and bounded
- `IntegrationManagementService`:
  - `submitDocument`, only with `wsa:Action` set to the Taleo export action
  - `getMessageByKey`
  - `getLargeDocumentByKey`

Everything else is denied by default.

## What the user must provide

The user should place secrets in a local secret file or secret manager. Secrets must not be pasted into an AI conversation.

Recommended `.env` format:

```dotenv
TALEO_BASE_URL=https://your-zone.taleo.net
TALEO_USERNAME=service_account_username
TALEO_PASSWORD=service_account_password

# Usually enterprise for Recruiting. Onboarding commonly uses transition.
TALEO_PRODUCT_PATH=enterprise

# Discover from the authenticated WSDL; do not assume this default is correct.
TALEO_MAPPING_VERSION=http://www.taleo.com/ws/tee800/2009/01

TALEO_OUTPUT_DIR=./outputs
```

Protect the file:

- Add `.env` to `.gitignore`.
- Restrict its filesystem permissions.
- Never copy it into the output directory.
- Never include it in an archive or migration deliverable.
- When debugging configuration, display variable names only—not values.

## Service and endpoint discovery

Do not guess an endpoint from another Taleo instance. Construct candidates from the configured base URL, then verify each with an authenticated WSDL request.

Common product paths:

| Product | Typical path |
|---|---|
| Recruiting | `enterprise` |
| Onboarding (Transitions) | `transition` |

Common service endpoints:

```text
{{TALEO_BASE_URL}}/{{TALEO_PRODUCT_PATH}}/soap?ServiceName=FindService
{{TALEO_BASE_URL}}/{{TALEO_PRODUCT_PATH}}/soap?ServiceName=IntegrationManagementService
```

The exact WSDL retrieval convention can vary by client and zone. Use an authenticated `GET` against the service URL and any WSDL form advertised by the zone. Save the credential-free WSDL locally for reproducibility.

From the WSDL, record:

- Service name and endpoint.
- SOAP version.
- Target namespaces.
- SOAP action for each permitted operation.
- Mapping/data-model version.
- Exportable entities.
- Entity fields and relations.
- Maximum/page behavior exposed by the service.
- Whether the product is Recruiting or Onboarding.

Do not construct business queries until these values are verified.

## Choosing the export pattern

### Pattern A: synchronous `FindService`

Use `FindService` for:

- Connectivity testing.
- Schema experiments.
- Exact-key lookups.
- Small, bounded result sets.
- Queries that are confidently below the service's synchronous record limit.

Oracle documents a maximum of 200 records per synchronous export call. If a query could reach the limit, partition it into non-overlapping filters or switch to the asynchronous bulk pattern.

Recommended synchronous sequence:

1. Retrieve the authenticated `FindService` WSDL.
2. Select an export operation exposed by that WSDL.
3. Query one known record with an exact filter.
4. Project only its non-sensitive business key.
5. Confirm HTTP success, no SOAP fault, one returned row, and the expected key.
6. Expand projections and scope incrementally.

### Pattern B: asynchronous Integration Toolkit export

Use `IntegrationManagementService` for:

- Bulk exports.
- Large graphs or relations.
- Large key lists.
- LOB or attachment discovery.
- Exports likely to exceed synchronous limits.

The asynchronous sequence is:

1. Submit an export document.
2. Capture the returned message key.
3. Poll message status by message key.
4. Capture the correlation key when processing completes.
5. Retrieve the resulting document by correlation key.
6. Parse the MTOM/multipart response.
7. Inspect document-level export errors before accepting records.

Oracle describes the same message-key, status, correlation-key, and result-document pattern for bulk Taleo exports.

## Selection Query Language fundamentals

Taleo uses Selection Query XML, commonly called SQ-XML.

Every query should specify:

- `projectedClass`: the base business object, such as `Candidate`, `Application`, `Requisition`, or `Offer`.
- `alias`: a short unique query name. Keep it at or below 30 characters for compatibility.
- `projections`: fields to return.
- `filterings`: conditions limiting the population.
- `sortings`: optional deterministic ordering.
- `locale`: normally `en`, unless another locale is required.
- `mode`: `CSV` or `XML`, depending on the operation and response needs.

Relation paths are comma-separated:

```xml
<q:field path="Requisition,ContestNumber"/>
<q:field path="Candidate,EmployeeNumber"/>
<q:field path="Application,Requisition,JobInformation,Title"/>
```

The path is always relative to `projectedClass`.

### Projection example

```xml
<q:projections>
  <q:projection alias="ApplicationNumber">
    <q:field path="Number"/>
  </q:projection>
  <q:projection alias="CandidateNumber">
    <q:field path="Candidate,Number"/>
  </q:projection>
  <q:projection alias="ContestNumber">
    <q:field path="Requisition,ContestNumber"/>
  </q:projection>
</q:projections>
```

### Exact filter

```xml
<q:filterings>
  <q:filtering>
    <q:equal>
      <q:field path="Number"/>
      <q:string>{{XML_ESCAPED_KEY}}</q:string>
    </q:equal>
  </q:filtering>
</q:filterings>
```

### Bounded list filter

```xml
<q:filterings>
  <q:filtering>
    <q:includedIn>
      <q:field path="Candidate,Number"/>
      <q:list>
        <q:string>{{XML_ESCAPED_KEY_1}}</q:string>
        <q:string>{{XML_ESCAPED_KEY_2}}</q:string>
      </q:list>
    </q:includedIn>
  </q:filtering>
</q:filterings>
```

Deduplicate the list locally before submission. Use configurable batches; 100–400 keys per batch is a practical starting range, not a universal Taleo limit.

### Date filters

Prefer half-open intervals:

```text
start <= value < next_period_start
```

For example, June is:

```text
2026-06-01T00:00:00 <= date < 2026-07-01T00:00:00
```

Half-open intervals prevent overlaps and omissions when monthly or daily partitions are recombined.

Use the filter operators and date serialization advertised by the zone's WSDL/SQ-XML schema. Do not invent an operator from SQL syntax.

## Synchronous `FindService` request template

This is a structural template. The SOAP version, namespaces, action, mapping version, operation element, and response packaging must be taken from the authenticated WSDL.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
  <s:Body>
    <exportCSVRowsRequest xmlns="{{FIND_NAMESPACE}}">
      <mappingVersion>{{MAPPING_VERSION}}</mappingVersion>
      <query>
        <q:query
          xmlns:q="http://itk.taleo.com/ws/query"
          alias="ReadOnlyKeyTest"
          projectedClass="{{ENTITY}}"
          locale="en"
          mode="CSV"
          csvheader="true"
          preventDuplicates="true">
          <q:projections>
            <q:projection alias="BusinessKey">
              <q:field path="{{KEY_FIELD_PATH}}"/>
            </q:projection>
          </q:projections>
          <q:filterings>
            <q:filtering>
              <q:equal>
                <q:field path="{{KEY_FIELD_PATH}}"/>
                <q:string>{{XML_ESCAPED_KEY}}</q:string>
              </q:equal>
            </q:filtering>
          </q:filterings>
        </q:query>
      </query>
      <attributes/>
    </exportCSVRowsRequest>
  </s:Body>
</s:Envelope>
```

Typical content type for SOAP 1.2:

```text
application/soap+xml; charset=UTF-8; action="{{WSDL_SOAP_ACTION}}"
```

Never copy the SOAP action from another zone without verifying it in the WSDL.

## Asynchronous bulk-export templates

### Namespaces and export action

Common Integration Toolkit values are:

```text
Management namespace:
http://www.taleo.com/ws/integration/toolkit/2011/05/management

Toolkit namespace:
http://www.taleo.com/ws/integration/toolkit/2011/05

WS-Addressing namespace:
http://www.w3.org/2005/03/addressing

Export action:
http://www.taleo.com/ws/integration/toolkit/2005/07/action/export

Queue address:
http://www.taleo.com/ws/integration/toolkit/2005/07/addressing/queue
```

Verify these against the zone WSDL before use.

### Submit an export document

```xml
<soapenv:Envelope
  xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:man="{{MANAGEMENT_NAMESPACE}}"
  xmlns:itk="{{TOOLKIT_NAMESPACE}}"
  xmlns:wsa="{{WS_ADDRESSING_NAMESPACE}}">
  <soapenv:Header>
    <wsa:MessageID>{{UNIQUE_READ_ONLY_MESSAGE_ID}}</wsa:MessageID>
    <wsa:ReplyTo>
      <wsa:Address>{{QUEUE_ADDRESS}}</wsa:Address>
    </wsa:ReplyTo>
    <wsa:Action>{{EXPORT_ACTION}}</wsa:Action>
  </soapenv:Header>
  <soapenv:Body>
    <man:submitDocument>
      <itk:Document>
        <itk:Attributes>
          <itk:Attribute name="mode">XML</itk:Attribute>
          <itk:Attribute name="version">{{MAPPING_VERSION}}</itk:Attribute>
        </itk:Attributes>
        <itk:Content>
          <ExportQuery xmlns="http://www.taleo.com/ws/integration/toolkit/2005/07/action/export">
            <q:query
              xmlns:q="http://itk.taleo.com/ws/query"
              alias="ReadOnlyBulkExport"
              projectedClass="{{ENTITY}}"
              locale="en"
              mode="XML"
              largegraph="false"
              preventDuplicates="false">
              <q:projections>
                {{PROJECTIONS}}
              </q:projections>
              <q:filterings>
                <q:filtering>
                  {{BOUNDED_FILTER}}
                </q:filtering>
              </q:filterings>
            </q:query>
          </ExportQuery>
        </itk:Content>
      </itk:Document>
    </man:submitDocument>
  </soapenv:Body>
</soapenv:Envelope>
```

The response should contain an `IntegrationMessage/MessageKey`.

### Poll by message key

```xml
<soapenv:Envelope
  xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:man="{{MANAGEMENT_NAMESPACE}}">
  <soapenv:Header/>
  <soapenv:Body>
    <man:getMessageByKey>
      <man:messageKey>{{MESSAGE_KEY}}</man:messageKey>
    </man:getMessageByKey>
  </soapenv:Body>
</soapenv:Envelope>
```

Poll with bounded retries and a delay. A 2–15 second interval is a reasonable starting range. Do not poll continuously.

Do not assume state meanings without verifying the WSDL/documentation and observed response. In commonly deployed Integration Toolkit versions, a completed export returns a correlation key with the completed state; failure states must stop processing and preserve sanitized diagnostics.

### Retrieve results by correlation key

```xml
<soapenv:Envelope
  xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:man="{{MANAGEMENT_NAMESPACE}}">
  <soapenv:Header/>
  <soapenv:Body>
    <man:getLargeDocumentByKey>
      <man:messageKey>{{CORRELATION_KEY}}</man:messageKey>
    </man:getLargeDocumentByKey>
  </soapenv:Body>
</soapenv:Envelope>
```

The result is commonly MTOM/multipart. It may not be a plain XML response body.

## MTOM and multipart response handling

The response parser must:

1. Read the `Content-Type` header.
2. Detect `multipart/related`.
3. Extract the MIME boundary parameter.
4. Split the response into MIME parts without treating arbitrary binary data as text when avoidable.
5. Identify the SOAP/XOP part, commonly `application/xop+xml`.
6. Identify the attached export document by `Content-ID` and content type.
7. Parse the export document.
8. Check for `Error` elements before accepting records.
9. Preserve the original bytes when the payload is binary.

For synchronous CSV responses, Taleo may return:

- CSV in an MTOM text attachment.
- Base64 content inside a `CSVContent` element.

Support both forms.

## Business-object starting points

These are conceptual starting points. Field paths must be validated against the zone's data dictionary.

| Business concept | Common entity | Useful keys/relations |
|---|---|---|
| Requisition/job | `Requisition` | `Number`, `ContestNumber`, `JobInformation`, `Department` |
| Submission/application | `Application` | `Number`, `Candidate`, `Requisition`, status/workflow fields |
| Candidate profile | `Candidate` | `Number`, `EmployeeNumber`, `EmailAddress` |
| Offer | `Offer` | `Number`, `Sequence`, `Application`, status and date fields |
| Onboarding | Zone-specific Transition entities | Candidate, process, task, document relations |

Important distinctions:

- Candidate number is not application number.
- Requisition internal number is not always the same as the displayed Contest Number.
- One application can have several offer versions.
- `Application.CurrentOffer.Number` can identify the current offer.
- An offer does not exist for every application.
- Onboarding commonly uses the `transition` product path, not `transitions`.

## Custom fields and UDFs

Never assume that an Analytics reporting label such as `UDF3` is the WSDL field name.

Custom fields may have encoded integration names such as:

```text
OrganizationPrefix_5fBusinessField
```

Required workflow:

1. Synchronize or inspect the Taleo Connect data dictionary.
2. Locate the entity that owns the field.
3. Record the integration/WSDL name, display label, type, and relation path.
4. Test the field on one known record.
5. Confirm the returned value against the Taleo UI or an approved report.
6. Only then use the field for bulk filtering or reconciliation.

If a projection fails with `ExportUnknownModelElementName`, remove only the failing field, verify its path in the dictionary, and rerun the bounded test. Do not change the entity or expand the query blindly.

## LOBs, attachments, and documents

Binary and LOB retrieval requires additional safeguards:

1. Retrieve metadata before content.
2. Filter to a known business record.
3. Project one attachment/document at a time during discovery.
4. Decode base64 locally.
5. Determine type from:
   - Declared MIME type.
   - Declared filename/extension.
   - File signature or magic bytes.
6. Do not assume every offer letter is PDF. A signed-offer LOB may decode to HTML.
7. Do not assume a named onboarding document is the individualized signed offer.
8. Preserve the original decoded bytes.
9. If local conversion is required, save both the source and converted artifact.
10. Calculate SHA-256 hashes and create a manifest.
11. Never execute an extracted file.
12. Do not retrieve attachments when the task asks only for metadata.

## Batching and large-extract strategy

The agent must avoid unbounded queries.

Preferred order:

1. Exact business key.
2. Small `includedIn` list.
3. Non-overlapping date partitions.
4. Asynchronous bulk export.

For every partition or batch:

- Save its filter definition.
- Record row count.
- Record first and last business/date key when applicable.
- Record a SHA-256 hash of the saved output.
- Deduplicate by the entity's stable business key.
- Reconcile combined row counts against partition totals.
- Confirm no overlapping date boundary.

If a synchronous result returns exactly 200 rows, treat the extract as possibly truncated until proven otherwise.

## Validation checklist

Before calling an extraction complete, validate:

- HTTP status is successful.
- No SOAP fault is present.
- No document-level Taleo `Error` is present.
- Entity count and row count are plausible.
- The result does not equal a known service limit without investigation.
- Required business keys are populated.
- Business keys are unique when uniqueness is expected.
- Child rows refer to an exported parent key.
- Partitions have no overlap or gap.
- Recombined totals equal the sum of partition totals after documented deduplication.
- Date/time zone assumptions are documented.
- Custom-field values are verified on a known record.
- Binary files match their declared or detected format.
- Outputs contain no credentials or authorization headers.
- The audit log lists only read-only operations.

## Audit log

Maintain a `journal.md` or machine-readable run manifest containing:

- UTC timestamp.
- Environment label supplied by the user.
- Hostname without credentials.
- Product path.
- Service and operation.
- Entity.
- Filter summary with sensitive values masked when necessary.
- Projection aliases and paths.
- Batch or partition number.
- Returned rows.
- Output filename.
- SHA-256 hash.
- WSDL/mapping version.
- Validation results.
- Exceptions and unresolved assumptions.
- Explicit statement that no import/write operation was invoked.

Never store:

- Passwords.
- Authorization headers.
- Raw `.env` contents.
- Session cookies.
- Unnecessary PII in console logs.

## Error-handling guide

| Symptom | Likely cause | Safe response |
|---|---|---|
| HTTP 401/403 | Wrong credentials, endpoint, or permission | Stop; verify configuration without printing secrets |
| SOAP fault before query execution | Namespace, action, body, or service mismatch | Compare request with authenticated WSDL |
| `ExportUnknownModelElementName` | Invalid entity relation or field path | Verify the data dictionary; test one field |
| `ExportBadSelectionQueryFormat` | Invalid SQ-XML or alias | Validate XML; keep alias short; reduce to one projection/filter |
| Exactly 200 synchronous rows | Possible synchronous limit | Partition or switch to bulk export |
| No message key | Wrong management operation/action | Stop; inspect sanitized SOAP response and WSDL |
| Poll never completes | Large job, throttling, or failed state handling | Use bounded retries; stop with saved message key |
| Correlation key absent | Job incomplete or failed | Do not call result retrieval; preserve status metadata |
| MTOM boundary missing | Unexpected response format or error | Inspect content type and SOAP fault safely |
| Empty result | Valid zero rows, masked field, wrong key, or security restriction | Validate with one known record and an alternate verified key |
| Duplicate records | One-to-many relation expansion or overlapping partitions | Dedupe by stable key and document the cause |

## Copy/paste master prompt for an AI agent

Copy the following prompt into an AI coding agent that has access to the working directory and network. Replace only the bracketed task inputs. Do not paste credentials into the prompt.

```text
You are performing a read-only Oracle Taleo Enterprise Edition data extraction.

OBJECTIVE
Create and run a safe, auditable WSDL/SOAP extraction for:

- Business question: [DESCRIBE THE DATA NEEDED]
- Product: [RECRUITING OR ONBOARDING/TRANSITIONS]
- Business object/entity if known: [ENTITY OR "DISCOVER"]
- Required output columns: [FIELDS OR BUSINESS DEFINITIONS]
- Filter/population: [EXACT KEYS, DATE RANGE, OR OTHER BOUNDED CRITERIA]
- Expected grain: [ONE ROW PER WHAT]
- Output format: [CSV, JSON, XML, BINARY ARTIFACTS]
- Output directory: [LOCAL OUTPUT DIRECTORY]

CONFIGURATION
Read the following values from a local secret file or secret manager:

- TALEO_BASE_URL
- TALEO_USERNAME
- TALEO_PASSWORD
- TALEO_PRODUCT_PATH
- Optional TALEO_MAPPING_VERSION

Never display, log, return, or save secret values. If configuration is incomplete, report only the missing variable names.

SAFETY CONTRACT
This task is strictly read-only even if the account has system-administrator privileges.

Allowed:
- Authenticated WSDL retrieval.
- FindService exportCSVRows, findPartialEntities, or a bounded findEntities call when exposed by the WSDL.
- IntegrationManagementService submitDocument only when WS-Addressing Action is exactly the Taleo export action.
- getMessageByKey.
- getLargeDocumentByKey.
- Local parsing, validation, hashing, conversion, and report creation.

Forbidden:
- Any import action.
- Any create, merge, update, delete, terminate, start-process, submit-task, or other mutation operation.
- Testing write permissions.
- submitLargeDocument unless I explicitly approve a separately reviewed read-only need.
- Unbounded queries.
- Attachment or LOB retrieval unless the objective explicitly asks for it.

If a requested step requires a forbidden operation, stop and explain the limitation.

REQUIRED WORKFLOW
1. Inspect the working directory for existing WSDLs, Taleo Connect configurations, data dictionaries, scripts, and prior journals.
2. Retrieve the current authenticated WSDL for the configured product and service. Do not guess the endpoint, namespaces, SOAP version, mapping version, entity, field path, or SOAP action.
3. Save a credential-free local copy of the WSDL.
4. Produce a discovery summary listing only:
   - Host and product path.
   - Service.
   - Permitted operations.
   - SOAP version and namespaces.
   - Mapping version.
   - Candidate entities/fields for the business question.
5. Before the requested extraction, run a one-row connectivity test:
   - Use one exact known business key supplied by the user or found in an approved local source.
   - Project only one non-sensitive key field.
   - Require HTTP success, no SOAP fault, and exactly the expected row.
   - Do not print the key if it is sensitive.
6. Choose FindService for a result confidently below 200 rows. Treat exactly 200 rows as possibly truncated.
7. Use IntegrationManagementService for bulk data:
   - submitDocument with the export action.
   - Capture MessageKey.
   - Poll getMessageByKey with bounded retries and a reasonable delay.
   - Capture CorrelationKey only after successful completion.
   - Retrieve results using getLargeDocumentByKey.
   - Parse MTOM/multipart safely.
8. Build SQ-XML with:
   - A verified projectedClass.
   - An alias no longer than 30 characters.
   - Minimal projections.
   - A bounded filter.
   - XML-escaped values.
   - Verified comma-separated relation paths.
9. For lists, deduplicate locally and submit configurable batches, initially 100–400 keys.
10. For dates, use non-overlapping half-open intervals and document the timezone.
11. For UDFs, find the integration/WSDL field name in the synchronized data dictionary. Do not substitute an Analytics reporting ID such as UDF3 for the WSDL name.
12. If binary content is requested:
   - Retrieve metadata first.
   - Decode locally.
   - Detect actual file type.
   - Preserve original bytes.
   - Hash every artifact.
   - Never execute extracted content.
13. Validate:
   - Row counts and possible service limits.
   - Required keys.
   - Duplicate business keys.
   - Referential integrity.
   - Partition completeness.
   - Expected grain.
   - Custom-field values against one known record.
14. Save:
   - Source code.
   - Credential-free request templates.
   - Output data.
   - Validation summary.
   - Run manifest with SHA-256 hashes.
   - journal.md.
15. In the final response, report:
   - What was extracted.
   - Exact row count and grain.
   - Filters and timezone.
   - Read-only services/operations used.
   - Validation results.
   - Output paths.
   - Any unresolved schema, masking, permissions, truncation, or data-quality issues.
   - An explicit statement that no Taleo write operation was performed.

IMPLEMENTATION REQUIREMENTS
- Prefer a maintainable PowerShell, Python, or another language already supported in the workspace.
- Keep endpoint, credentials, entity, fields, filters, batch size, poll interval, timeout, and output directory configurable.
- Separate request construction, SOAP invocation, MTOM parsing, polling, record parsing, validation, and output writing into testable functions.
- Fail closed: if the service, action, field, response state, or content type is unexpected, stop instead of broadening the request.
- Sanitize errors so credentials and sensitive filter values are not exposed.
- Do not ask me to paste a password into the conversation.

Start by stating the exact read-only test you intend to perform. Then proceed unless a required endpoint, credential variable, or business-key choice is missing.
```

## Short prompt for experienced teams

```text
Build a strictly read-only, instance-independent Oracle Taleo Enterprise WSDL extractor for [BUSINESS OBJECT AND POPULATION].

Discover the authenticated WSDL and mapping version. Do not guess field paths or UDF names. Begin with an exact-filter, one-key, one-field connectivity test.

Allowed operations are FindService exports and IntegrationManagementService submitDocument with the export action, getMessageByKey, and getLargeDocumentByKey. No import, merge, update, create, delete, process, task, or permission-testing operations are allowed.

Use bounded SQ-XML, XML escaping, <=30-character aliases, configurable batches, half-open date partitions, bounded polling, MTOM parsing, row-limit detection, deduplication, referential-integrity checks, hashes, a run manifest, and journal.md.

Read secrets from local variables TALEO_BASE_URL, TALEO_USERNAME, TALEO_PASSWORD, and TALEO_PRODUCT_PATH; never print them. Save credential-free templates and outputs to [OUTPUT DIRECTORY]. Report exact grain, filters, counts, validation, limitations, and explicitly confirm that no Taleo writes occurred.
```

## Official Oracle references

- Taleo Web Services — Standard Type Basics and the distinction between the export `FindService` and product-specific import services:  
  https://docs.oracle.com/en/cloud/saas/taleo-enterprise/25a/otwsu/c-standardtypebasics.html
- Taleo Web Services — Selection Query Language:  
  https://docs.oracle.com/en/cloud/saas/taleo-enterprise/22d/otwsu/c-selectionquerylanguagel.html
- Taleo Web Services — synchronous export limit guidance:  
  https://docs.oracle.com/en/cloud/saas/talent-acquisition/17.8/otwsu/getting-started.html
- Oracle Integration — asynchronous Taleo export pattern using message key, status, correlation key, and result document:  
  https://docs.oracle.com/en/cloud/paas/application-integration/talent-acquisition-cloud-adapter-user/export-candidate-data-from-oracle-talent-acquisition-cloud-taleo-ee.html
- Taleo Connect Client — product integration-pack dictionary and custom-field synchronization:  
  https://docs.oracle.com/en/cloud/saas/taleo-enterprise/21a/otccu/description.html
- Taleo Connect Client — request/response formats and UTF-8 requirement:  
  https://docs.oracle.com/en/cloud/saas/taleo-enterprise/otccu/c-confgentab.html
- Taleo Connect Server overview:  
  https://docs.oracle.com/en/cloud/saas/taleo-enterprise/otccu/c-tcs.html

## Final reminder

WSDL access is not proof that every entity or field is readable by the account, and a system-administrator account is not a reason to broaden the extraction. Discover narrowly, test one row, expand deliberately, validate every batch, and keep the operation allowlist read-only.
