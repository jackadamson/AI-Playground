from dataclasses import dataclass, field
from typing import Optional, List
from secrets import token_urlsafe
from functools import partial
from enum import Enum

from aiplayground.api.bots import Bot
from aiplayground.api.rooms import Room
from aiplayground.types import TournamentId, ParticipantId, MatchId, GameName, PlayerSID, TournamentKey
from redorm import RedormBase, many_to_one, one_to_many, many_to_many, one_to_one


class MatchState(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    errored = "errored"
    deleted = "deleted"


@dataclass
class Tournament(RedormBase):
    """"""

    id: TournamentId
    name: str = field(metadata={"unique": True})
    game: GameName = field(metadata={"index": True})
    description: Optional[str] = field(default=None)
    api_key: TournamentKey = field(default_factory=partial(token_urlsafe, 32))
    participants = one_to_many("Participant", backref="tournament")
    matches = one_to_many("Match", backref="tournament")


@dataclass
class Participant(RedormBase):
    id: ParticipantId
    index: int
    tournament = many_to_one(Tournament, backref="participants")
    bot = many_to_one(Bot, backref="participants")
    disqualified: bool = field(default=False)
    matches = many_to_many("Match", backref="players")


@dataclass
class Match(RedormBase):
    id: MatchId
    index: int
    tournament = many_to_one(Tournament, backref="matches")
    state: MatchState = field(default=MatchState.pending, metadata={"index": True})
    players = many_to_many(Participant, backref="matches")
    room = one_to_one(Room, backref="match")


@dataclass
class PlayerQueueEntry(RedormBase):
    """
    A player
    """

    tournament_id: TournamentId = field(metadata={"index": True})
    sid: PlayerSID = field(metadata={"index": True})
    participant_id: ParticipantId = field(metadata={"index": True})
