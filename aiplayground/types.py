from typing import NewType, Union, Dict, Any
from dataclasses_jsonschema import JsonSchemaMixin, FieldEncoder

PlayerId = NewType("PlayerId", str)
RoomId = NewType("RoomId", str)
StateId = NewType("StateId", str)
Board = NewType("Board", Dict[str, Any])
Move = NewType("Move", Dict[str, Any])
GameRole = NewType("GameRole", str)
GameName = NewType("GameName", str)
RoomName = NewType("RoomName", str)
PlayerName = NewType("PlayerName", str)
PlayerSID = NewType("PlayerSID", str)
GameServerSID = NewType("GameServerSID", str)
BroadcastSID = NewType("BroadcastSID", str)
SioSID = Union[PlayerSID, GameServerSID, BroadcastSID]
RoomDict = Dict[str, Any]


class UUIDField(FieldEncoder):
    @property
    def json_schema(self):
        return {
            "type": "string",
            "pattern": r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
        }


JsonSchemaMixin.register_field_encoders(
    {PlayerId: UUIDField(), RoomId: UUIDField(), StateId: UUIDField()}
)
