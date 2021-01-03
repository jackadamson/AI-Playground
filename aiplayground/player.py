import asyncio
import json
import time
from time import sleep
from typing import Optional, Type, Dict

import socketio
from socketio.exceptions import ConnectionError

from aiplayground.logging import logger
from aiplayground.messages import (
    GamestateMessage,
    JoinMessage,
    JoinedMessage,
    ListMessage,
    MoveMessage,
    Finish,
)
from aiplayground.players import all_players, BasePlayer
from aiplayground.settings import settings
from aiplayground.types import PlayerId, RoomId, RoomName, GameName, PlayerName
from aiplayground.utils.expect import expect


class PlayerClient(socketio.AsyncClientNamespace):
    player_id: Optional[PlayerId] = None
    room_id: Optional[RoomId] = None
    game_name: Optional[GameName] = None
    room_name: Optional[RoomName] = None
    player: Optional[BasePlayer] = None
    player_name: PlayerName

    def __init__(self, player_name: PlayerName = settings.PLAYER_NAME):
        super().__init__()
        self.player_name = player_name

    async def on_connect(self):
        # TODO: Handle reconnection properly
        logger.info("Connected to broker")
        self.room_id = None
        self.player_id = None
        self.game_name = None
        self.room_name = None
        self.player = None
        await ListMessage().send(sio=self, callback=self.rooms_callback)

    async def rooms_callback(self, rooms: Dict[str, Dict]):
        if self.room_id is not None:
            logger.warning("Received rooms callback after joining a room")
            return
        logger.debug(f"Games available: {rooms}")
        lobbies = [
            (k, v["game"], v["name"]) for k, v in rooms.items() if v["status"] == "lobby" and v["game"] in all_players
        ]
        if not lobbies:
            logger.warning("No verified lobbies found, sleeping for 2s")
            time.sleep(2)
            await ListMessage().send(sio=self, callback=self.rooms_callback)
            return
        self.room_id, self.game_name, self.room_name = lobbies[0]
        await JoinMessage(roomid=self.room_id, name=self.player_name).send(sio=self)

    @expect(JoinedMessage)
    async def on_joined(self, msg: JoinedMessage):
        if msg.broadcast:
            return
        assert self.game_name is not None
        self.player_id = msg.playerid
        self.room_id = msg.roomid
        logger.info(f"Joined Game: {self.room_name}({self.game_name})")
        player: Type[BasePlayer] = all_players[self.game_name]
        self.player = player(gamerole=msg.gamerole, player_id=msg.playerid)

    @expect(GamestateMessage)
    async def on_gamestate(self, msg: GamestateMessage):
        if msg.finish is not None:
            await self.finished(msg.finish)
            return
        if msg.roomid != self.room_id:
            return
        assert self.player is not None
        assert self.room_id is not None
        assert self.player_id is not None
        if msg.roomid != self.room_id:
            return
        move = self.player.update(board=msg.board, turn=msg.turn)
        if move is not None:
            await MoveMessage(roomid=self.room_id, playerid=self.player_id, move=move).send(sio=self)

    async def finished(self, finish: Finish):
        assert self.player_id is not None
        assert finish.scores is not None
        if finish.normal:
            logger.debug("Game finished normally")
            score = finish.scores[self.player_id]
            if score > 0:
                logger.info("We won :)")
            elif score == 0:
                logger.info("We tied :|")
            else:
                logger.info("We lost :(")

            if settings.RUN_ONCE:
                await self.disconnect()
            else:
                await self.on_connect()
        else:
            logger.error(f"Game finished with error: {finish.reason}")
            if finish.fault == self.player_id:
                logger.error("AND IT WAS ALL OUR FAULT D:")
                if settings.LEEROY_JENKINS:
                    logger.error("But YOLO I'll try again")
                    await self.on_connect()
                else:
                    await self.disconnect()

    async def on_fail(self, data):
        logger.error(f"Received fail:\n{json.dumps(data, indent=2)}")

    async def on_disconnect(self):
        logger.error("Disconnected!")


async def main():
    for i in range(settings.CONNECTION_RETRIES):
        try:
            if settings.API_KEY is not None:
                headers = {"X-API-KEY": settings.API_KEY}
            else:
                headers = {}
            sio = socketio.AsyncClient(reconnection_attempts=settings.CONNECTION_RETRIES)
            player_client = PlayerClient()
            sio.register_namespace(player_client)
            await sio.connect(settings.ASIMOV_URL, headers=headers)
            await sio.wait()
            break
        except ConnectionError:
            logger.warning(f"Connection failed (attempt {i + 1} of {settings.CONNECTION_RETRIES}), waiting 2 secs...")
            sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
