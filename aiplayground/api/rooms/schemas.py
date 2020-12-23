from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from aiplayground.api.players import PlayerSchema
from aiplayground.types import PlayerId, RoomId, StateId, RoomName, Board, Move, GameName, GameStatus


class GameStateSchema(BaseModel):
    id: StateId = Field(..., description="Game state unique identifier")
    timestamp: datetime
    player: Optional[PlayerId] = Field(
        ..., description="Identifies the player who made the move directly leading to the state"
    )
    epoch: int = Field(..., description="The index of the state within the span of the game")
    move: Optional[Move] = Field(None, description="The move which lead to the state")
    board: Optional[Board] = Field(..., description="Game state")
    turn: PlayerId = Field(None, description="Id of next player to play")

    class Config:
        orm_mode = True


class RoomSchema(BaseModel):
    id: RoomId = Field(..., description="Game state unique identifier")
    name: RoomName = Field(..., description="Name of the game room", example="Chess Lobby 1")
    game: GameName = Field(..., description="Game played in room", example="chess")
    status: GameStatus = Field(..., description="Current state of hello fresh")
    board: Board = Field(..., description="Current room game board")
    created_at: datetime
    players: List[PlayerSchema]
    maxplayers: int
    states: List[GameStateSchema]

    class Config:
        orm_mode = True


class RoomSchemaSummary(BaseModel):
    id: RoomId = Field(..., description="Game state unique identifier")
    name: RoomName = Field(..., description="Name of the game room", example="Chess Lobby 1")
    game: GameName = Field(..., description="Game played in room", example="chess")
    status: GameStatus = Field(..., description="Current state of hello fresh")
    board: Optional[Board] = Field(..., description="Current room game board")
    created_at: datetime
    players: List[PlayerSchema]
    maxplayers: int

    class Config:
        orm_mode = True


all_schemas = [GameStateSchema, RoomSchema, RoomSchemaSummary]
