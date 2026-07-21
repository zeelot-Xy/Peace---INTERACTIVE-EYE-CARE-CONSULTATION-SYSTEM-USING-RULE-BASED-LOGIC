# Authentication and API Contract

## Security model

- Passwords use Werkzeug scrypt hashes and are never logged or serialized.
- Passwords must contain 12–128 characters; arbitrary composition rules are intentionally avoided.
- Access JWTs expire after 15 minutes and refresh JWTs after seven days.
- Both tokens use HttpOnly cookies; JavaScript can access only the separate CSRF values.
- Production cookies are Secure and SameSite Lax. Development permits HTTP on localhost.
- Production and packaged profiles refuse to start with the development fallback secret.
- Every refresh rotates the token. Reuse revokes the entire token family.
- Logout revokes the current family; logout-all and password changes revoke all active families.
- Access to administrator resources is role-checked and audited.

The frontend sends `X-CSRF-TOKEN` for state-changing requests, restores the current user from `/users/me`, and attempts only one refresh-and-retry cycle after an authentication failure. Tokens never enter local or session storage.

## Endpoints

| Method | Endpoint | Authentication | Result |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Public | Create patient, set cookies, return safe user |
| POST | `/api/v1/auth/login` | Public | Validate credentials and set cookies |
| POST | `/api/v1/auth/refresh` | Refresh cookie + CSRF | Rotate session tokens |
| POST | `/api/v1/auth/logout` | Access cookie + CSRF | Revoke current session and clear cookies |
| POST | `/api/v1/auth/logout-all` | Access cookie + CSRF | Revoke every session and clear cookies |
| GET | `/api/v1/users/me` | Access cookie | Return safe profile |
| PATCH | `/api/v1/users/me` | Access cookie + CSRF | Update permitted profile fields |
| POST | `/api/v1/users/me/password` | Access cookie + CSRF | Change password, revoke sessions, clear cookies |
| GET | `/api/v1/admin/users` | Administrator access cookie | Return paginated safe user records |

Responses retain the standard `data`, `errors`, and `correlation_id` envelope. Validation failures use HTTP 422 and stable `validation_error` entries with field names. Authentication responses never include token material.

## Administrator bootstrap

After applying migrations, run:

```powershell
.venv\Scripts\python -m flask --app run.py bootstrap-admin
```

The command prompts for email, name, and a hidden confirmed password. It refuses duplicate accounts and never promotes an existing patient silently.

## Privacy boundary

Registration requires only full name, email, and password. Phone and date of birth are optional. Tests and documentation use synthetic identities. Logs exclude credentials, cookies, JWTs, CSRF values, and medical responses.
