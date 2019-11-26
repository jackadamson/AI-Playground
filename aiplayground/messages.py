from dataclasses import dataclass, asdict
from typing import Optional, Dict, Callable
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
    SioSID,
)
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class MessageBase(JsonSchemaMixin):
    _callback = None

    def send(
        self, sio, to: Optional[SioSID] = None, callback: Optional[Callable] = None
    ):
        message_name = self.__class__.__name__[:-7].lower()
        self._callback = callback
        if to is None:
            logger.debug(f"Sending message {message_name}:\n{self!r}")
            sio.emit(message_name, asdict(self), callback=self.callback)
        else:
            logger.debug(f"Sending message {message_name} to {to!r}:\n{self!r}")
            sio.emit(message_name, asdict(self), room=to, callback=self.callback)

    def callback(self, msgtype=None, *args):
        if msgtype == "fail":
            error = args[1]
            raise all_exceptions[error["error"]](
                f"{error['details']!r},\nReceived in response to: {self!r}"
            )
        elif self._callback:
            logger.debug(f"Recv Callback: msgtype={msgtype!r}, args={args!r}")
            self._callback(*args)


# Sent from broker
@dataclass
class GamestateMessage(MessageBase):
    """
    :param dict board: New game board
    :param str roomid: ID of room that the state change occurred in
    :param int epoch: Number of state updates that occured before this state update
    :param str playerid|None: Intended recipient of the message
    :param str|None turn: ID of player who's turn it is

    Message from broker to players to indicate a change in game state
    """

    board: Board
    roomid: RoomId
    epoch: int
    playerid: Optional[PlayerId]
    turn: Optional[PlayerId]


@dataclass
class JoinedMessage(MessageBase):
    """
    :param str roomid: ID of room that the player joined
    :param str playerid: Player that joined
    :param str|None gamerole: Role the player has in the game, eg. 'white' in chess

    Message from broker to players on successfully joining a room
    """

    playerid: PlayerId
    roomid: RoomId
    gamerole: Optional[GameRole] = None


@dataclass
class PlayerMoveMessage(MessageBase):
    """
    :param dict move: Move the player is making
    :param str roomid: ID of room that the move is in
    :param str playerid: Player that is moving
    :param str stateid: ID of the state used to correlate a move with a resulting state

    Message from broker to game server with a players move
    """

    move: Move
    playerid: PlayerId
    roomid: RoomId
    stateid: StateId


@dataclass
class RegisterMessage(MessageBase):
    """
    :param str roomid: ID of room that the player wishes to join
    :param str playerid: Player that is joining

    Message from broker to game server requesting a player joins the room
    """

    playerid: PlayerId
    roomid: RoomId


@dataclass
class RoomCreatedMessage(MessageBase):
    """
    :param str roomid: ID of the new game room

    Message from broker to game server acknowledging creation of a game room
    """

    roomid: RoomId


@dataclass
class JoinAcknowledgementMessage(MessageBase):
    """
    :param str roomid: ID of room that the player joined
    :param str playerid: Player that acknowledged joining the room

    Message from broker to game server indicating that a player has acknowledge a JoinSuccess
    """

    roomid: RoomId
    playerid: PlayerId


@dataclass
class FinishedMessage(MessageBase):
    """
    :param str roomid: Room that finished the game
    :param bool normal: Whether the game finished normally, such as a player winning, as opposed to due to an error
    :param dict|None scores: The scores of the players in the game
    :param str|None reason: Why the game finished abnormally
    :param str|None fault: Player tha caused the game to end abnormally

    Message from broker to player indicating a game finished
    """

    roomid: RoomId
    normal: bool
    scores: Optional[Dict[PlayerId, int]] = None
    reason: Optional[str] = None
    fault: Optional[PlayerId] = None


# Sent from server
@dataclass
class CreateRoomMessage(MessageBase):
    """
    :param str name: Name of the lobby to create
    :param str game: Name of the game that will be played
    :param int maxplayers: The number of players allowed in the game

    Message from game server to broker requesting creation of a game room
    """

    name: RoomName
    game: GameName
    maxplayers: int


@dataclass
class JoinSuccessMessage(MessageBase):
    """
    :param str playerid: Player that successfully joined
    :param str roomid: Room that the player joined
    :param str|None gamerole: Role of the player in the game, eg. 'white' in chess

    Message from game server to broker confirming player joining a room
    """

    playerid: PlayerId
    roomid: RoomId
    gamerole: Optional[GameRole] = None


@dataclass
class JoinFailMessage(MessageBase):
    """
    :param str playerid: Player that failed to join
    :param str roomid: Room that the player failed to join
    :param str|None reason: Reason the player failed to join

    Message from game server to broker reporting a player failed to join a room
    """

    playerid: PlayerId
    roomid: RoomId
    reason: Optional[str] = None


@dataclass
class GameUpdateMessage(MessageBase):
    """
    :param str roomid: Room that the player failed to join
    :param str visibility: Visibility of game state update ('public', 'broadcast' or 'private')
    :param int epoch: The number of state transitions the game has had (turn count)
    :param dict board: New board state
    :param str|None stateid: ID of the state used to correlate a move with a resulting state
    :param str|None playerid: Player to send private update to
    :param str|None turn: Player who's turn it is

    From gameserver, informing broker that a player failed to join a room
    """

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
    :param str roomid: Room that finished the game
    :param bool normal: Whether the game finished normally, such as a player winning, as opposed to due to an error
    :param dict|None scores: The scores of the players in the game
    :param str|None reason: Why the game finished abnormally
    :param str|None fault: Player tha caused the game to end abnormally

    Message from game server to broker, or broker to player indicating a game finished
    """

    roomid: RoomId
    normal: bool
    scores: Optional[Dict[PlayerId, int]] = None
    reason: Optional[str] = None
    fault: Optional[PlayerId] = None


# Sent from player
@dataclass
class JoinMessage(MessageBase):
    """
    :param str roomid: Room player is joining
    :param str name: Chosen name of player joining the game

    Player request to broker requesting joining a room
    """

    roomid: RoomId
    name: PlayerName


@dataclass
class MoveMessage(MessageBase):
    """
    :param str playerid: Player making a move
    :param str roomid: Room player is making a move in
    :param dict move: Move to make in the game

    Player sending a move to be made in game
    """

    playerid: PlayerId
    roomid: RoomId
    move: Move


@dataclass
class ListMessage(MessageBase):
    """
    Player requests list of available rooms
    """

    pass


@dataclass
class SpectateMessage(MessageBase):
    """
    :param str roomid: Room to spectate

    Spectator subscribes to state updates for a game
    """

    roomid: RoomId
