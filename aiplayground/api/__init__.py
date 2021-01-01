from aiplayground.api.auth import auth_router, initialize_auth
from aiplayground.api.bot import bots_router
from aiplayground.api.players import players_router
from aiplayground.api.rooms import rooms_router

all_routers = (auth_router, rooms_router, bots_router, players_router)


def initialize_all():
    initialize_auth()
