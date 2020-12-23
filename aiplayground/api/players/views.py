from typing import List

from fastapi import APIRouter

from aiplayground.api.players.models import Player
from aiplayground.api.players.schemas import PlayerSchema

players_router = APIRouter(prefix="/players")


@players_router.get("/", tags=["Players"], response_model=List[PlayerSchema])
def list_players():
    return Player.list()
