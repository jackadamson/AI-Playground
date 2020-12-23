from os import environ

environ["BROKER"] = "true"
import socketio
from fastapi import FastAPI
from aiplayground.broker import sio
from aiplayground.api import rooms_router, players_router, auth_router

tags_metadata = [
    {"name": "Players", "description": "Players information"},
    {"name": "Rooms", "description": "Game rooms that are running"},
    {"name": "Auth", "description": "Authentication"},
]
api_app = FastAPI(
    title="AI Playground",
    description="Tournament server for AI boardgames",
    openapi_tags=tags_metadata,
)
api_app.include_router(rooms_router)
api_app.include_router(players_router)
api_app.include_router(auth_router)

app = socketio.ASGIApp(socketio_server=sio, socketio_path="socket.io", other_asgi_app=api_app)
