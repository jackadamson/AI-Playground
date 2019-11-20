from dataclasses import dataclass, asdict
from typing import Optional, Dict
import aiplayground.schemas as schemas
from flaskplusplus import logger
from aiplayground.exceptions import all_exceptions
from aiplayground.types import (
    PlayerId,
    RoomId,
    StateId,
    Board,
    Move,
    GameRole,
    PlayerName,
    RoomName,
    GameName,
)


@dataclass
class MessageBase:
    schema = dict()
    _callback = None

    def send(self, sio, to: Optional[str] = None, callback: Optional[callable] = None):
        message_name = self.__class__.__name__[:-7].lower()
        self._callback = callback
        if to is None:
            logger.debug(f"Sending message {message_name}:\n{self!r}")
            sio.emit(message_name, asdict(self), callback=self.callback)
        else:
            logger.debug(f"Sending message {message_name} to {to!r}:\n{self!r}")
            sio.emit(message_name, asdict(self), room=to, callback=self.callback)

    def callback(self, msgtype=None, error=None):
        if msgtype == "fail":
            raise all_exceptions[error["error"]](
                f"{error['details']!r},\nReceived in response to: {self!r}"
            )
        elif self._callback:
            self._callback()


# Sent from broker
@dataclass
class GamestateMessage(MessageBase):
    """
    :from broker
    :to player
    """

    # TODO: Add schema
    board: Board
    playerid: PlayerId
    roomid: RoomId
    turn: PlayerId


@dataclass
class JoinedMessage(MessageBase):
    """
    :from broker
    :to player
    """

    # TODO: Add schema
    playerid: PlayerId
    roomid: RoomId
    gamerole: Optional[GameRole] = None


@dataclass
class PlayerMoveMessage(MessageBase):
    """
    :from broker
    :to server
    """

    # TODO: Add schema
    move: Move
    playerid: PlayerId
    roomid: RoomId
    stateid: StateId


@dataclass
class RegisterMessage(MessageBase):
    """
    :from broker
    :to server
    """

    # TODO: Add schema
    playerid: PlayerId
    roomid: RoomId


@dataclass
class RoomCreatedMessage(MessageBase):
    """
    :from broker
    :to server
    """

    # TODO: Add schema
    roomid: RoomId


@dataclass
class RoomsMessage(MessageBase):
    """
    :from broker
    :to player
    """

    # TODO: Add schema
    rooms: dict


@dataclass
class JoinAcknowledgement(MessageBase):
    """
    Indicates a player has received a Joined event
    :from broker
    :to player
    """

    roomid: RoomId
    playerid: PlayerId


# Sent from server
@dataclass
class CreateRoomMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.createroom_schema
    name: RoomName
    game: GameName
    maxplayers: int


@dataclass
class JoinSuccessMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.joinsuccess_schema
    playerid: PlayerId
    roomid: RoomId
    gamerole: Optional[GameRole] = None


@dataclass
class JoinFailMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.joinfail_schema
    playerid: PlayerId
    roomid: RoomId
    reason: Optional[str] = None


@dataclass
class GameUpdateMessage(MessageBase):
    """
    :from server
    :to broker
    """

    schema = schemas.gameupdate_schema
    roomid: RoomId
    visibility: str
    epoch: int
    board: Board
    stateid: Optional[StateId] = None
    playerid: Optional[PlayerId] = None
    turn: Optional[PlayerId] = None


@dataclass
class FinishMessage(MessageBase):
    """
    :from server or broker
    :to broker
    """

    schema = schemas.finish_schema
    roomid: RoomId
    normal: bool
    scores: Optional[Dict[PlayerId, int]] = None
    reason: Optional[str] = None
    fault: Optional[PlayerId] = None


# Sent from player
@dataclass
class JoinMessage(MessageBase):
    """
    :from player
    :to broker
    """

    schema = schemas.join_schema
    roomid: RoomId
    name: PlayerName


@dataclass
class MoveMessage(MessageBase):
    """
    :from player
    :to broker
    """

    schema = schemas.move_schema
    playerid: PlayerId
    roomid: RoomId
    move: Move


@dataclass
class ListMessage(MessageBase):
    """
    :from broker
    :to player
    """

    pass
