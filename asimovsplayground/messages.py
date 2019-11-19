from dataclasses import dataclass, InitVar, asdict
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from asimovsplayground.broker import GameRoom


@dataclass
class MessageBase:
    sio: InitVar["GameRoom"]
    to: InitVar[str]

    def __post_init__(self, sio: "GameRoom", to):
        message_name = self.__class__.__name__[:-7].lower()
        sio.emit(message_name, asdict(self), room=to)


@dataclass
class FinishedMessage(MessageBase):
    normal: bool
    reason: Optional[str] = None
    scores: Optional[Dict[str, int]] = None


@dataclass
class GamestateMessage(MessageBase):
    board: dict
    playerid: str
    roomid: str
    turn: str


@dataclass
class JoinedMessage(MessageBase):
    playerid: str
    roomid: str


@dataclass
class PlayerMoveMessage(MessageBase):
    move: dict
    playerid: str
    roomid: str
    stateid: str


@dataclass
class RegisterMessage(MessageBase):
    playerid: str
    roomid: str


@dataclass
class RoomCreatedMessage(MessageBase):
    roomid: str
