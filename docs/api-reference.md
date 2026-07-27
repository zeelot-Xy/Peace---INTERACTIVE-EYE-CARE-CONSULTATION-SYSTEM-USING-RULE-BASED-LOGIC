# REST API Reference

## Contract

All resources are versioned under `/api/v1`. JSON responses use:

```json
{
  "data": {},
  "errors": [],
  "correlation_id": "uuid"
}
```

Validation errors contain stable `code`, `message`, and, where applicable, `field` values.
List resources may include pagination metadata in `data`. Unexpected errors return a safe
message and correlation ID; secrets and stack traces are not returned.

Authentication uses short-lived access and rotated refresh JWTs in HttpOnly cookies. Clients
must send credentials. State-changing requests also send the readable CSRF cookie value in the
`X-CSRF-TOKEN` header. Token material is never returned in JSON. Cookies are `Secure` in
production and hosted deployments must use HTTPS.

## Public and authentication resources

| Method | Resource | Purpose |
|---|---|---|
| `GET` | `/health` | Service and active-knowledge health |
| `POST` | `/auth/register` | Create and sign in a patient |
| `POST` | `/auth/login` | Establish an authenticated session |
| `POST` | `/auth/refresh` | Rotate refresh state and replace the access cookie |
| `POST` | `/auth/logout` | Revoke the current family and clear cookies |
| `POST` | `/auth/logout-all` | Revoke all sessions for the authenticated user |
| `GET` | `/users/me` | Read the safe current-user profile |
| `PATCH` | `/users/me` | Update name, phone, or date of birth |
| `POST` | `/users/me/password` | Change password and revoke other sessions |

Registration accepts `full_name`, `email`, and `password`. Login accepts `email` and
`password`. Profile and user responses never expose password hashes, token identifiers, or
security-event internals.

## Consultation resources

| Method | Resource | Purpose |
|---|---|---|
| `POST` | `/consultations` | Start a version-frozen consultation |
| `GET` | `/consultations` | List owned consultations with supported filters |
| `GET` | `/consultations/{id}` | Read current state and next applicable question |
| `PUT` | `/consultations/{id}/responses/{question_id}` | Save or revise one answer |
| `DELETE` | `/consultations/{id}/responses/{question_id}` | Remove a revisable answer |
| `POST` | `/consultations/{id}/complete` | Validate and complete the consultation |
| `POST` | `/consultations/{id}/cancel` | Cancel an active consultation |
| `GET` | `/consultations/{id}/result` | Read the immutable result snapshot |
| `POST` | `/consultations/{id}/report` | Generate or return the immutable report |

Answer writes include the consultation `revision`. A stale revision returns a conflict rather
than overwriting a newer answer. Question IDs and values are validated against the consultation's
frozen knowledge package. Completion fails while an applicable required or safety question is
unanswered.

Example answer request:

```json
{
  "value": true,
  "revision": 3
}
```

The result includes the risk level, possible indications, recommendations, red flags, evidence,
matched rules, inference trace, rule-match score, knowledge version, and mandatory disclaimer.

## Report resources

| Method | Resource | Purpose |
|---|---|---|
| `GET` | `/reports` | List the patient's owned reports |
| `GET` | `/reports/{id}` | Read report metadata |
| `GET` | `/reports/{id}/download` | Download the stored PDF bytes |

Report ownership is enforced at the database query boundary. Report snapshots are immutable and
retain a checksum, patient, consultation, inference explanation, and knowledge version.

## Administrator resources

Every resource below requires the persisted `administrator` role, not only a role copied into an
older token.

| Method | Resource | Purpose |
|---|---|---|
| `GET` | `/admin/summary` | Operational counts |
| `GET` | `/admin/users` | Paginated user listing |
| `GET` | `/admin/consultations` | Governed consultation listing |
| `GET` | `/admin/consultations/{id}/report` | Review a completed result/report |
| `GET` | `/admin/audit-logs` | Read redacted security and governance events |
| `GET` | `/admin/knowledge` | Read active and retained knowledge state |
| `GET` | `/admin/knowledge/versions/{version}` | Inspect a retained version |
| `POST` | `/admin/knowledge/validate` | Validate and preview a complete ZIP package |
| `POST` | `/admin/knowledge/publish` | Publish a previously valid candidate |
| `POST` | `/admin/knowledge/rollback` | Reactivate a retained valid version |

Knowledge uploads use the documented archive limits and exact package inventory. Invalid,
encrypted, linked, traversing, oversized, or identity-mismatched archives are rejected before
publication.

## Status and error behavior

Successful creation normally returns `201`; successful reads and updates return `200`; empty
successful operations may return `204`. Common failures are:

| Status | Meaning |
|---:|---|
| `400` | Invalid JSON, request, or state transition |
| `401` | Missing, invalid, expired, or revoked authentication |
| `403` | Valid identity without permission, or invalid CSRF |
| `404` | Resource absent or not visible to the caller |
| `409` | Duplicate identity, stale revision, or conflicting operation |
| `413` | Request or archive exceeds the configured limit |
| `415` | Unsupported media type |
| `422` | Field or knowledge validation failed |
| `429` | Rate limit exceeded |

For detailed consultation shapes see [Consultation API](consultation-api.md); for authentication
flows see [Authentication](authentication.md).

