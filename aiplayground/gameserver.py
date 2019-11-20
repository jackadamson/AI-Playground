import socketio
from socketio.exceptions import ConnectionError
import json
from time import sleep
from typing import Optional
from enum import Enum, auto
from aiplayground.utils.atomic import AtomicCounter
from aiplayground.settings import (
    GAME,
    LOBBY_NAME,
    ASIMOV_URL,
    RUN_ONCE,
    CONNECTION_RETRIES,
)
from aiplayground.gameservers import all_games, BaseGame
from aiplayground.exceptions import (
    GameFull,
    ExistingPlayer,
    GameCompleted,
    AsimovServerError,
)
from aiplayground.utils.clients import expect
from aiplayground.messages import (
    CreateRoomMessage,
    RoomCreatedMessage,
    RegisterMessage,
    JoinSuccessMessage,
    JoinFailMessage,
    GameUpdateMessage,
    PlayerMoveMessage,
    FinishMessage,
)
from flaskplusplus.logging import logger


class GameServerState(Enum):
    CONNECTING = auto()
    LOBBY = auto()
    STARTING = auto()
    PLAYING = auto()
    FINISHED = auto()


class GameServer(socketio.ClientNamespace):
    game: BaseGame
    game_name: str
    name: str
    room_id: Optional[str]
    player_counter: AtomicCounter

    def __init__(self, gamename=GAME, name=LOBBY_NAME):
        super().__init__()
        self.game = all_games[gamename]()
        self.game_name = gamename
        self.name = name
        self.player_counter = AtomicCounter()

    def on_connect(self):
        logger.info("Connected")
        self.player_counter.set(0)
        CreateRoomMessage(
            name=self.name, game=self.game_name, maxplayers=self.game.max_players
        ).send(sio=self)

    def player_added(self):
        count = self.player_counter.increment_then_get()
        if count == self.game.max_players:
            GameUpdateMessage(
                visibility="broadcast",
                roomid=self.room_id,
                board=self.game.show_board(),
                turn=self.game.players[self.game.turn],
                epoch=self.game.movenumber,
            ).send(sio=self)

    @expect(RoomCreatedMessage)
    def on_roomcreated(self, msg: RoomCreatedMessage):
        """
        Receives confirmation that a roomcreated was created
        """
        logger.info("Successfully created room")
        self.room_id = msg.roomid

    @expect(RegisterMessage)
    def on_register(self, msg: RegisterMessage):
        """
        Player requests to join a lobby
        """
        try:
            self.game.add_player(msg.playerid)
            # Game is not ready to start
            JoinSuccessMessage(playerid=msg.playerid, roomid=msg.roomid).send(
                sio=self, callback=self.player_added
            )

        except (GameFull, ExistingPlayer) as e:
            logger.warning(f"Player failed to join with error: {e}")
            JoinFailMessage(
                playerid=msg.playerid, roomid=msg.roomid, reason=repr(e)
            ).send(sio=self)

    @expect(PlayerMoveMessage)
    def on_playermove(self, msg: PlayerMoveMessage):
        """
        Player sends a move
        """
        # TODO: Handle exceptions that can be raised (eg. Illegal move)
        try:
            self.game.move(msg.playerid, msg.move)
            GameUpdateMessage(
                visibility="broadcast",
                roomid=msg.roomid,
                board=self.game.show_board(),
                turn=self.game.players[self.game.turn],
                epoch=self.game.movenumber,
                stateid=msg.stateid,
            ).send(sio=self)
        except GameCompleted:
            self.game.playing = False
            GameUpdateMessage(
                visibility="broadcast",
                roomid=msg.roomid,
                board=self.game.show_board(),
                turn=None,
                epoch=self.game.movenumber,
                stateid=msg.stateid,
            ).send(sio=self)
            FinishMessage(
                normal=True, scores=self.game.score(), roomid=self.room_id
            ).send(sio=self)
            if RUN_ONCE:
                sio.disconnect()
            else:
                self.game = all_games[self.game_name]()
                self.on_connect()

        except AsimovServerError as e:
            logger.error(e)

    def on_fail(self, data):
        logger.error("error received:\n" + json.dumps(data, indent=2))


def main():
    for i in range(CONNECTION_RETRIES):
        try:
            sio = socketio.Client(reconnection_attempts=CONNECTION_RETRIES)
            server = GameServer()
            sio.register_namespace(server)
            sio.connect(ASIMOV_URL)
            sio.wait()
            break
        except ConnectionError:
            print(
                f"Connection failed (attempt {i+1} of {CONNECTION_RETRIES}), waiting 5 secs..."
            )
            sleep(5)


if __name__ == "__main__":
    main()
