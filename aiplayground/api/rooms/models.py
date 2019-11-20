from typing import Optional, List
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from flaskplusplus import Base
from flaskplusplus.database import JSONColumn
import json
from aiplayground.types import (
    PlayerId,
    RoomId,
    StateId,
    RoomName,
    GameName,
    Board,
    Move,
    GameServerSID,
    BroadcastSID,
)
from aiplayground.api.players import Player


class Room(Base):
    __tablename__ = "rooms"
    id: RoomId
    name: RoomName = Column(String, nullable=False)
    game: GameName = Column(String, nullable=False)
    maxplayers = Column(Integer, nullable=False)
    server_sid: GameServerSID = Column(String, nullable=False)
    status = Column(String, default="lobby")
    board: Board = Column(JSONColumn, default={})
    turn = Column(String, ForeignKey("players.id"), nullable=True)
    normal_finish = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    players: List[Player] = relationship("Player", foreign_keys=[Player.room_id])

    @property
    def broadcast_sid(self):
        return BroadcastSID(f"room-{self.id}")


class GameState(Base):
    __tablename__ = "gamestates"
    id: StateId
    timestamp = Column(DateTime, default=datetime.now)
    player_id: PlayerId = Column(String, ForeignKey("players.id"), nullable=True)
    player = relationship("Player", backref="moves", foreign_keys=[player_id])

    room_id: RoomId = Column(String, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room", backref="states")

    epoch = Column(Integer)
    move: Move = Column(JSONColumn, nullable=True)
    boardstate_id = Column(String, ForeignKey("boardstates.id"), nullable=True)
    board = relationship("BoardState", lazy="joined")
    turn: PlayerId = Column(String, ForeignKey("players.id"), nullable=True)

    def __init__(self, board=None, **kwargs):
        boardstate_id = BoardState.id_from_state(board)
        # noinspection PyArgumentList
        Base.__init__(self, boardstate_id=boardstate_id, **kwargs)

    def update(self: "GameState", board=None, **kwargs):
        if board is not None:
            boardstate_id = BoardState.id_from_state(board)
            return super().update(self, boardstate_id=boardstate_id, **kwargs)
        else:
            return super().update(self, commit=True, **kwargs)


class BoardState(Base):
    __tablename__ = "boardstates"
    state: Board = Column(JSONColumn, nullable=False, unique=True, index=True)

    @classmethod
    def id_from_state(cls, state: Optional[dict]) -> Optional[str]:
        if state is None:
            return None
        try:
            return cls.get(state=state).id
        except NoResultFound:
            return cls.create(state=state).id
