from aiplayground.api.auth import auth_router, initialize_auth
from aiplayground.api.bots import bots_router
from aiplayground.api.players import players_router
from aiplayground.api.rooms import rooms_router
from aiplayground.api.tournaments import tournaments_router

all_routers = (auth_router, rooms_router, bots_router, players_router, tournaments_router)


def initialize_all():
    initialize_auth()
