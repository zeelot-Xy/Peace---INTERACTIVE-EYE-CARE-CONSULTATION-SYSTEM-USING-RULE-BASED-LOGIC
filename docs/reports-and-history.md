# Reports and Patient History

## Purpose and boundary

Phase 9 turns a completed consultation into a printable PDF artifact without rerunning the
inference engine. The report remains educational, non-diagnostic, and tied to the exact
consultation result and knowledge fingerprint that produced it.

## Immutable report lifecycle

`POST /api/v1/consultations/{consultation_id}/report` creates the report for the authenticated
owner. The consultation must be completed and have a stored inference result. The service
captures:

- patient name, email, optional phone, and optional date of birth at generation time;
- consultation and completion dates;
- displayed questions and recorded answers from the frozen knowledge package;
- possible indications, risk, red flags, recommendations, sources, explanation, and disclaimer;
- knowledge package ID, content version, and SHA-256 fingerprint; and
- generation time, PDF filename, MIME type, and PDF SHA-256 checksum.

The JSON composition snapshot and exact PDF bytes are stored in SQLite. The one-report-per-
consultation constraint makes creation idempotent: a repeat request returns the existing report
and never silently recomposes it from a changed profile or knowledge version.

## Resources

All responses except the file download use `{data, errors, correlation_id}`.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/consultations/{id}/report` | Create or retrieve the owned immutable report |
| `GET` | `/api/v1/reports` | List owned reports; administrators may list all reports |
| `GET` | `/api/v1/reports/{id}` | Read secure report metadata |
| `GET` | `/api/v1/reports/{id}/download` | Download the retained PDF bytes |

Patient access is ownership-scoped. Unknown and non-owned report IDs both return 404 to avoid
disclosing that another patient's record exists. Administrators may review report metadata and
download reports for governed support and audit work. Creation and download actions are
audited without recording consultation answers in the audit log.

Downloads use `application/pdf`, attachment disposition, `nosniff`, and private no-store cache
controls. Cookie authentication is required. Report identifiers are UUIDs, not access tokens.

## PDF composition

The PDF uses an embedded Unicode-capable font and paginated A4 layout. It contains a prominent
limitation, patient and consultation details, action level, red flags, next steps, possible
indications, responses, matched-rule explanation, sources, knowledge fingerprint, and page
numbers. Long tables repeat their headings across pages.

The PDF deliberately says "possible indications" rather than diagnoses, describes match scores
as authored-criteria matches rather than probabilities, and preserves the mandatory disclaimer.
It does not prescribe medication or replace urgent professional care.

## History filtering

`GET /api/v1/consultations` accepts:

- `status`: `in_progress`, `completed`, or `cancelled`;
- `risk`: one authored risk-level ID;
- `date_from` and `date_to`: inclusive `YYYY-MM-DD` dates; and
- bounded `page` and `per_page` values.

Returned items include `report_id` when a PDF already exists. Filters are applied by the server
inside the authenticated ownership boundary. Invalid dates, statuses, or risk IDs return 422.

## Privacy, retention, and limitations

Reports contain sensitive user-provided information and must not be copied into Slack, public
issues, screenshots, or test fixtures using real identities. A profile edit after generation
does not rewrite an existing report. Formal deletion and configurable retention behavior remain
Governed retention, deletion, backup, and restore operations keep the database and its report
blobs together.

The report is reproducible evidence of software behavior, not evidence of clinical validity.
The knowledge base has not received expert clinical validation.
