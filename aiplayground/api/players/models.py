from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from flaskplusplus import Base

from aiplayground.types import PlayerName, PlayerId, PlayerSID, GameRole, RoomId
from aiplayground.api.players.schemas import player_schema


class Player(Base):
    __tablename__ = "players"
    id: PlayerId
    name: PlayerName = Column(String, nullable=False)
    sid: PlayerSID = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.now)
    game_role: GameRole = Column(String, nullable=True)
    joined = Column(Boolean, default=False, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="players")
    room_id: RoomId = Column(String, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room", foreign_keys=[room_id])
    schema = player_schema
