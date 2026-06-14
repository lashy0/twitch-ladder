# Twitch Ladder API

FastAPI backend for Twitch Ladder.

## Stack

- FastAPI, Pydantic v2
- Async SQLAlchemy, Alembic
- PostgreSQL, Redis
- `httpx` for Twitch clients
- Ruff, mypy, pytest

## Commands

Run from `apps/api`:

```bash
uv run fastapi dev app/main.py
uv run alembic upgrade head
uv run ruff check .
uv run mypy .
uv run pytest
```

See `docs/` for architecture and data model notes.
