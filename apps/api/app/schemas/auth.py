from pydantic import BaseModel


class AuthUserRead(BaseModel):
    twitch_id: str
    login: str
    display_name: str
    avatar_url: str | None


class AuthSessionRead(BaseModel):
    authenticated: bool
    user: AuthUserRead | None = None
