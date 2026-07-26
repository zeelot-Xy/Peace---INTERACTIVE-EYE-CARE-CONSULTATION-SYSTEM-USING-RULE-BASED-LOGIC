# Phase 11 Academic Methodology

Phase 11 uses threat-model-led security hardening. Analysis identifies assets, actors, entry
points, trust boundaries, and plausible misuse paths before changing controls. Review then
traces untrusted sources through their closest guard to authentication, authorization, parsing,
filesystem, database, logging, or publication effects. Candidate weaknesses retain their
counterevidence rather than being promoted from keyword matches alone.

The main controls follow defence in depth. Request bounds reduce parser resource abuse;
endpoint throttling limits credential guessing and repeated expensive work; atomic refresh
rotation reduces session replay races; persisted-role comparison shortens privilege-revocation
delay; explicit CORS and hosted secure-cookie profiles reduce ambiguity; security headers reduce
browser interpretation risk; and generic error envelopes avoid implementation disclosure.

Knowledge ZIP files are treated as hostile structured input even though upload is
administrator-only. Validation combines compressed and expanded size bounds, entry and ratio
limits, path and link rejection, exact filename allowlisting, bounded reads, immutable identity
comparison, and serialized publication. Audit evidence is centrally redacted and
application-layer immutable.

Privacy evaluation uses data minimization and lifecycle controls instead of indefinite academic
retention. Dry-run-first maintenance makes deletion observable before application. Verified
SQLite backup and restore support recoverability, while patient deletion retains only minimal
non-clinical governance evidence.

Verification combines negative API tests, concurrency-sensitive token logic, archive controls,
audit mutation tests, backup and restore checks, retention checks, linting, coverage, builds,
and dependency advisories. These results demonstrate implemented software controls, not
clinical safety, regulatory compliance, penetration-test certification, or protection from a
compromised host administrator.
