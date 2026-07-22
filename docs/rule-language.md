# Rule Language

## Intent

Rules are data, not Python conditionals. This keeps the knowledge inspectable and lets later packages add a supported pathway without changing inference-engine source code. Phase 3 defines and validates the language; Phase 5 will execute it.

## Expression forms

A leaf predicate has a fact ID, operator, and comparison value:

```json
{"fact_id": "fact_age_years", "operator": "gte", "value": 55}
```

Supported operators are `eq`, `neq`, `in`, `not_in`, `gt`, `gte`, `lt`, and `lte`. Expressions may be nested with `all`, `any`, and `not`:

```json
{
  "all": [
    {"fact_id": "fact_sudden_floaters", "operator": "eq", "value": true},
    {"fact_id": "fact_light_flashes", "operator": "eq", "value": true}
  ]
}
```

`all` is logical AND, `any` is logical OR, and `not` negates one expression. An absent answer is not equivalent to `false`; incomplete-fact behavior belongs to the Phase 5 engine specification.

## Rule outcome

Each rule contains:

- a stable ID and descriptive name;
- priority from 1 to 1000;
- one `when` expression;
- one or more possible-indication IDs;
- one risk-level ID;
- one or more recommendation IDs;
- a human-readable rationale and explanation template; and
- cited evidence.

Priority resolves ordering between otherwise eligible rules. Risk rank is independent: the highest safety risk must prevail even if a lower-risk rule has another strong match. The future rule-match score will describe satisfied authored criteria, not diagnostic probability.

## Safety example

`rule_chemical_exposure` matches a reported chemical exposure, has priority 1000, selects `risk_emergency`, and returns immediate irrigation and emergency-care guidance. Its two citations support the first-aid and escalation assertions. A common dry-eye rule may also match surface discomfort, but it cannot lower the emergency result.
