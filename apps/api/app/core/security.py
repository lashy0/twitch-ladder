from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

_JWT_ALGORITHM = "HS256"
_JWT_REQUIRED_CLAIMS = ["aud", "exp", "iat", "iss", "sub"]


def create_access_token(
    claims: dict[str, Any],
    *,
    secret: str,
    expires_delta: timedelta,
    issuer: str,
    audience: str,
) -> str:
    """Create a signed JWT access token."""
    issued_at = datetime.now(UTC)
    payload = {
        **claims,
        "iat": issued_at,
        "exp": issued_at + expires_delta,
        "iss": issuer,
        "aud": audience,
    }
    return jwt.encode(payload, secret, algorithm=_JWT_ALGORITHM)


def decode_access_token(
    token: str,
    *,
    secret: str,
    issuer: str,
    audience: str,
) -> dict[str, Any] | None:
    """Verify and decode a signed JWT access token."""
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[_JWT_ALGORITHM],
            audience=audience,
            issuer=issuer,
            options={"require": _JWT_REQUIRED_CLAIMS},
        )
    except InvalidTokenError:
        return None

    return payload if isinstance(payload, dict) else None
