# Development of an Interactive Eye Care Consultation System Using Rule-Based Logic

## Submission note

This is the adaptable academic manuscript. Institution-specific title pages, declarations,
certification, pagination, citation style, and candidate details must be applied from the
departmental template without changing the verified technical claims. No patient or clinician
study was conducted; the evaluation is software-conformance testing of an academic prototype.

## Abstract

Limited awareness of eye warning signs can contribute to delayed professional assessment, while
unqualified self-diagnosis can create false reassurance or unsafe action. This project designed
and implemented an interactive educational eye-care consultation system using transparent
rule-based logic. The application presents adults with one applicable question at a time,
evaluates normalized answers through a deterministic forward-chaining engine, escalates the
highest matched safety risk, and explains the rules and published sources supporting each
result. React 19 provides the accessible browser interface; Flask exposes a versioned REST API;
SQLite retains accounts, consultations, immutable results, reports, and audit evidence; and
versioned JSON packages separate eye-care knowledge from program logic. The package contains
common concerns, chronic-risk pathways, and urgent red flags sourced from recognized public
eye-health organizations. Verification covered 152 backend tests with 91.30% statement
coverage, 17 frontend tests, linting, production builds, dependency review, migration cycles,
and Windows and Docker persistence smoke tests. The system met its specified functional,
explainability, authorization, reproducibility, accessibility, and packaging requirements.
These results demonstrate implementation correctness for the tested scenarios, not diagnostic
accuracy, clinical effectiveness, or regulatory approval. The principal contribution is a
defensible, data-driven expert-system prototype whose decisions can be traced from patient
answers through authored rules to cited evidence.

## Chapter One: Introduction

### 1.1 Background

Vision affects education, employment, mobility, and independence. The World Health Organization
describes vision impairment as a significant public-health concern and emphasizes access to
timely eye care [S1]. Eye symptoms vary from minor irritation to time-sensitive emergencies.
Digital education may help a person recognize an appropriate next action, but a poorly bounded
system can be mistaken for diagnosis or professional care.

Expert systems encode domain knowledge as facts and rules. Unlike an opaque predictive model,
a rule-based system can show which supplied facts satisfied an authored rule and why a risk
level was selected. This transparency suits an academic consultation-support prototype where
safety, reproducibility, and explanation are more important than statistical prediction.

### 1.2 Problem statement

General internet searches may present unstructured or contradictory advice, while access to an
eye-care professional may not be immediate. A user needs a structured way to describe symptoms,
recognize urgent patterns, and receive sourced educational guidance without the software
claiming to diagnose. The corresponding engineering problem is to provide this interaction
while preventing skipped questions, incomplete information, stale rules, unauthorized access,
or conflicting recommendations from weakening a safety warning.

### 1.3 Aim and objectives

The aim was to develop an interactive educational eye-care consultation system using rule-based
logic.

The objectives were to:

1. elicit and document functional, safety, privacy, and deployment requirements;
2. create a versioned and sourced eye-care knowledge representation;
3. implement deterministic forward chaining with explainable outcomes and safety-first conflict
   resolution;
4. provide secure patient and administrator workflows for consultations, history, reports, and
   knowledge governance;
5. verify the implementation through automated, integration, accessibility, security-negative,
   and release tests; and
6. deliver both a self-contained Windows edition and a persistent server deployment option.

### 1.4 Research questions

1. How can eye-care guidance be represented so that content changes do not require changes to
   the inference program?
2. How can a rule engine preserve incomplete information while ensuring that the highest safety
   risk prevails?
3. How can consultation outcomes remain explainable and reproducible after the knowledge base
   changes?
4. Can the resulting prototype satisfy its specified usability, security, and deployment
   requirements in repeatable software tests?

### 1.5 Significance

The project demonstrates how sourced declarative knowledge, explicit safety boundaries, and
testable inference traces can be combined in a final-year software artifact. It also provides a
foundation for subsequent expert review, localization, usability study, and clinical
validation. The contribution is the software architecture and transparent reasoning process,
not a validated medical intervention.

### 1.6 Scope

Version 1 supports English-speaking adults and patient and administrator roles. It covers 15
authored eye-care condition pathways and 21 rules, including common concerns, chronic-risk
indications, and urgent red flags. It supports accounts, one-question consultation, autosave,
resume, explainable results, filtered history, immutable PDF reports, governed knowledge
publication, local Windows delivery, and single-instance server delivery.

Image diagnosis, machine learning, prescriptions, appointments, telemedicine, hospital or
electronic-record integration, paediatric use, and multilingual content are excluded.

### 1.7 Limitations

The knowledge base has not received expert clinical review and the application is not a medical
device. Published sources cannot replace local clinical protocols or an examination. Rule
coverage is finite; omitted, misunderstood, or unrepresented facts may change the appropriate
action. SQLite and process-local controls limit horizontal server scaling. The evaluation used
fictional scenarios and software tests rather than patients, clinicians, diagnostic accuracy
measures, or a formal usability sample.

### 1.8 Definition of terms

- **Fact:** a normalized consultation answer available to the engine.
- **Forward chaining:** evaluation that starts from supplied facts and fires rules whose
  conditions are satisfied.
- **Knowledge package:** an immutable, versioned set of JSON collections and source records.
- **Possible indication:** a non-diagnostic educational pattern produced by a matched rule.
- **Rule-match score:** the degree to which authored rule criteria are satisfied; it is not
  diagnostic probability.
- **Red flag:** an authored fact pattern requiring urgent safety advice.

## Chapter Two: Literature Review

### 2.1 Eye-care information and timely referral

WHO materials establish the public-health importance of preventing avoidable vision impairment
and obtaining appropriate eye care [S1, S2]. Nigerian policy provides the local service,
prevention, and referral context [S16]. These sources support an educational referral aid, but
not autonomous diagnosis.

The knowledge scope uses public information from the National Eye Institute on dry eye,
blepharitis, conjunctivitis, cataract, glaucoma, diabetic retinopathy, age-related macular
degeneration, and retinal detachment [S3–S5, S7–S11]. CDC information supports conjunctivitis
infection-control and contact-lens warning content [S6, S12]. NHS and MedlinePlus emergency
material supports urgent pathways for sudden vision loss, chemical exposure, and eye injury
[S13–S15]. Each assertion in the machine-readable package references its source ID.

### 2.2 Clinical decision support and expert systems

Clinical decision-support systems organize patient information to assist decisions. In this
project the term is used cautiously: the user is a patient, the output is educational, and the
system does not issue a diagnosis. A knowledge-based expert system normally separates a
knowledge base, an inference mechanism, and an explanation facility. This separation enables a
reviewer to inspect both the authored content and the reasoning algorithm.

### 2.3 Rule-based reasoning and forward chaining

Production rules express an antecedent and conclusion: if conditions over facts are satisfied,
the rule contributes an outcome. Forward chaining is suitable because consultation answers
arrive as facts and multiple rules may be evaluated without selecting a single diagnostic
hypothesis. JSON rules allow new reviewed content to execute without Python changes.

Ordinary Boolean evaluation treats unknown information as false, which may hide the difference
between a negative answer and an unanswered question. The implemented engine therefore uses
three values—true, false, and unknown—through nested `AND`, `OR`, and `NOT` groups. Priorities
give stable ordering, while conflict resolution separately ensures that the highest safety rank
governs displayed advice.

### 2.4 Explainability and reproducibility

For every result, the system retains the knowledge version, normalized facts, matched rules,
evidence, and inference trace. This is more defensible than presenting an unexplained score.
Freezing the package identity when a consultation begins prevents later publication from
rewriting historical meaning. Immutable PDF bytes provide a reproducible projection of the
stored result.

### 2.5 Ethical, privacy, and safety considerations

Medical wording can influence behavior even when software is labelled educational. The design
therefore prohibits diagnostic certainty, prescribing, unsupported treatment claims, and
unsafe delay recommendations. Urgent warnings appear during partial consultation and cannot be
hidden by optional branches. The privacy design minimizes profile fields, uses protected cookie
sessions, enforces ownership, redacts audit evidence, and provides governed retention, backup,
restore, and deletion operations.

### 2.6 Identified gap

Many symptom resources are static, while generic conversational systems may not expose a stable
rule-to-source chain. The project addresses the academic gap by combining one-question
interaction, three-valued safety-first inference, immutable sourced knowledge, governed
publication, reproducible reporting, and dual local/server delivery in one testable prototype.
It does not claim to close the separate clinical-validation gap.

## Chapter Three: Methodology and System Design

### 3.1 Development method

An iterative, approval-gated process divided the work into governance, authentication,
knowledge design, loading, inference, consultation, patient interface, administration, reports,
verification, hardening, packaging, documentation, and final audit. Each accepted phase
required implementation, tests, documentation, a descriptive Git commit, and review. This
reduced the risk of building later behavior on an unverified foundation and preserved a
traceable project history.

Requirements were maintained in a traceability matrix and mapped to automated evidence. Formal
clinical interviews were unavailable, so medical content acquisition used reputable published
sources and recorded that limitation.

### 3.2 Functional and non-functional requirements

Core functions are account management, one-question consultation, answer revision, urgent
partial escalation, deterministic completion, history, PDF reporting, administrator oversight,
and knowledge validation/publication/rollback. Non-functional requirements include
explainability, reproducibility, accessibility, authorization, data minimization, safe failure,
portable deployment, and maintainability.

### 3.3 Architecture

The system uses a layered architecture. React pages communicate with `/api/v1`; Flask routes
validate and authorize; services own use cases and transactions; SQLAlchemy models retain
operational state; and the inference subsystem reads an immutable knowledge snapshot. Business
rules do not reside in routes. The complete visual models are in
[Architecture and Defence Diagrams](architecture/diagrams.md).

### 3.4 Data design

UUID-keyed relational records represent users, consultations, responses, reports, refresh-token
families, revocations, application events, audit logs, and retained knowledge versions.
Constraints enforce unique normalized email, response identity, terminal-state invariants, and
report reproducibility. SQLite foreign keys are enabled and Alembic controls schema evolution.
Knowledge remains outside the operational database as versioned JSON.

### 3.5 Knowledge representation and acquisition

Each package declares schema and content versions, publication metadata, inventory checksums,
source registry, questions, symptoms, conditions, rules, recommendations, and risk levels.
Stable IDs connect collections. JSON Schema validates structure; semantic validation checks
versions, duplicates, references, citations, risk order, emergency evidence, and prohibited
wording. An update is activated atomically only after complete validation, and the last valid
snapshot remains active when a candidate fails.

### 3.6 Inference design

Answers are normalized to strict fact types. Recursive expressions support logical groups and
comparison operators. Unknown facts propagate through strong three-valued logic. Matched rules
are ordered deterministically by priority and ID. The result aggregator deduplicates outcomes,
retains evidence, chooses the highest risk, suppresses advice that would dilute urgent action,
and emits a stable trace and disclaimer.

### 3.7 Consultation and interface design

The consultation service freezes knowledge identity at creation, determines the next applicable
question, stores one answer per question, and increments a revision for optimistic concurrency.
Safety questions remain applicable regardless of ordinary branching. The React interface uses
semantic landmarks, native controls, labelled errors, visible focus, responsive navigation,
dark mode, and distinct urgent and non-diagnostic result regions.

### 3.8 Security and privacy design

Passwords use Werkzeug's adaptive hashing. Fifteen-minute access and seven-day refresh JWTs are
held in HttpOnly cookies. Refresh tokens rotate atomically and only hashed identifiers are
stored. CSRF uses a header/cookie double-submit check. Persisted roles, ownership queries,
request limits, rate limiting, secure headers, strict origins, upload bounds, audit redaction,
and safe error envelopes constrain the main threats. Operations include verified backup,
restore, dry-run retention, and explicit deletion.

### 3.9 Deployment design

The Windows edition bundles React, Flask, Waitress, Python, migrations, schemas, and seed
knowledge. Mutable data and first-run secrets live under `%LOCALAPPDATA%` for the client user.
The server edition uses a non-root multi-stage Docker image and persistent `/data` volume behind
HTTPS. Both serve the compiled interface and API from one origin.

### 3.10 Evaluation method

Evaluation combined unit, integration, API, migration, component, accessibility-semantic,
security-negative, dependency, build, and artifact smoke tests. Table-driven inference tests
covered every operator and rule. Cross-layer defence scenarios used fictional accounts and
answers. Release checks verified first run, restart, retained data, stable installation secrets,
and Docker volume persistence. No clinical accuracy, sensitivity, specificity, or patient
outcome was measured.

## Chapter Four: Implementation, Testing, and Results

### 4.1 Development environment

The implementation uses Python 3.12+, Flask, SQLAlchemy, Alembic, SQLite, ReportLab, Waitress,
React 19, TypeScript, Vite, Tailwind CSS, Axios, React Hook Form, Zod, pytest, Ruff, Vitest,
Testing Library, ESLint, PyInstaller, and Docker Compose.

### 4.2 Implemented subsystems

The completed application includes secure registration and session management; sourced
knowledge authoring and loading; forward-chaining inference; version-frozen consultation;
responsive patient screens; administrator reporting and publication governance; immutable PDF
history; security/privacy operations; and Windows and Linux/server release paths. A consistent
API envelope and correlation ID connect interface errors to safe operational logs.

### 4.3 Representative inference

When a supplied answer set satisfies a retinal-detachment warning rule, the engine records each
evaluated leaf and group, marks the rule matched, links the relevant NEI source [S11], emits the
urgent risk, and prevents routine advice from diluting it. If a required fact is absent, the
condition remains unknown rather than becoming a negative clinical assertion. A newly validated
JSON rule follows the same engine path without a Python edit.

### 4.4 Verification results

The Phase 12 release gate passed 152 backend tests with 91.30% statement coverage and 17
frontend tests. Ruff, ESLint, TypeScript, Vite production compilation, migration checks, Python
dependency review, and the governed npm production audit passed. A 31,968,481-byte Windows
archive was built and smoke-tested for health, first-run migration, persistent random secrets,
registration, consultation creation, restart, and retained state. Its SHA-256 was
`ba6aee0ffc94e17d56acd3a630de759821af0a6276ce8e60daa14b88960fb1c0`.
An isolated non-root Docker deployment passed health, migration, restart, and persistent-volume
checks.

### 4.5 Requirements evaluation

The traceability matrix records every implemented requirement and links it to code,
verification, and documentation. Tests cover authentication failure and revocation, role and
ownership boundaries, knowledge corruption, inference operators and conflicts, incomplete and
emergency paths, consultation concurrency, accessibility semantics, report reproducibility,
unsafe uploads, audit redaction, backup/restore, and release persistence.

### 4.6 Discussion

The results answer the research questions at the software level. Declarative packages allow
content evolution independent of engine code; three-valued logic preserves incomplete facts;
highest-risk aggregation protects urgent advice; and frozen versions plus traces explain and
reproduce outcomes. The same verified source can be delivered locally or on a persistent
server. These findings are bounded to the authored rules and tested scenarios and must not be
interpreted as evidence of clinical performance.

## Chapter Five: Summary, Conclusion, and Recommendations

### 5.1 Summary

The project transformed published adult eye-health guidance into a versioned, cited knowledge
package and implemented a secure interactive system around it. The architecture separates
interface, use-case services, persistence, inference, and knowledge. Approval-gated development
and executable traceability retained evidence from foundation through release.

### 5.2 Contribution

The principal contribution is an end-to-end academic expert-system prototype with a transparent
rule language, incomplete-fact semantics, safety-first conflict resolution, early red-flag
escalation, governed knowledge updates, historical reproducibility, and client-operable release
artifacts.

### 5.3 Conclusion

The system satisfies its documented implementation requirements and can support a credible
software demonstration and defence. Rule-based logic was appropriate because its decisions are
deterministic, inspectable, and separable from application code. The software remains an
educational prototype and should not be deployed as a diagnostic service without expert review,
clinical evaluation, governance, and applicable regulatory assessment.

### 5.4 Recommendations

Future work should obtain ophthalmology and optometry review; conduct ethics-approved usability
and clinical-safety studies; localize content and referral pathways; add verified accessibility
testing with disabled participants; support a managed multi-user database and distributed
limits for scaling; introduce governed email verification and account recovery; and reassess
medical-device obligations before any clinical use.

## References

The list below uses project source IDs. Convert it to the institution's required citation style
without changing titles, organizations, dates, URLs, or retrieval dates. Full metadata and live
links are maintained in [Source Register](source-register.md).

- **S1** `source_who_vision_impairment` — World Health Organization, *Blindness and vision
  impairment*.
- **S2** `source_who_refractive_errors` — World Health Organization, *Blindness and vision
  impairment: refractive errors*.
- **S3** `source_nei_dry_eye` — National Eye Institute, *Dry Eye*.
- **S4** `source_nei_blepharitis` — National Eye Institute, *Blepharitis*.
- **S5** `source_nei_pink_eye` — National Eye Institute, *Pink Eye*.
- **S6** `source_cdc_conjunctivitis` — Centers for Disease Control and Prevention, *Clinical
  Overview of Pink Eye (Conjunctivitis)*.
- **S7** `source_nei_cataracts` — National Eye Institute, *Cataracts*.
- **S8** `source_nei_glaucoma_types` — National Eye Institute, *Types of Glaucoma*.
- **S9** `source_nei_diabetic_retinopathy` — National Eye Institute, *Diabetic Retinopathy*.
- **S10** `source_nei_amd` — National Eye Institute, *Age-Related Macular Degeneration*.
- **S11** `source_nei_retinal_detachment` — National Eye Institute, *Retinal Detachment*.
- **S12** `source_cdc_contact_lens_infections` — Centers for Disease Control and Prevention,
  *What Causes Contact Lens-related Eye Infections*.
- **S13** `source_nhs_eye_injuries` — National Health Service, *Eye injuries*.
- **S14** `source_nhs_vision_loss` — National Health Service, *Vision loss*.
- **S15** `source_medlineplus_eye_emergencies` — MedlinePlus, *Eye emergencies*.
- **S16** `source_nigeria_eye_health_policy` — Federal Ministry of Health and Social Welfare,
  Nigeria, *National Eye Health Policy*.

## Appendices

- Appendix A: [Requirements Traceability Matrix](requirements-traceability.md)
- Appendix B: [Architecture and Defence Diagrams](architecture/diagrams.md)
- Appendix C: [Knowledge Schema Reference](knowledge-schema-reference.md) and
  [Rule Language](rule-language.md)
- Appendix D: [REST API Reference](api-reference.md)
- Appendix E: [Requirements-to-Test Evidence](requirements-to-test-report.md)
- Appendix F: [Defence Demonstration](defence-demo.md)
- Appendix G: [User Guide](user-guide.md) and [Administrator Guide](administration.md)
- Appendix H: [Phase Reports](phase-reports/) and Git history

