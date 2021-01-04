from datetime import timedelta
from typing import Optional
from secrets import token_urlsafe
from pydantic import BaseSettings, Field, validator
from aiplayground.types import PlayerName


class Settings(BaseSettings):
    # General Settings
    LOG_LEVEL: str = "INFO"

    # Broker Settings
    ALLOW_GUEST: bool = Field(True, description="Allow users to login without registering")
    ADMIN_EMAIL: Optional[str] = Field(None, description="Email of admin account to create")
    ADMIN_PASSWORD: Optional[str] = Field(None, description="Password of admin account to create")
    EPHEMERAL: bool = Field(True, description="Delete database on startup (for development)")
    SECRET_KEY: str = Field(token_urlsafe(32))
    ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=15)
    REFRESH_TOKEN_EXPIRES: timedelta = timedelta(hours=24)
    TOKEN_ALGORITHM: str = "HS256"
    REDIS_URL: Optional[str] = Field(None)
    REDORM_URL: Optional[str] = None
    SOCKETIO_REDIS_URL: Optional[str] = None
    USER_APPROVAL_REQUIRED: bool = Field(False, description="Require admin approval of users before the can signin")

    # Game Server / Player Settings
    ASIMOV_URL: str = Field("http://127.0.0.1:8000", description="URL for asimov broker / API")
    API_KEY: Optional[str] = None
    EMAIL: str = ""
    PASSWORD: str = ""
    RUN_ONCE: bool = Field(False, description="Whether to quit after one game")
    CONNECTION_RETRIES: int = 5

    # Game Server Settings
    GAME: str = "ScissorsPaperRock"
    LOBBY_NAME: str = "Some lobby"

    # Player Settings
    PLAYER_NAME: PlayerName = Field("Some Player", description="")
    LEEROY_JENKINS: bool = Field(False, description="Whether to keep playing new games after making an illegal move")

    @validator("REDORM_URL", pre=True, always=True)
    def default_redorm_url(cls, v, values):
        default = None if values.get("REDIS_URL") is None else f"{values['REDIS_URL']}0"
        return v or default

    @validator("SOCKETIO_REDIS_URL", pre=True, always=True)
    def default_socketio_redis_url(cls, v, values):
        # return None
        default = None if values.get("REDIS_URL") is None else f"{values['REDIS_URL']}1"
        return v or default


settings = Settings(_env_file=".env")
