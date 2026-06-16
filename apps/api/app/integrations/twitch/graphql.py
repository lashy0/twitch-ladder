from typing import Any
from uuid import uuid4

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
        with_integrity: bool = False,
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
        self._with_integrity = with_integrity
        self._device_id = uuid4().hex
        self._integrity_token: str | None = None

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

        headers = await self._headers()

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

        if self._with_integrity and _has_integrity_error(data):
            await self._refresh_integrity_token()
            response = await self._client.post(
                self._url,
                json=payload,
                headers=await self._headers(),
            )
            if response.is_error:
                raise TwitchApiError(
                    f"Twitch GraphQL retry failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            data = response.json()
            if not isinstance(data, dict):
                raise TwitchApiError("Twitch GraphQL retry returned a non-object response")

        logger.info(
            "Twitch GraphQL operation completed operation={operation_name} has_errors={has_errors}",
            operation_name=operation_name,
            has_errors="errors" in data,
        )
        return data

    async def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Device-Id": self._device_id,
        }
        if self._client_id:
            headers["Client-Id"] = self._client_id
        if self._with_integrity:
            if self._integrity_token is None:
                await self._refresh_integrity_token()
            headers["Client-Integrity"] = self._integrity_token or ""
        return headers

    async def _refresh_integrity_token(self) -> None:
        headers = {
            "Client-Id": self._client_id,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Device-Id": self._device_id,
        }
        try:
            response = await self._client.post(
                "https://gql.twitch.tv/integrity",
                headers=headers,
            )
        except httpx.HTTPError as exc:
            raise TwitchApiError("Twitch integrity request failed") from exc
        if response.is_error:
            raise TwitchApiError(
                f"Twitch integrity request failed with status {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )
        token = response.json().get("token")
        if not isinstance(token, str) or not token:
            raise TwitchApiError("Twitch integrity response did not contain a token")
        self._integrity_token = token

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


def _has_integrity_error(data: object) -> bool:
    if not isinstance(data, dict):
        return False
    errors = data.get("errors")
    if not isinstance(errors, list):
        return False
    return any(
        isinstance(error, dict)
        and "integrity" in str(error.get("message", "")).lower()
        for error in errors
    )
