from os import environ

environ["BROKER"] = "true"
from aiplayground.settings import Settings
from flaskplusplus import create_app, socketio
from flaskplusplus.auth import initialize_users
from aiplayground.broker import GameBroker
from aiplayground.api import blueprint

socketio.on_namespace(GameBroker())

app = create_app((blueprint,), Settings(), initializations=(initialize_users,))
