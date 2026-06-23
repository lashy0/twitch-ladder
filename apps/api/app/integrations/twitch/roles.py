from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol

from app.core.config import settings
from app.integrations.twitch.dto import TwitchUserData
from app.integrations.twitch.exceptions import TwitchApiError
from app.integrations.twitch.graphql import TwitchGraphQLClient
from app.integrations.twitch.utils import parse_rfc3339

_CHANNEL_ROLES_QUERY = """
query ChannelRoles($login: String!) {
  user(login: $login) {
    id
    login
    displayName
    profileImageURL(width: 150)
    createdAt
    followers { totalCount }
    follows { totalCount }
    mods(first: 100) {
      edges {
        grantedAt
        node {
          id
          login
          displayName
          profileImageURL(width: 150)
          createdAt
        }
      }
    }
    vips(first: 100) {
      edges {
        grantedAt
        node {
          id
          login
          displayName
          profileImageURL(width: 150)
          createdAt
        }
      }
    }
  }
}
"""


class TwitchRoleCategory(StrEnum):
    """Supported channel role categories exposed by the product API."""

    MODS = "mods"
    VIPS = "vips"
    FOUNDERS = "founders"
    ARTISTS = "artists"


@dataclass(frozen=True, slots=True)
class TwitchRoleData:
    """Normalized user role on a Twitch channel."""

    category: TwitchRoleCategory
    user: TwitchUserData
    granted_at: datetime | None


@dataclass(frozen=True, slots=True)
class TwitchRolePage:
    """One Twitch channel role projection."""

    channel: TwitchUserData
    items: list[TwitchRoleData]
    followers_total: int | None
    follows_total: int | None


class TwitchRoleGraphQLClient(Protocol):
    async def execute(
        self,
        *,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]: ...

    async def aclose(self) -> None: ...


class TwitchRoleClient:
    """Adapter for Twitch channel role projections.

    Twitch does not expose every role category through public Helix endpoints.
    Keep the unofficial GraphQL shape contained in this adapter and return only
    normalized product DTOs to services.
    """

    def __init__(self, client: TwitchRoleGraphQLClient | None = None) -> None:
        self._client = client or TwitchGraphQLClient(
            client_id=settings.TWITCH_GQL_FALLBACK_CLIENT_ID,
        )
        self._owns_client = client is None

    async def list_by_login(self, login: str) -> TwitchRolePage:
        payload = await self._client.execute(
            query=_CHANNEL_ROLES_QUERY,
            variables={"login": login.lower()},
            operation_name="ChannelRoles",
        )
        if payload.get("errors"):
            raise TwitchApiError(
                "Twitch GraphQL rejected the role query",
                response_body=str(payload.get("errors")),
            )

        user = _as_dict(_as_dict(payload.get("data")).get("user"))
        if not user:
            raise TwitchApiError("Twitch user was not found", status_code=404)

        channel = _parse_user(user)
        items: list[TwitchRoleData] = []
        for category in (TwitchRoleCategory.MODS, TwitchRoleCategory.VIPS):
            items.extend(_parse_role_items(user.get(category.value), category))

        followers = _as_dict(user.get("followers"))
        follows = _as_dict(user.get("follows"))
        return TwitchRolePage(
            channel=channel,
            items=_deduplicate_roles(items),
            followers_total=_optional_integer(followers.get("totalCount")),
            follows_total=_optional_integer(follows.get("totalCount")),
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()


def _parse_role_items(
    value: object, category: TwitchRoleCategory
) -> list[TwitchRoleData]:
    connection = _as_dict(value)
    edges = connection.get("edges")
    if isinstance(edges, list):
        return [
            role
            for role in (_parse_role_edge(edge, category) for edge in edges)
            if role is not None
        ]

    nodes = connection.get("nodes")
    if isinstance(nodes, list):
        return [
            role
            for role in (
                _parse_role_node(node, category, granted_at=None) for node in nodes
            )
            if role is not None
        ]

    values = value if isinstance(value, list) else []
    return [
        role
        for role in (
            _parse_role_node(node, category, granted_at=None) for node in values
        )
        if role is not None
    ]


def _parse_role_edge(
    value: object, category: TwitchRoleCategory
) -> TwitchRoleData | None:
    edge = _as_dict(value)
    return _parse_role_node(
        edge.get("node"),
        category,
        granted_at=parse_rfc3339(_string(edge.get("grantedAt"))),
    )


def _parse_role_node(
    value: object,
    category: TwitchRoleCategory,
    *,
    granted_at: datetime | None,
) -> TwitchRoleData | None:
    node = _as_dict(value)
    if not node:
        return None
    return TwitchRoleData(
        category=category,
        user=_parse_user(node),
        granted_at=granted_at if granted_at is not None else None,
    )


def _parse_user(value: object) -> TwitchUserData:
    user = _as_dict(value)
    twitch_id = _string(user.get("id"))
    login = _string(user.get("login"))
    if twitch_id is None or login is None:
        raise TwitchApiError("Twitch role user response was incomplete")
    return TwitchUserData(
        twitch_id=twitch_id,
        login=login,
        display_name=_string(user.get("displayName")) or login,
        avatar_url=_string(user.get("profileImageURL")),
        created_at=parse_rfc3339(_string(user.get("createdAt"))),
    )


def _deduplicate_roles(items: Iterable[TwitchRoleData]) -> list[TwitchRoleData]:
    seen: set[tuple[TwitchRoleCategory, str]] = set()
    result: list[TwitchRoleData] = []
    for item in items:
        key = (item.category, item.user.twitch_id)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _as_dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _optional_integer(value: object) -> int | None:
    return value if isinstance(value, int) else None
