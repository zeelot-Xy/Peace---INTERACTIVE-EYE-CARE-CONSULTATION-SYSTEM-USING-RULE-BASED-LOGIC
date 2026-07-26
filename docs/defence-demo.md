# Defence Demonstration Guide

This guide provides a repeatable, non-sensitive demonstration of the implemented system. Use
fictional identities only. The demonstration does not establish clinical validity.

## Preparation

1. Start the backend and frontend using the documented development commands.
2. Confirm `GET /api/v1/health` returns HTTP 200.
3. Prepare one patient account and one administrator account through the secure bootstrap
   procedure. Never place credentials in screenshots, source files, Slack, or Drive.
4. Keep the knowledge source register and requirements-to-test report available for questions.

## Patient safety-path demonstration

1. Register a fictional patient and show that the browser stores no JWT in local storage.
2. Start a consultation and explain the frozen package identity and progress indicator.
3. Answer the chemical-exposure question **Yes**. Point out that emergency advice appears
   immediately, before consultation completion.
4. Complete the remaining questions with the prepared fictional scenario.
5. Show the emergency action level, red flags, possible indications, authored rule explanation,
   source links, rule-match wording, and non-diagnostic disclaimer.
6. Generate and download the PDF. Show the patient identity, responses, action level, sources,
   knowledge fingerprint, explanation, and disclaimer.
7. Generate the report again and explain that the same immutable stored report is returned.
8. Filter history to completed emergency consultations and reopen the result.

Expected evidence: safety escalation cannot be hidden by branching, the result is explainable,
the report is reproducible, and another patient cannot retrieve it.

## Administrator governance demonstration

1. Sign in as a patient and show that `/admin` redirects away and the admin API returns 403.
2. Sign in through the bootstrapped administrator account.
3. Show operational summaries, user roles, consultation summaries, report review, and audit
   events without exposing passwords or tokens.
4. Upload a prepared complete knowledge ZIP and select validation only.
5. Explain validation issues or the collection diff and affected-rule preview.
6. Publish only a valid candidate, then show the prior version remains retained.
7. Roll back to the prior version and show the audited action.
8. Reopen a historical consultation and explain why its frozen knowledge fingerprint is
   unchanged.

Expected evidence: role boundaries, validation-before-publication, retained versions, rollback,
auditability, and historical reproducibility.

## Automated rehearsal

From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-phase10.ps1
```

The cross-layer patient and role-boundary rehearsals live in
`backend/tests/test_defence_demo.py`. The React journey, accessibility, and recovery checks live
in `frontend/src/App.test.tsx`. Detailed requirement mappings are in
`docs/requirements-to-test-report.md`.

## Suggested defence narrative

Describe the system as an educational rule-based consultation aid. Explain that JSON knowledge
is validated and versioned, forward chaining is deterministic, the highest safety risk wins,
results retain an inference trace, and reports preserve the frozen knowledge version. State
clearly that published sources improve traceability but do not replace expert clinical
validation.
