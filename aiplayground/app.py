from os import environ

environ["BROKER"] = "true"
import socketio
from fastapi import FastAPI
from redorm import red
from aiplayground.settings import settings
from aiplayground.broker import sio
from aiplayground.api import rooms_router, players_router, auth_router, initialize_all

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
api_app.include_router(rooms_router)
api_app.include_router(players_router)
api_app.include_router(auth_router)

red.bind(settings.REDORM_URL)
initialize_all()

app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=api_app)
