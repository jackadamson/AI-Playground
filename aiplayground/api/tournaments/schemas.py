from typing import List, Optional

from pydantic import BaseModel

from aiplayground.api.tournaments.models import MatchState
from aiplayground.types import BotId, MatchId, ParticipantId, TournamentId, GameName, TournamentKey


class BotPartialSchema(BaseModel):
    id: BotId
    name: str

    class Config:
        orm_mode = True


class ParticipantPartialSchema(BaseModel):
    id: ParticipantId
    bot: BotPartialSchema
    disqualified: bool

    class Config:
        orm_mode = True


class MatchPartialSchema(BaseModel):
    id: MatchId
    state: MatchState
    participants: List[ParticipantPartialSchema]

    class Config:
        orm_mode = True


class TournamentPartialSchema(BaseModel):
    id: TournamentId
    name: str
    game: GameName
    description: Optional[str] = None
    matches: List[MatchPartialSchema]
    participants: List[ParticipantPartialSchema]

    class Config:
        orm_mode = True


class TournamentPrivateSchema(BaseModel):
    id: TournamentId
    name: str
    game: GameName
    description: Optional[str] = None
    api_key: TournamentKey

    class Config:
        orm_mode = True


class CreateTournamentSchema(BaseModel):
    name: str
    game: GameName
    description: Optional[str] = None
