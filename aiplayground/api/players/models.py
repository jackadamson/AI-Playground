from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from flaskplusplus import Base
from aiplayground.api.players.schemas import player_schema
from datetime import datetime


class Player(Base):
    __tablename__ = "players"
    name = Column(String, nullable=False)
    sid = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.now)
    # updated_at = Column(DateTime, onupdate=datetime.now)
    game_role = Column(String, nullable=True)
    joined = Column(Boolean, default=False, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="players")
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room", backref="players")
    schema = player_schema
