from flaskplusplus import create_app, Settings, socketio
from flaskplusplus.auth import initialize_users
from aiplayground.broker import GameRoom
from aiplayground.api import blueprint

socketio.on_namespace(GameRoom())

app = create_app((blueprint,), Settings(), initializations=(initialize_users,))
