from typing import NewType

PlayerId = NewType("PlayerId", str)
RoomId = NewType("RoomId", str)
StateId = NewType("StateId", str)
Board = NewType("Board", dict)
Move = NewType("Move", dict)
GameRole = NewType("GameRole", str)
GameName = NewType("GameName", str)
RoomName = NewType("RoomName", str)
PlayerName = NewType("PlayerName", str)
