# Knowledge Schema Reference

All contracts use JSON Schema Draft 2020-12, reject unknown properties, and require schema version `1.0.0`. Every content document repeats the semantic `content_version` so a mixed package is rejected.

| File | Collection | Purpose | Key references |
|---|---|---|---|
| `manifest.json` | `files` | Package identity, scope, disclaimer, lifecycle state, and SHA-256 inventory | Schema and content filenames |
| `sources.json` | `sources` | Published evidence registry | None |
| `symptoms.json` | `symptoms` | Normalized consultation facts and value types | Sources |
| `questions.json` | `questions` | User-facing prompts mapped to facts | Facts and sources |
| `conditions.json` | `conditions` | Cautious possible-indication descriptions | Sources |
| `recommendations.json` | `recommendations` | Non-prescribing care actions | Sources |
| `risk-levels.json` | `risk_levels` | Ordered safety response levels | Sources |
| `rules.json` | `rules` | Declarative conditions, conclusions, risk, rationale, and explanation | Facts, conditions, recommendations, risks, sources |

## Source date handling

`published_or_updated` is an ISO date when the publisher displays a verified date. It is `null` with `date_status: "not_listed"` when no reliable date is shown. `retrieved_on` is always required.

## Fact types

- `boolean`: yes/no information.
- `integer`: a bounded whole number such as adult age.
- `choice`: one value from an explicit `allowed_values` list.

Question answer types are `yes_no`, `integer`, and `single_choice`. Phase 6 will define branching and answer persistence; Phase 3 only defines the authored prompts and their fact mapping.

## Risk invariants

The validator requires exactly this order:

| ID | Rank | Meaning |
|---|---:|---|
| `risk_routine` | 1 | Routine comprehensive examination |
| `risk_prompt` | 2 | Prompt professional assessment |
| `risk_urgent` | 3 | Same-day professional assessment |
| `risk_emergency` | 4 | Emergency eye care now |

The later inference engine must select the highest matched rank. It must never average or suppress an emergency result.

## Package integrity

The manifest lists all seven content documents, the schema assigned to each, and a lowercase SHA-256 digest of its exact bytes. The authoring validator rejects missing files, malformed JSON, invalid schemas, mixed content versions, broken references, duplicate IDs, checksum changes, unsafe risk order, weak emergency evidence, and prohibited wording.
