from typing import Optional

from pydantic import BaseModel

from aiplayground.types import BotId


class UserPartialSchema(BaseModel):
    username: str

    class Config:
        orm_mode = True


class BotSchema(BaseModel):
    id: BotId
    name: str
    description: Optional[str] = None
    user: UserPartialSchema

    class Config:
        orm_mode = True


class BotPrivateSchema(BaseModel):
    id: BotId
    name: str
    description: Optional[str] = None
    user: UserPartialSchema
    api_key: str

    class Config:
        orm_mode = True


class CreateBotSchema(BaseModel):
    name: str
    description: Optional[str] = None
