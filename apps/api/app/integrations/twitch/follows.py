from typing import Any

from app.core.config import settings
from app.integrations.twitch.dto import (
    TwitchFollowData,
    TwitchFollowPage,
    TwitchUserData,
)
from app.integrations.twitch.exceptions import TwitchApiError
from app.integrations.twitch.graphql import TwitchGraphQLClient
from app.integrations.twitch.utils import parse_rfc3339

_CHANNEL_FOLLOWS_QUERY = """
query ChannelFollows($login: String!, $first: Int!, $after: Cursor) {
  user(login: $login) {
    id
    login
    displayName
    profileImageURL(width: 150)
    createdAt
    followers { totalCount }
    follows(first: $first, after: $after) {
      totalCount
      edges {
        cursor
        followedAt
        node {
          id
          login
          displayName
          profileImageURL(width: 150)
          createdAt
          broadcastSettings { language }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""


class TwitchFollowClient:
    """Adapter for Twitch's public follow connection."""

    def __init__(self, client: TwitchGraphQLClient | None = None) -> None:
        self._client = client or TwitchGraphQLClient(
            client_id=settings.TWITCH_GQL_FALLBACK_CLIENT_ID,
        )
        self._owns_client = client is None

    async def list_by_login(
        self, login: str, *, first: int = 100, after: str | None = None
    ) -> TwitchFollowPage:
        payload = await self._client.execute(
            query=_CHANNEL_FOLLOWS_QUERY,
            variables={"login": login.lower(), "first": first, "after": after},
            operation_name="ChannelFollows",
        )
        if payload.get("errors"):
            raise TwitchApiError("Twitch GraphQL rejected the follow query")

        user = _as_dict(_as_dict(payload.get("data")).get("user"))
        if not user:
            raise TwitchApiError("Twitch user was not found", status_code=404)

        connection = _as_dict(user.get("follows"))
        edges = connection.get("edges")
        if not isinstance(edges, list):
            edges = []

        items: list[TwitchFollowData] = []
        last_cursor: str | None = None
        for edge_value in edges:
            edge = _as_dict(edge_value)
            node = _as_dict(edge.get("node"))
            twitch_id = node.get("id")
            login_value = node.get("login")
            if not isinstance(twitch_id, str) or not isinstance(login_value, str):
                continue
            cursor = edge.get("cursor")
            if isinstance(cursor, str):
                last_cursor = cursor
            items.append(
                TwitchFollowData(
                    twitch_id=twitch_id,
                    login=login_value,
                    display_name=_string(node.get("displayName")) or login_value,
                    avatar_url=_string(node.get("profileImageURL")),
                    created_at=parse_rfc3339(_string(node.get("createdAt"))),
                    followed_at=parse_rfc3339(_string(edge.get("followedAt"))),
                    language=_string(_as_dict(node.get("broadcastSettings")).get("language")),
                )
            )

        total = _integer(connection.get("totalCount"), len(items))
        page_info = _as_dict(connection.get("pageInfo"))
        end_cursor = _string(page_info.get("endCursor")) or last_cursor
        has_next_page = page_info.get("hasNextPage") is True or (
            after is None and len(items) < total
        )
        followers = _as_dict(user.get("followers"))
        twitch_id = _string(user.get("id"))
        user_login = _string(user.get("login"))
        if twitch_id is None or user_login is None:
            raise TwitchApiError("Twitch user response was incomplete")
        return TwitchFollowPage(
            channel=TwitchUserData(
                twitch_id=twitch_id,
                login=user_login,
                display_name=_string(user.get("displayName")) or user_login,
                avatar_url=_string(user.get("profileImageURL")),
                created_at=parse_rfc3339(_string(user.get("createdAt"))),
            ),
            items=items,
            total=total,
            followers_total=_optional_integer(followers.get("totalCount")),
            cursor=end_cursor if has_next_page else None,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()


def _as_dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _integer(value: object, default: int) -> int:
    return value if isinstance(value, int) else default


def _optional_integer(value: object) -> int | None:
    return value if isinstance(value, int) else None
