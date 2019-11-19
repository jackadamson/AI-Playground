from flaskplusplus import create_app, Settings, socketio
from flaskplusplus.auth import initialize_users
from asimovsplayground.broker import GameRoom
from asimovsplayground.api import blueprint

socketio.on_namespace(GameRoom())

app = create_app((blueprint,), Settings(), initializations=(initialize_users,))
