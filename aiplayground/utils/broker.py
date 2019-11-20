import json
from jsonschema import validate, ValidationError
from functools import wraps
from typing import TYPE_CHECKING, Optional, Tuple, Callable, Type
from flask import request
from flaskplusplus import logger
from aiplayground.exceptions import (
    AsimovErrorBase,
    NoSuchPlayer,
    NoSuchRoom,
    UnauthorizedGameServer,
    UnauthorizedPlayer,
    PlayerNotInRoom,
)
from aiplayground.messages import MessageBase
from aiplayground.api.rooms import Room
from aiplayground.api.players import Player

if TYPE_CHECKING:
    from aiplayground.broker import GameBroker


def get_room_player(
    sid: str, roomid: str, playerid: Optional[str], check_server=True
) -> Tuple[Room, Optional[Player]]:
    """
    Checks if a server has permission to act for the room as well as whether the room and player
    are correct.
    returns the room and player
    :param sid:
    :param roomid:
    :param playerid:
    :param check_server: Whether to check if the other party has game server permissions
    """
    # TODO: Remove reliance on SID for authorization
    room = Room.get(roomid)
    if room is None:
        raise NoSuchRoom
    if check_server and sid != room.sid:
        raise UnauthorizedGameServer
    if playerid is None:
        return room, None
    player = Player.get(playerid, relax=True)
    if player is None:
        raise NoSuchPlayer
    if not check_server and player.sid != sid:
        raise UnauthorizedPlayer
    if player.room_id != roomid:
        raise PlayerNotInRoom
    return room, player
