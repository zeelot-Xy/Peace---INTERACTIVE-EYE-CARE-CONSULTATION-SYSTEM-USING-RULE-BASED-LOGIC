# Architecture and Defence Diagrams

These Mermaid diagrams are source-controlled projections of the implemented architecture.

## System context

```mermaid
flowchart LR
    P["Patient"] --> UI["React web interface"]
    A["Administrator"] --> UI
    UI --> API["Flask /api/v1"]
    API --> DB[("SQLite operational data")]
    API --> KB["Versioned JSON knowledge packages"]
    API --> PDF["Immutable PDF composer"]
    KB --> SRC["Published eye-health sources"]
    API -. "educational guidance only" .-> P
```

## Layered components

```mermaid
flowchart TB
    UI["React pages, guards, forms and API client"] --> ROUTES["Flask routes: validation and authorization"]
    ROUTES --> SERVICES["Authentication, consultation, administration and report services"]
    SERVICES --> ENGINE["Deterministic rule inference"]
    SERVICES --> MODELS["SQLAlchemy models"]
    ENGINE --> LOADER["Validated immutable knowledge snapshot"]
    MODELS --> SQLITE[("SQLite")]
    LOADER --> JSON["Schemas and versioned JSON package"]
```

## Consultation and report sequence

```mermaid
sequenceDiagram
    actor Patient
    participant UI as React UI
    participant API as Consultation API
    participant KB as Frozen knowledge
    participant Engine as Rule engine
    participant DB as SQLite
    Patient->>UI: Start consultation
    UI->>API: POST /consultations
    API->>KB: Freeze active package identity
    API->>DB: Persist session
    loop One applicable question
        Patient->>UI: Answer
        UI->>API: PUT answer with revision
        API->>Engine: Evaluate partial facts
        Engine-->>API: Risk and explanation
        API->>DB: Autosave answer and revision
        API-->>UI: Next question or urgent alert
    end
    UI->>API: POST complete
    API->>Engine: Final deterministic inference
    API->>DB: Store immutable result snapshot
    UI->>API: POST report
    API->>DB: Store PDF bytes and checksum
```

## Rotated browser session

```mermaid
sequenceDiagram
    participant Browser
    participant API
    participant DB
    Browser->>API: Login credentials
    API->>DB: Verify user and record token family
    API-->>Browser: HttpOnly access + refresh cookies, CSRF cookie
    Browser->>API: State change + X-CSRF-TOKEN
    API-->>Browser: Authorized response
    Browser->>API: Refresh after access expiry
    API->>DB: Atomically consume and rotate refresh token
    API-->>Browser: Replacement cookies
    Note over API,DB: Replay revokes the compromised family
```

## Governed knowledge publication

```mermaid
flowchart LR
    ZIP["Complete uploaded ZIP"] --> BOUNDS{"Archive bounds and identity"}
    BOUNDS -->|invalid| REJECT["Reject and retain active version"]
    BOUNDS -->|valid| VALIDATE["Schema, checksum, reference, source and safety validation"]
    VALIDATE -->|invalid| REJECT
    VALIDATE -->|valid| PREVIEW["Diff and affected-rule preview"]
    PREVIEW --> PUBLISH["Serialized atomic publication"]
    PUBLISH --> RETAIN["Retain prior version and audit event"]
    RETAIN --> ACTIVE["New immutable active snapshot"]
    RETAIN --> ROLLBACK["Audited rollback if required"]
```

## Delivery projections

```mermaid
flowchart TB
    SOURCE["One verified source tree"] --> WIN["Windows PyInstaller / Waitress edition"]
    SOURCE --> SERVER["Docker / Linux server edition"]
    WIN --> LOCAL["Loopback browser + %LOCALAPPDATA% state"]
    SERVER --> PROXY["HTTPS reverse proxy"]
    SERVER --> VOLUME[("Persistent /data volume")]
    PROXY --> CLIENTS["Authorized remote browsers"]
```

