# Twitch Ladder API

Backend API for the Twitch Ladder application.

## Project Structure

```
api/
├── app
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core application logic and utilities
│   ├── db/            # Database configuration and session management
│   ├── integrations/  # Integrations with external services
│   ├── models/        # SQLAlchemy database models
│   ├── repositories/  # Database access layer and queries
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic and application use cases
│   └── main.py        # FastAPI application entry point
├── docs/              # API documentation
├── migrations/        # Alembic database migrations
├── scripts/           # Utility scripts
└── tests/             # Test suite
```
