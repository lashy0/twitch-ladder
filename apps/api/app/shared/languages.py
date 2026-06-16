def normalize_language(value: str | None) -> str:
    language = (value or "").strip().replace("_", "-").upper()
    return language or "OTHER"
