from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from aiplayground.types import PlayerId, PlayerName, GameRole


class PlayerSchema(BaseModel):
    id: PlayerId = Field(..., description="Player unique identifier")
    name: PlayerName = Field(..., description="Human readable unique name")
    gamerole: Optional[GameRole] = Field(
        None, description="Role within a particular game, eg. in Tic Tac Toe 'x' or 'o'"
    )
    joined_at: Optional[datetime] = None

    class Config:
        orm_mode = True


all_schemas = [PlayerSchema]
