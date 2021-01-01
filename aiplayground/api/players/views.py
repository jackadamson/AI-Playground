from typing import List

from fastapi import APIRouter, Security

from aiplayground.api.auth import get_claims
from aiplayground.api.players.models import Player
from aiplayground.api.players.schemas import PlayerSchema

players_router = APIRouter(prefix="/players", tags=["Players"], dependencies=[Security(get_claims)])


@players_router.get("/", response_model=List[PlayerSchema])
def list_players():
    return Player.list()
