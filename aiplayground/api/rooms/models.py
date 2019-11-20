from typing import Optional
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from flaskplusplus import Base
from flaskplusplus.database import JSONColumn
import json


class Room(Base):
    __tablename__ = "rooms"
    name = Column(String, nullable=False)
    game = Column(String, nullable=False)
    maxplayers = Column(Integer, nullable=False)
    sid = Column(String, nullable=False)
    status = Column(String, default="lobby")
    board = Column(JSONColumn, default={})
    turn = Column(Integer, nullable=True)
    normal_finish = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    players = relationship("Player")
    # updated_at = Column(DateTime, onupdate=datetime.now)


class GameState(Base):
    __tablename__ = "gamestates"
    timestamp = Column(DateTime, default=datetime.now)
    player_id = Column(String, ForeignKey("players.id"), nullable=True)
    player = relationship("Player", backref="moves")

    room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room", backref="states")

    epoch = Column(Integer)
    move = Column(JSONColumn, nullable=True)
    boardstate_id = Column(String, ForeignKey("boardstates.id"), nullable=True)
    board = relationship("BoardState", lazy="joined")
    turn = Column(Integer, nullable=True)

    def __init__(self, board=None, **kwargs):
        boardstate_id = BoardState.id_from_state(board)
        Base.__init__(self, boardstate_id=boardstate_id, **kwargs)

    def update(self: "GameState", board=None, **kwargs):
        if board is not None:
            boardstate_id = BoardState.id_from_state(board)
            return super().update(self, boardstate_id=boardstate_id, **kwargs)
        else:
            return super().update(self, commit=True, **kwargs)


class BoardState(Base):
    __tablename__ = "boardstates"
    state = Column(JSONColumn, nullable=False, unique=True, index=True)

    @classmethod
    def id_from_state(cls, state: Optional[dict]) -> Optional[str]:
        if state is None:
            return None
        try:
            return cls.get(state=state).id
        except NoResultFound:
            print(f"Creating state:\n{json.dumps(state, indent=2)}")
            return cls.create(state=state).id
