# ADR 0001: Layered Application with a JSON Knowledge Base

- Status: Accepted
- Date: 2026-07-13

## Context

The application must separate user-generated records from expert-system knowledge, expose explainable decisions, and allow knowledge updates without changing Python source code.

## Decision

Use a React client and a versioned Flask REST API. HTTP routes delegate to services. SQLite will hold dynamic application records, while versioned, schema-validated JSON packages will hold questions, symptoms, conditions, rules, recommendations, risk levels, and sources. A custom forward-chaining engine will consume that knowledge in later phases.

## Consequences

- Rules remain inspectable and independent of database migrations.
- Historical consultations must retain their knowledge version.
- Strong schema, reference, upload, and rollback validation is required.
- Published-source provenance and non-diagnostic language can be audited separately from code.

