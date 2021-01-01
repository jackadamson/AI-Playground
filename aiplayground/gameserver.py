import json
import asyncio
from enum import Enum, auto
from threading import Lock
from time import sleep
from typing import Optional

import socketio
from socketio.exceptions import ConnectionError

from aiplayground.exceptions import (
    GameFull,
    ExistingPlayer,
    GameCompleted,
    IllegalMove,
)
from aiplayground.gameservers import all_games, BaseGameServer
from aiplayground.logging import logger
from aiplayground.messages import (
    CreateRoomMessage,
    RoomCreatedMessage,
    RegisterMessage,
    JoinSuccessMessage,
    JoinFailMessage,
    JoinAcknowledgementMessage,
    GameUpdateMessage,
    PlayerMoveMessage,
    Finish,
)
from aiplayground.settings import settings
from aiplayground.types import GameName, RoomName, RoomId
from aiplayground.utils.atomic import AtomicCounter
from aiplayground.utils.expect import expect


class GameServerState(Enum):
    CONNECTING = auto()
    LOBBY = auto()
    STARTING = auto()
    PLAYING = auto()
    FINISHED = auto()


class GameServer(socketio.AsyncClientNamespace):
    game: BaseGameServer
    game_name: GameName
    name: RoomName
    lock: Lock
    room_id: Optional[RoomId]
    player_counter: AtomicCounter

    def __init__(self, gamename=settings.GAME, name=settings.LOBBY_NAME):
        super().__init__()
        self.game = all_games[gamename]()
        self.game_name = gamename
        self.name = name
        self.player_counter = AtomicCounter()
        self.lock = Lock()

    async def initialize(self):
        self.player_counter.set(0)
        await CreateRoomMessage(name=self.name, game=self.game_name, maxplayers=self.game.max_players).send(sio=self)

    async def on_connect(self):
        with self.lock:
            # TODO: Handle reconnection properly
            logger.info("Connected")
            await self.initialize()

    @expect(JoinAcknowledgementMessage)
    async def on_joinacknowledgement(self, msg: JoinAcknowledgementMessage):
        if self.room_id is None:
            return
        count = self.player_counter.increment_then_get()
        if count == self.game.max_players:
            self.game.start()
            await GameUpdateMessage(
                visibility="broadcast",
                roomid=self.room_id,
                board=self.game.show_board(),
                turn=self.game.turn,
                epoch=self.game.movenumber,
            ).send(sio=self)

    @expect(RoomCreatedMessage)
    async def on_roomcreated(self, msg: RoomCreatedMessage):
        """
        Receives confirmation that a roomcreated was created
        """
        logger.warning("Got created getting lock")
        with self.lock:
            logger.warning("Successfully created room")
            self.room_id = msg.roomid

    @expect(RegisterMessage)
    async def on_register(self, msg: RegisterMessage):
        """
        Player requests to join a lobby
        """
        with self.lock:
            try:
                gamerole = self.game.add_player(msg.playerid)
                # Game is not ready to start
                await JoinSuccessMessage(playerid=msg.playerid, roomid=msg.roomid, gamerole=gamerole).send(sio=self)

            except (GameFull, ExistingPlayer) as e:
                logger.warning(f"Player failed to join with error: {e}")
                await JoinFailMessage(playerid=msg.playerid, roomid=msg.roomid, reason=repr(e)).send(sio=self)

    @expect(PlayerMoveMessage)
    async def on_playermove(self, msg: PlayerMoveMessage):
        """
        Player sends a move
        """
        with self.lock:
            assert self.room_id is not None
            try:
                logger.debug("Starting player move")
                self.game.move(msg.playerid, msg.move)
                logger.debug("Finished player move")
                await GameUpdateMessage(
                    visibility="broadcast",
                    roomid=msg.roomid,
                    board=self.game.show_board(),
                    turn=self.game.turn,
                    epoch=self.game.movenumber,
                    stateid=msg.stateid,
                ).send(sio=self)
            except GameCompleted:
                self.game.playing = False
                await GameUpdateMessage(
                    visibility="broadcast",
                    roomid=msg.roomid,
                    board=self.game.show_board(),
                    turn=None,
                    epoch=self.game.movenumber,
                    stateid=msg.stateid,
                    finish=Finish(
                        normal=True,
                        scores=self.game.score(),
                    ),
                ).send(sio=self)

                if settings.RUN_ONCE:
                    await self.disconnect()
                else:
                    self.game = all_games[self.game_name]()
                    await self.initialize()

            except IllegalMove as e:
                logger.exception(e)
                await GameUpdateMessage(
                    roomid=self.room_id,
                    visibility="broadcast",
                    epoch=self.game.movenumber,
                    board=self.game.show_board(),
                    turn=None,
                    finish=Finish(
                        normal=False,
                        reason=e.details,
                        fault=msg.playerid,
                        scores={p: (-1 if p == msg.playerid else 1) for p in self.game.players},
                    ),
                ).send(sio=self)

    async def on_fail(self, data):
        logger.error("error received:\n" + json.dumps(data, indent=2))


async def main():
    for i in range(settings.CONNECTION_RETRIES):
        try:
            sio = socketio.AsyncClient(reconnection_attempts=settings.CONNECTION_RETRIES)
            server = GameServer()
            sio.register_namespace(server)
            await sio.connect(settings.ASIMOV_URL, headers={"X-ROLE": "gameserver"})
            await sio.wait()
            break
        except ConnectionError:
            print(f"Connection failed (attempt {i + 1} of {settings.CONNECTION_RETRIES}), waiting 2 secs...")
            sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
