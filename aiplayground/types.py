from typing import NewType, Union

PlayerId = NewType("PlayerId", str)
RoomId = NewType("RoomId", str)
StateId = NewType("StateId", str)
Board = NewType("Board", dict)
Move = NewType("Move", dict)
GameRole = NewType("GameRole", str)
GameName = NewType("GameName", str)
RoomName = NewType("RoomName", str)
PlayerName = NewType("PlayerName", str)
PlayerSID = NewType("PlayerSID", str)
GameServerSID = NewType("GameServerSID", str)
BroadcastSID = NewType("BroadcastSID", str)
SioSID = Union[PlayerSID, GameServerSID, BroadcastSID]
