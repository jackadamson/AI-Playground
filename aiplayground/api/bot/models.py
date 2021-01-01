from dataclasses import dataclass, field
from typing import Optional
from secrets import token_urlsafe
from functools import partial

from aiplayground.api.auth import User
from aiplayground.types import BotId
from redorm import RedormBase, many_to_one


@dataclass
class Bot(RedormBase):
    """
    A bot owned by a user
    :field name: Unique name of bot, seen in scoreboard
    :field description: Human readable description
    :field user User that owns the bot
    """

    id: BotId = field(metadata={"unique": True})
    name: str = field(metadata={"unique": True})
    description: Optional[str] = field(default=None)
    api_key: str = field(default_factory=partial(token_urlsafe, 32))
    user = many_to_one(User, backref="bots")
