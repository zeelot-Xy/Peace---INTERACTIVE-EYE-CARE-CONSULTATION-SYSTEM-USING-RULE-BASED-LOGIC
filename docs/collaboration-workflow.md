# Git, Google Drive, and Slack Workflow

## Sources of truth

- **Git repository:** source code, code-linked technical documentation, architecture decisions, schemas, migrations, and reproducible tests.
- **Google Drive:** academic drafts, supervisor comments, planning Sheet, screenshots, presentation material, phase report copies, and final-submission packages.
- **Slack:** morning priorities, end-of-day progress, blockers, decisions requiring attention, and phase approval notices.

Slack is coordination, not permanent technical documentation. Accepted decisions are copied into an ADR, requirement, phase report, or academic document.

## Connected project destinations

- [Google Drive workspace](https://drive.google.com/drive/folders/1FyQi4tO8tqkd1Bf2xFkEJuEyDoziAFXI)
- [Project tracker](https://docs.google.com/spreadsheets/d/1d9mcW9AyPAuenbmQyL4Nk3rCISiWayQC8ORJ4mTDNCs/edit)
- Slack workspace: `Trivest Ltd`
- Private coordination channel: `eye-care-project` (`C0BGWKL96HX`)

These destinations were created and verified on 2026-07-13. The tracker contains `Project Tasks` and `Briefing Log` tabs, controlled priority and status fields, Phase 1 evidence, and the Phase 2 backlog.

## Suggested Drive structure

1. Planning and Tracking
2. Academic Report
3. Research and References
4. Phase Completion Reports
5. Diagrams and Screenshots
6. Testing Evidence
7. Defense Presentation
8. Final Submission

The planning Sheet should record ID, phase, task, priority, status, acceptance criterion, owner, target date, blocker, evidence link, and notes.

## Morning briefing

Priorities are ordered by phase-blocking acceptance work, carry-over work, failed checks, Slack decisions, missing documentation/evidence, then non-critical improvements. Each briefing contains the current phase, three primary goals, carry-over work, blockers, scheduled checks, and the end-of-day target.

## End-of-day update

Record completed work, verification results, carry-over work, blockers, and tomorrow's likely focus. Update the Drive tracker before posting so the next briefing has durable task state.

## Phase completion

Commit accepted source and documentation, update the tracker, mirror the phase report and evidence to Drive, post a short Slack completion notice with the report link, and wait for approval.

## Connector safety

External writes use the verified destinations above. Slack kickoff or progress wording should be drafted for review unless the user explicitly requests immediate posting. If connector access is unavailable, this repository documentation remains the setup specification.
