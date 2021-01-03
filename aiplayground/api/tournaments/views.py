from typing import List

from fastapi import APIRouter, Security

from aiplayground.api.auth import get_user_id
from aiplayground.api.tournaments.models import Tournament
from aiplayground.api.tournaments.schemas import (
    TournamentPartialSchema,
    TournamentPrivateSchema,
    CreateTournamentSchema,
)
from aiplayground.types import TournamentId

tournaments_router = APIRouter(prefix="/tournaments", dependencies=[Security(get_user_id)], tags=["Tournaments"])


@tournaments_router.get("/all", response_model=List[TournamentPartialSchema])
def list_tournaments():
    return Tournament.list()


@tournaments_router.post(
    "/", response_model=TournamentPrivateSchema, dependencies=[Security(get_user_id, scopes=["admin"])]
)
def create_tournament(data: CreateTournamentSchema):
    return Tournament.create(name=data.name, description=data.description, game=data.game)


@tournaments_router.get(
    "/admin/{tournament_id}",
    response_model=List[TournamentPrivateSchema],
    dependencies=[Security(get_user_id, scopes=["admin"])],
)
def admin_get_tournament(tournament_id: TournamentId):
    return Tournament.get(tournament_id)
