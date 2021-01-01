from typing import NewType, Union, Dict, Any
from enum import Enum


BotId = NewType("BotId", str)
PlayerId = NewType("PlayerId", str)
RoomId = NewType("RoomId", str)
StateId = NewType("StateId", str)
UserId = NewType("UserId", str)
Board = NewType("Board", Dict[str, Any])
Move = NewType("Move", Dict[str, Any])
GameRole = NewType("GameRole", str)
GameName = NewType("GameName", str)
RoomName = NewType("RoomName", str)
PlayerName = NewType("PlayerName", str)
PlayerSID = NewType("PlayerSID", str)
GameServerSID = NewType("GameServerSID", str)
BroadcastSID = NewType("BroadcastSID", str)
SpectatorSID = NewType("SpectatorSID", str)
SioSID = Union[PlayerSID, GameServerSID, BroadcastSID, SpectatorSID]
RoomDict = Dict[str, Any]


class GameStatus(str, Enum):
    lobby = "lobby"
    playing = "playing"
    finished = "finished"
