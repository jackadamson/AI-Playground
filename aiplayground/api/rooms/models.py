from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from redorm import RedormBase, one_to_many, many_to_one
from redorm.types import DateTime

from aiplayground.types import (
    PlayerId,
    RoomId,
    StateId,
    RoomName,
    GameName,
    Board,
    Move,
    GameServerSID,
    BroadcastSID,
)


@dataclass
class Room(RedormBase):
    id: RoomId = field(metadata={"unique": True})
    name: RoomName
    game: GameName
    maxplayers: int
    server_sid: GameServerSID
    board: Optional[Board]
    status: str = field(default="lobby", metadata={"index": True})
    turn: Optional[PlayerId] = field(default=None)
    normal_finish: Optional[bool] = field(default=None)
    created_at: DateTime = field(default_factory=datetime.now)
    players = one_to_many("Player", backref="room")
    states = one_to_many("GameState", backref="room")

    @property
    def broadcast_sid(self) -> BroadcastSID:
        return BroadcastSID(f"room_{self.id}")

    @property
    def spectator_sid(self) -> BroadcastSID:
        return BroadcastSID(f"room_spectator_{self.id}")


@dataclass
class GameState(RedormBase):
    id: StateId = field(metadata={"unique": True})
    player = many_to_one("Player", backref="moves")
    room = many_to_one("Room", backref="states")
    epoch: Optional[int] = None
    move: Optional[Move] = None
    board: Optional[Board] = None
    turn: Optional[PlayerId] = None
    timestamp: DateTime = field(default_factory=datetime.now)
