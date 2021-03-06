from typing import List

from fastapi import APIRouter, HTTPException, Security

from aiplayground.api.auth import get_claims
from redorm import InstanceNotFound

from aiplayground.api.rooms.models import Room
from aiplayground.api.rooms.schemas import RoomSchema, RoomSchemaSummary
from aiplayground.logging import logger

rooms_router = APIRouter(prefix="/rooms", tags=["Rooms"], dependencies=[Security(get_claims)])


@rooms_router.get("/", response_model=List[RoomSchemaSummary])
def list_rooms():
    return Room.list(private=False)


@rooms_router.get("/{room_id}", response_model=RoomSchema)
def get_room(room_id):
    try:
        room = Room.get(room_id)
        logger.debug(room)
        return room
    except InstanceNotFound:
        raise HTTPException(status_code=404, detail="Could not find lobby")
