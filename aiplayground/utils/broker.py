from typing import Optional, Tuple
from redorm import InstanceNotFound
from aiplayground.exceptions import (
    NoSuchPlayer,
    NoSuchRoom,
    UnauthorizedGameServer,
    UnauthorizedPlayer,
    PlayerNotInRoom,
)
from aiplayground.api.rooms import Room
from aiplayground.api.players import Player


def get_room_player(sid: str, roomid: str, playerid: Optional[str], check_server=True) -> Tuple[Room, Optional[Player]]:
    """
    Checks if a server has permission to act for the room as well as whether the room and player
    are correct.
    returns the room and player
    :param sid:
    :param roomid:
    :param playerid:
    :param check_server: Whether to check if the other party has game server permissions
    """
    try:
        room = Room.get(roomid)
    except InstanceNotFound as e:
        raise NoSuchRoom from e
    if check_server and sid != room.server_sid:
        raise UnauthorizedGameServer
    if playerid is None:
        return room, None
    try:
        player = Player.get(playerid)
    except InstanceNotFound as e:
        raise NoSuchPlayer from e
    if not check_server and player.sid != sid:
        raise UnauthorizedPlayer
    if player.room is not None and player.room.id != roomid:
        raise PlayerNotInRoom
    return room, player
