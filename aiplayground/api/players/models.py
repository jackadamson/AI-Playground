from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from redorm import RedormBase, many_to_one
from redorm.types import DateTime
from aiplayground.types import PlayerName, PlayerId, PlayerSID, GameRole
from aiplayground.api.players.schemas import player_schema


@dataclass
class Player(RedormBase):
    id: PlayerId = field(metadata={"unique": True})
    name: PlayerName
    sid: PlayerSID
    gamerole: Optional[GameRole]
    joined: bool = field(default=False)
    joined_at: DateTime = field(default_factory=datetime.now)
    user = many_to_one("User", backref="players")
    room = many_to_one("Room", backref="players")
    schema = player_schema
