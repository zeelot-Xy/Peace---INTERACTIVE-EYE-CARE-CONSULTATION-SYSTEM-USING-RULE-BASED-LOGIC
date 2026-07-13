# Contribution Guide

## Phase gate

Work is completed one approved phase at a time. A phase is ready for review only when its acceptance criteria pass, documentation is current, no placeholders remain, and the changes have a descriptive commit.

## Branches and commits

- Use focused branches when remote collaboration begins.
- Use Conventional Commit prefixes: `feat`, `fix`, `docs`, `test`, `refactor`, `build`, and `chore`.
- Keep commits reviewable and never commit secrets, generated dependencies, databases, or patient information.

## Quality requirements

- Keep business logic out of HTTP routes.
- Add tests for new behavior and failure modes.
- Update the traceability matrix and relevant documentation with each feature.
- Use non-diagnostic, safety-conscious language throughout the product.
- Do not leave TODOs, placeholder implementations, or disabled checks in accepted work.

## Review checklist

1. Tests, linting, and production builds pass.
2. Security and privacy implications are considered.
3. User-facing behavior is accessible and documented.
4. Architecture decisions with lasting impact have an ADR.
5. Evidence is recorded in the phase report.

