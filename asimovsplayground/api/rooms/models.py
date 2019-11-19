from flaskplusplus import Base
from flaskplusplus.database import db, JSONColumn
from datetime import datetime


class Room(Base):
    __tablename__ = "rooms"
    name = db.Column(db.String, nullable=False)
    game = db.Column(db.String, nullable=False)
    maxplayers = db.Column(db.Integer, nullable=False)
    sid = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default="lobby")
    board = db.Column(JSONColumn, default={})
    turn = db.Column(db.Integer, nullable=True)
    normal_finish = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    # updated_at = db.Column(db.DateTime, onupdate=datetime.now)


class GameState(Base):
    timestamp = db.Column(db.DateTime, default=datetime.now)
    player_id = db.Column(db.String, db.ForeignKey("players.id"), nullable=True)
    player = db.relationship("Player", backref="moves")

    room_id = db.Column(db.String, db.ForeignKey("rooms.id"), nullable=False)
    room = db.relationship("Room", backref="states")

    epoch = db.Column(db.Integer)
    move = db.Column(JSONColumn, nullable=True)
    board = db.Column(JSONColumn, nullable=True)
    turn = db.Column(db.Integer, nullable=True)
