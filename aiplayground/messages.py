from dataclasses import dataclass, asdict
from typing import Optional, Dict
import aiplayground.schemas as schemas
from flaskplusplus import logger


@dataclass
class MessageBase:
    schema = dict()

    def send(self, sio, to: Optional[str] = None, callback: Optional[callable] = None):
        message_name = self.__class__.__name__[:-7].lower()
        if to is None:
            logger.debug(f"Sending message {message_name}:\n{self!r}")
            sio.emit(message_name, asdict(self), callback=callback)
        else:
            logger.debug(f"Sending message {message_name} to {to!r}:\n{self!r}")
            sio.emit(message_name, asdict(self), room=to, callback=callback)


# Sent from broker
@dataclass
class FinishedMessage(MessageBase):
    """
    :from broker
    :to player
    """

    # TODO: Add schema
    normal: bool
    roomid: str
    reason: Optional[str] = None
    scores: Optional[Dict[str, int]] = None


@dataclass
class GamestateMessage(MessageBase):
    """
    :from broker
    :to player
    """

    # TODO: Add schema
    board: dict
    playerid: str
    roomid: str
    turn: str


@dataclass
class JoinedMessage(MessageBase):
    """
    :from broker
    :to player
    """

    # TODO: Add schema
    playerid: str
    roomid: str
    gamerole: Optional[str] = None


@dataclass
class PlayerMoveMessage(MessageBase):
    """
    :from broker
    :to server
    """

    # TODO: Add schema
    move: dict
    playerid: str
    roomid: str
    stateid: str


@dataclass
class RegisterMessage(MessageBase):
    """
    :from broker
    :to server
    """

    # TODO: Add schema
    playerid: str
    roomid: str


@dataclass
class RoomCreatedMessage(MessageBase):
    """
    :from broker
    :to server
    """

    # TODO: Add schema
    roomid: str


@dataclass
class RoomsMessage(MessageBase):
    """
    :from broker
    :to player
    """

    # TODO: Add schema
    rooms: dict


# Sent from server
@dataclass
class CreateRoomMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.createroom_schema
    name: str
    game: str
    maxplayers: int


@dataclass
class JoinSuccessMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.joinsuccess_schema
    playerid: str
    roomid: str
    gamerole: Optional[str] = None


@dataclass
class JoinFailMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.joinfail_schema
    playerid: str
    roomid: str
    reason: Optional[str] = None


@dataclass
class GameUpdateMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.gameupdate_schema
    roomid: str
    visibility: str
    epoch: int
    board: dict
    stateid: Optional[str] = None
    playerid: Optional[str] = None
    turn: Optional[str] = None


@dataclass
class FinishMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.finish_schema
    roomid: str
    normal: bool
    scores: Optional[Dict[str, int]] = None
    reason: Optional[str] = None


# Sent from player
@dataclass
class JoinMessage(MessageBase):
    """
    :from player
    :to broker
    """

    schema = schemas.join_schema
    roomid: str
    name: str


@dataclass
class MoveMessage(MessageBase):
    """
    :from player
    :to broker
    """

    schema = schemas.move_schema
    playerid: str
    roomid: str
    move: dict


@dataclass
class ListMessage(MessageBase):
    """
    :from broker
    :to player
    """

    pass
