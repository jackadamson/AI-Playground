from typing import Optional, List

from pydantic import BaseModel, Field


class AuthSchema(BaseModel):
    success: bool
    payload: Optional[str] = Field(None, description="Bearer token")
    message: Optional[str] = Field(None, description="Error message")


class RoleSchema(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    username: str
    email: str
    roles: List[RoleSchema]

    class Config:
        orm_mode = True


class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
