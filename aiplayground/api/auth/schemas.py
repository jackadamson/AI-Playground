from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from aiplayground.types import UserId


class AuthSchema(BaseModel):
    success: bool
    access_token: Optional[str] = Field(None, description="Bearer token")
    message: Optional[str] = Field(None, description="Error message")


class RoleSchema(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    id: UserId
    username: str
    email: str
    roles: List[RoleSchema]

    class Config:
        orm_mode = True


class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str


class TokenType(str, Enum):
    refresh = "refresh"
    access = "access"


class TokenSchema(BaseModel):
    sub: str
    iat: datetime = Field(default_factory=datetime.utcnow)
    exp: Optional[datetime] = None
    scopes: List[str] = []
    type: TokenType = TokenType.access
