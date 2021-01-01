from os import environ

environ["BROKER"] = "true"
import socketio
from fastapi import FastAPI
from redorm import red
from aiplayground.settings import settings
from aiplayground.broker import sio
from aiplayground.api import all_routers, initialize_all
from aiplayground.logging import logger

tags_metadata = [
    {"name": "Players", "description": "Players information"},
    {"name": "Rooms", "description": "Game rooms that are running"},
    {"name": "Auth", "description": "Authentication"},
]
api_app = FastAPI(
    title="AI Playground",
    description="Tournament server for AI boardgames",
    openapi_tags=tags_metadata,
    root_path="/api/v1",
)

for router in all_routers:
    api_app.include_router(router)

red.bind(settings.REDORM_URL)
if settings.EPHEMERAL:
    logger.info("Flushing Database")
    red.client.flushall()
initialize_all()

app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=api_app)
