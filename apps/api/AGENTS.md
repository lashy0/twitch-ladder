# AGENTS.md

## Stack

- FastAPI with async SQLAlchemy.
- Pydantic v2 for API schemas and settings.
- Alembic for migrations.
- `httpx` for external HTTP clients.
- Redis may be used for cache, rate limiting, and background job infrastructure.

## Implementation Rules

- Routes should not contain business logic or raw SQL.
- Services should not know concrete Twitch query documents or database session details beyond repositories.
- Repositories should not call Twitch or other external APIs.
- Store VOD scan progress in `ScanJob`-style records instead of relying on a single long HTTP request.
- Store chat activity as aggregates first; avoid storing every chat message unless a feature requires it.
