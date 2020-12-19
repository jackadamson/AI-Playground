from os import environ

environ["BROKER"] = "true"
from aiplayground.settings import settings
from flaskplusplus import create_app, socketio
from flaskplusplus.auth import initialize_users
from aiplayground.broker import GameBroker
from aiplayground.api import blueprint


app = create_app((blueprint,), settings, initializations=(initialize_users,))
socketio.on_namespace(GameBroker())
