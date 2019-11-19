from flaskplusplus import Base
from flaskplusplus.database import db
from asimovsplayground.api.players.schemas import player_schema
from datetime import datetime


class Player(Base):
    __tablename__ = "players"
    name = db.Column(db.String, nullable=False)
    sid = db.Column(db.String, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.now)
    # updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    joined = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", backref="players")
    room_id = db.Column(db.String, db.ForeignKey("rooms.id"), nullable=False)
    room = db.relationship("Room", backref="players")
    schema = player_schema
