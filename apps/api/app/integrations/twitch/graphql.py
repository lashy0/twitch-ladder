from typing import Any

import httpx
from loguru import logger

from app.core.config import settings
from app.integrations.twitch.exceptions import TwitchApiError

JsonObject = dict[str, Any]


class TwitchGraphQLClient:
    """Generic client for Twitch's unofficial GraphQL endpoint."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        url: str = settings.TWITCH_GQL_URL,
        client_id: str = settings.TWITCH_GQL_CLIENT_ID,
    ) -> None:
        """Initialize the GraphQL client.

        Args:
            client: Optional shared HTTP client.
            url: GraphQL endpoint URL.
            client_id: Optional Twitch web client ID for the `Client-Id` header.
        """
        self._client = client or httpx.AsyncClient(timeout=settings.TWITCH_HTTP_TIMEOUT_SECONDS)
        self._owns_client = client is None
        self._url = url
        self._client_id = client_id

    async def aclose(self) -> None:
        """Close owned HTTP resources."""
        if self._owns_client:
            await self._client.aclose()

    async def execute(
        self,
        *,
        query: str,
        variables: JsonObject | None = None,
        operation_name: str | None = None,
    ) -> JsonObject:
        """Execute a raw GraphQL operation.

        Args:
            query: GraphQL query or mutation document.
            variables: Optional GraphQL variables.
            operation_name: Optional operation name.

        Returns:
            Raw GraphQL JSON response as a dictionary.
        """
        payload: JsonObject = {"query": query, "variables": variables or {}}
        if operation_name is not None:
            payload["operationName"] = operation_name

        headers: dict[str, str] = {}
        if self._client_id:
            headers["Client-Id"] = self._client_id

        logger.info(
            "Executing Twitch GraphQL operation={operation_name}",
            operation_name=operation_name,
        )
        try:
            response = await self._client.post(self._url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            logger.opt(exception=exc).warning(
                "Twitch GraphQL request failed operation={operation_name}",
                operation_name=operation_name,
            )
            raise TwitchApiError("Twitch GraphQL request failed") from exc

        if response.is_error:
            logger.warning(
                "Twitch GraphQL returned error operation={operation_name} status={status_code}",
                operation_name=operation_name,
                status_code=response.status_code,
            )
            raise TwitchApiError(
                f"Twitch GraphQL request failed with status {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )

        data = response.json()
        if not isinstance(data, dict):
            logger.warning(
                "Twitch GraphQL returned non-object response operation={operation_name}",
                operation_name=operation_name,
            )
            raise TwitchApiError("Twitch GraphQL returned a non-object response")

        logger.info(
            "Twitch GraphQL operation completed operation={operation_name} has_errors={has_errors}",
            operation_name=operation_name,
            has_errors="errors" in data,
        )
        return data

    async def __aenter__(self) -> "TwitchGraphQLClient":
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit async context manager and close owned resources."""
        await self.aclose()
