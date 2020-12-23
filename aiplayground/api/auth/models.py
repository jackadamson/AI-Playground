from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Type, List

from jose import jwt
from passlib.context import CryptContext
from redorm import RedormBase, many_to_many

from aiplayground.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class Role(RedormBase):
    """
    A role in the RBAC system
    :field default: Added to new users by default
    :field name: Actual unique name of role
    :field description: Human readable role description
    :field users: All user roles that are tied to the user
    """

    name: str = field(metadata={"unique": True})
    description: str
    default: bool = field(default=False)
    users = many_to_many("User", backref="roles")


@dataclass
class User(RedormBase):
    username: str = field(metadata={"unique": True})
    email: str = field(metadata={"unique": True})
    password: Optional[str]
    reset_token: Optional[str] = field(metadata={"unique": True})
    verified: bool = field(default=not settings.USER_APPROVAL_REQUIRED)
    guest: bool = field(default=False)
    roles = many_to_many(Role, backref="users")

    @classmethod
    def create(cls: Type["User"], password=None, **kwargs) -> "User":
        if password is not None:
            password = cls.create_password(password)
            newuser = super().create(password=password, **kwargs)
        else:
            newuser = super().create(**kwargs)
        assert isinstance(newuser, cls)
        return newuser

    @classmethod
    def create_password(cls, password: str) -> str:
        """
        Set's a users password to the salted and hashed value
        :param password:
        :return:
        """
        return pwd_context.hash(password)

    def check_password(self, password) -> bool:
        """
        Salt, hash and compare provided password to stored
        :param password:
        :return:
        """
        return pwd_context.verify(password, self.password)

    def create_token(
        self,
        extra_scopes: Optional[List[str]] = None,
        expires_delta: Optional[timedelta] = None,
        refresh: bool = False,
    ):
        """
        Create JWT for access through browser
        :param extra_scopes: List of scopes in addition to user roles
        :param expires_delta:
        :param refresh: Whether to create a refresh token (or an access token)
        :return:
        """
        if extra_scopes is None:
            extra_scopes = []
        issued_at = datetime.utcnow()
        expire = issued_at + expires_delta if expires_delta is not None else None
        roles = [role.name for role in self.roles]
        scopes = roles + extra_scopes if not refresh else []
        claims = {"sub": self.id, "scopes": scopes, "iat": issued_at, "type": "refresh" if refresh else "access"}
        if expire is not None:
            claims["exp"] = expire
        return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)
