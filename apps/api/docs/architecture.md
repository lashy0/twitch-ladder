# API Architecture

This document describes the intended backend architecture for `apps/api`.

## Main Flow

The first product flow is:

```text
channel login -> VOD list -> VOD scan -> chat aggregates -> ladder
```

The backend should own this flow. The frontend should not call Twitch APIs directly.

## Layer Boundaries

Use the existing application layers with clear responsibilities:

```text
routes -> services -> repositories -> models
          services -> integrations
```

- Routes validate HTTP input, call services, and return response schemas.
- Services implement application use cases.
- Repositories own database queries and persistence.
- Models describe persisted database state.
- Integrations call external APIs such as Twitch Helix or unofficial Twitch GraphQL.

Rules:

- Routes should not contain business logic or raw SQL.
- Repositories should not call external APIs.
- Services should not depend on raw GraphQL query shape.
- Twitch DTOs, database models, and public API schemas should stay separate.

## Twitch Data

Twitch is an external data source, not the application database.

Use local projections for product data that needs to be shown, scanned, retried, refreshed, or aggregated. For example, a Twitch VOD becomes a local `Video`, and chat activity becomes `VideoChatter` aggregates.

Data source preference:

```text
Official Twitch Helix first
Unofficial Twitch GraphQL only behind adapter
```

The unofficial GraphQL API is useful for gaps, but it is more fragile. Keep it isolated under integrations so future schema changes do not leak into services, repositories, or frontend contracts.

## Long-Running Work

VOD scanning should not run as a single long HTTP request.

The expected API behavior is:

```text
POST scan request -> create ScanJob -> return job id
GET job status -> frontend polls progress
GET ladder -> frontend reads persisted aggregate result
```

`ScanJob` stores persistent progress and failure state. A background worker can be introduced later without changing the public flow.

## Related Docs

- [Data model](./data-model.md)
