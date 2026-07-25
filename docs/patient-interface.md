# Patient Interface Guide

## Purpose and safety boundary

The Phase 7 React interface turns the version-frozen consultation API into an accessible
patient journey. It describes outputs as educational guidance and possible indications, never
as diagnoses. Emergency and same-day advice appears before routine content and remains visible
while the patient continues answering.

## Patient journey

1. A visitor reviews the safety boundary on the landing or About page and creates an account.
2. The dashboard starts a new consultation or resumes the most recent active one.
3. The consultation presents one applicable question, saves each answer, and shows progress.
4. Previous answers can be reviewed and cleared for revision. Branch-dependent stale answers
   are removed by the service.
5. A stale browser tab reloads current state instead of overwriting a newer revision.
6. Once every applicable question is resolved, the patient completes the consultation.
7. Results show the action level, warning signs, recommendations, possible indications,
   rule explanations, evidence links, knowledge version, and disclaimer.
8. History provides secure resume and completed-result access. Report view supports browser
   printing; downloadable PDF generation remains Phase 9.

## Accessibility

- Semantic headings, landmarks, lists, labels, fieldsets, legends, and native controls are used.
- Keyboard focus has a high-contrast visible outline.
- Progress exposes `role="progressbar"` and numeric values.
- Loading updates use status regions; failures and safety escalation use alert regions.
- Selected answers are communicated through native radio state as well as colour and icons.
- Navigation collapses on narrow displays and retains an explicit accessible toggle name.
- Light and dark themes retain readable contrast and the selected theme persists locally.
- Print styles remove navigation without hiding report content.

## Failure recovery

API failures retain the current screen and show reader-facing recovery text. Initial-load
failures provide a retry action. A 409 revision conflict triggers a safe reload. Consultations
can be deliberately cancelled only after an inline confirmation, and terminal sessions cannot
be edited.

## Privacy

Tokens remain in HttpOnly cookies. The interface stores no consultation answers or tokens in
browser storage. Only the non-sensitive theme preference uses local storage. Source links open
in a separate tab without opener access.
