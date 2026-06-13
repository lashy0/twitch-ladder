import re
from datetime import datetime

_DURATION_PATTERN = re.compile(
    r"^(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?$"
)


def parse_rfc3339(value: str | None) -> datetime | None:
    """Parse a Twitch RFC3339 timestamp.

    Args:
        value: Timestamp from Twitch, usually ending with `Z`.

    Returns:
        Parsed datetime, or `None` when the input is empty.
    """
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_twitch_duration(value: str | None) -> int | None:
    """Parse a Twitch duration string into seconds.

    Args:
        value: Twitch duration such as `1h2m3s`, `42m`, or `30s`.

    Returns:
        Duration in seconds, or `None` when the input is empty or invalid.
    """
    if not value:
        return None

    match = _DURATION_PATTERN.match(value)
    if match is None:
        return None

    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    return hours * 3600 + minutes * 60 + seconds
