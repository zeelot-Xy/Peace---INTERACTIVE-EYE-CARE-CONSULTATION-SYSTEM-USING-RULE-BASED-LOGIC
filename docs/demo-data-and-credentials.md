# Demonstration Data and Credentials

## Safety rule

Use fictional identities and answers only. Never place real patient information, passwords,
tokens, database files, reports, or installation secrets in source control, Drive, Slack,
screenshots, or presentation files.

## Fictional demonstration identity

The suggested patient identity is:

- Full name: `Amina Demo`
- Email: `amina.demo@example.test`
- Date of birth: `1990-01-15`
- Phone: leave blank

The `.test` domain cannot receive internet email and is reserved for testing. The application
does not seed this account; create it during the demonstration so registration remains visible.

## Password procedure

No password is shipped. Immediately before a demonstration:

1. Generate or choose a unique password of at least 12 characters.
2. Enter it only in the local or controlled demonstration environment.
3. Do not display it in screen recordings or browser developer tools.
4. Delete or reset the disposable demonstration database after the defence if it is no longer
   required.

Create the administrator through `bootstrap-admin` or `Create Administrator.cmd`. Use a
different fictional `.test` email and a different temporary password. The bootstrap command
will not silently promote the patient account.

The client receives this procedure, not a universal username and password. This avoids a known
credential being reused after delivery.

## Prepared inference scenarios

- `backend/examples/demo-facts-emergency.json` reports chemical exposure and demonstrates
  immediate emergency escalation.
- `backend/examples/demo-facts-routine.json` reports gradual near blur in a fictional 46-year-old
  without severe pain and demonstrates routine, non-diagnostic indications.

Run either example from `backend`:

```powershell
.venv\Scripts\python -m flask --app run.py inference-evaluate `
  --facts-file examples\demo-facts-emergency.json --json
```

These are inference fixtures, not patient records. The full browser demonstration should follow
the [Defence Demonstration Guide](defence-demo.md).

