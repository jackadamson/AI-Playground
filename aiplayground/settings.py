from environs import Env
from secrets import token_urlsafe
from os import environ

if environ.get("BROKER") == "true":
    # If broker, inherit flaskplusplus default settings
    from flaskplusplus.settings import Settings as BaseSettings
else:
    BaseSettings = object

env = Env()
env.read_env()


class Settings(BaseSettings):
    ALLOW_GUEST = env.bool("ALLOW_GUEST", default=True)
    SQLALCHEMY_DATABASE_URI = env.str(
        "DATABASE_URL", default=f"sqlite:////tmp/asimovdev-{token_urlsafe(8)}.db"
    )

    # For a player
    # Name for player
    PLAYER_NAME = env.str("ASIMOV_PLAYER_NAME", default="Some Player")
    # Whether to keep playing new games after losing due to playing an illegal move
    LEEROY_JENKINS = env.bool("LEEROY_JENKINS", default=False)

    # URL of the asimov API/broker
    ASIMOV_URL = env.str("ASIMOV_URL", default="http://127.0.0.1:5000")
    EMAIL = env.str("EMAIL", default="")
    PASSWORD = env.str("PASSWORD", default="")

    # For gameservers and players
    # Whether to keep playing after one game
    RUN_ONCE = env.bool("RUN_ONCE", default=False)
    # How many times to try to reconnect
    CONNECTION_RETRIES = env.int("CONNECTION_RETRIES", default=5)

    # Settings for a game server
    GAME = env.str("ASIMOV_GAME", default="ScissorsPaperRock")
    LOBBY_NAME = env.str("ASIMOV_LOBBY_NAME", default=f"A {GAME} lobby")
