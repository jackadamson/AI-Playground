from typing import List

from fastapi import APIRouter, Security, HTTPException, status

from aiplayground.api.auth import get_user_id
from aiplayground.api.bots import Bot
from aiplayground.api.tournaments.models import Tournament
from aiplayground.api.tournaments.schemas import (
    TournamentPartialSchema,
    TournamentPrivateSchema,
    CreateTournamentSchema,
    ParticipantPartialSchema,
)
from aiplayground.api.tournaments.tournaments import add_player
from aiplayground.exceptions import AlreadyInTournament
from aiplayground.logging import logger
from aiplayground.types import TournamentId, UserId, BotId
from redorm import InstanceNotFound

tournaments_router = APIRouter(prefix="/tournaments", dependencies=[Security(get_user_id)], tags=["Tournaments"])


@tournaments_router.get("/all", response_model=List[TournamentPartialSchema])
def list_tournaments():
    return Tournament.list()


@tournaments_router.get("/all/{tournament_id}", response_model=TournamentPartialSchema)
def get_tournament(tournament_id: TournamentId):
    return Tournament.get(tournament_id)


@tournaments_router.post("/all/{tournament_id}/join", response_model=ParticipantPartialSchema)
def join_tournament(tournament_id: TournamentId, bot_id: BotId, user_id: UserId = Security(get_user_id)):
    try:
        tournament = Tournament.get(tournament_id)
        bot = Bot.get(bot_id)
    except InstanceNotFound as e:
        logger.warning(f"Failed to add bot to tournament\n{e!r}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if bot.user.id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        return add_player(bot, tournament)
    except AlreadyInTournament as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already in tournament") from e


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
