from pydantic import BaseSettings


class Settings(BaseSettings):
    ALLOW_GUEST: bool = True
    LOG_LEVEL: str = "INFO"
    ALLOW_API_KEYS: bool = True
    # For a player
    # Name for player
    PLAYER_NAME: str = "Some Player"
    # Whether to keep playing new games after losing due to playing an illegal move
    LEEROY_JENKINS: bool = False

    # URL of the asimov API/broker
    ASIMOV_URL: str = "http://127.0.0.1:5000"
    EMAIL: str = ""
    PASSWORD: str = ""

    # For gameservers and players
    # Whether to keep playing after one game
    RUN_ONCE: bool = False
    # How many times to try to reconnect
    CONNECTION_RETRIES: int = 5

    # Settings for a game server
    GAME: str = "ScissorsPaperRock"
    LOBBY_NAME: str = f"A {GAME} lobby"
    IS_GUNICORN: bool = False
    IS_SHELL: bool = False
    EPHEMERAL: bool = False


settings = Settings()
