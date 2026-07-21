# Local Port Registry

Host ports are reserved per active project to prevent conflicts between concurrent local and Docker development environments. The connected Google Sheet tracker is the cross-project source of truth; this repository records its own allocation for reproducibility.

| Service | Host port | Status | Reserved on | Release condition |
| --- | ---: | --- | --- | --- |
| React/Vite frontend | 5173 | Reserved | 2026-07-13 | Release only after client delivery and explicit user confirmation |
| Flask API | 5000 | Reserved | 2026-07-13 | Release only after client delivery and explicit user confirmation |

Neither port may be allocated to another active project while this reservation is in force. Container-internal ports may be reused because Docker isolates them; the reservation applies to host-facing bindings on `localhost`.

Before starting this project, check that both ports are available. If a conflict occurs, identify and stop the unintended process instead of silently changing the registered ports. Any approved reassignment must update the environment configuration, Docker Compose bindings, CORS configuration, documentation, and the shared tracker together.
