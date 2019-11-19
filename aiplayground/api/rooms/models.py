from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from flaskplusplus import Base
from flaskplusplus.database import JSONColumn


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
    board = Column(JSONColumn, nullable=True)
    turn = Column(Integer, nullable=True)
