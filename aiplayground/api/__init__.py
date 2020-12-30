from aiplayground.api.players import players_router
from aiplayground.api.rooms import rooms_router
from aiplayground.api.auth import auth_router, initialize_auth


def initialize_all():
    initialize_auth()
