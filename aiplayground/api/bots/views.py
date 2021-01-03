from typing import List

from fastapi import APIRouter, Security, HTTPException, status

from aiplayground.api.auth import get_user_id, User
from aiplayground.api.bots.models import Bot
from aiplayground.api.bots.schemas import BotSchema, BotPrivateSchema, CreateBotSchema
from aiplayground.logging import logger
from aiplayground.types import UserId, BotId

bots_router = APIRouter(prefix="/bots", dependencies=[Security(get_user_id)], tags=["Bots"])


@bots_router.get("/all", response_model=List[BotSchema])
def list_bots():
    return Bot.list()


@bots_router.post("/", response_model=BotPrivateSchema)
def create_bot(data: CreateBotSchema, user_id: UserId = Security(get_user_id)):
    user = User.get(user_id)
    bot = Bot.create(name=data.name, description=data.description, user=user)
    return bot


@bots_router.get("/my", response_model=List[BotSchema])
def my_bots(user_id: UserId = Security(get_user_id)):
    user = User.get(user_id)
    return user.bots


@bots_router.get("/my/{bot_id}", response_model=BotPrivateSchema)
def get_my_bot(bot_id: BotId, user_id: UserId = Security(get_user_id)):
    bot = Bot.get(bot_id)
    if bot.user.id != user_id:
        logger.debug(f"Bot owner: {bot.user.id}, accessing user: {user_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accessing bot not owned by you")
    return bot
