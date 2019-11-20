from environs import Env
from secrets import token_hex

env = Env()
env.read_env()

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

# For a player
# Whether to keep playing new games after losing due to an illegal move
LEEROY_JENKINS = env.bool("LEEROY_JENKINS", default=False)


class Settings:
    SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL", default="sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = env.str("FLASK_ENV", default="development")
    FLASK_DEBUG = FLASK_ENV == "development"
    LOG_LEVEL = env.str("LOG_LEVEL", default="DEBUG" if FLASK_DEBUG else "INFO")
    SECRET_KEY = env.str("SECRET_KEY", default=token_hex(16).encode("utf-8"))
