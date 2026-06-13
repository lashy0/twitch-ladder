class TwitchIntegrationError(Exception):
    """Base error for Twitch integration failures."""


class TwitchAuthError(TwitchIntegrationError):
    """Raised when Twitch app token acquisition fails."""


class TwitchApiError(TwitchIntegrationError):
    """Raised when a Twitch API request fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error message.
            status_code: Optional HTTP status code returned by Twitch.
            response_body: Optional raw response body for diagnostics.
        """
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)
