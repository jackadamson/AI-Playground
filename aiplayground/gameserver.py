import socketio
import json
from typing import Optional
from aiplayground.settings import GAME, LOBBY_NAME, ASIMOV_URL, RUN_ONCE
from aiplayground.gameservers import all_games, BaseGame
from aiplayground.exceptions import (
    GameFull,
    ExistingPlayer,
    GameCompleted,
    AsimovServerError,
)
from flaskplusplus.logging import logger


class GameServer(socketio.ClientNamespace):
    game: BaseGame
    game_name: str
    name: str
    server_id: Optional[str]

    def __init__(self, gamename=GAME, name=LOBBY_NAME):
        super().__init__()
        self.game = all_games[gamename]()
        self.game_name = gamename
        self.name = name

    def on_connect(self):
        logger.info("Connected")
        self.emit(
            "createroom",
            {
                "name": self.name,
                "game": self.game_name,
                "maxplayers": self.game.max_players,
            },
        )

    def on_roomcreated(self, data):
        """
        Receives confirmation that a roomcreated was created
        :property roomid
        """
        # TODO: Add validation of input against schema
        logger.info("Successfully created room")
        logger.debug(json.dumps(data, indent=2))
        self.server_id = data["roomid"]

    def on_register(self, data):
        """
        Receives request from player to join lobby
        :property roomid
        :property playerid
        """
        # TODO: Add validation of input against schema
        logger.info("Received player registration")
        logger.debug(json.dumps(data, indent=2))
        try:
            self.game.add_player(data["playerid"])
            board = self.game.show_board()
            self.emit(
                "joinsuccess", {"playerid": data["playerid"], "roomid": data["roomid"]}
            )
            if board is not None:
                self.emit(
                    "gameupdate",
                    {
                        "visibility": "broadcast",
                        "roomid": data["roomid"],
                        "board": self.game.show_board(),
                        "turn": self.game.players[self.game.turn],
                        "epoch": self.game.movenumber,
                    },
                )
        except (GameFull, ExistingPlayer) as e:
            logger.warning(f"Player failed to join with error: {e}")
            self.emit(
                "joinfail",
                {
                    "playerid": data["playerid"],
                    "roomid": data["roomid"],
                    "reason": repr(e),
                },
            )

    def on_playermove(self, data):
        """
        Player sends a move
        :property roomid
        :property playerid
        :property move
        :property stateid
        """
        # TODO: Add validation of input against schema
        # TODO: Handle exceptions that can be raised
        logger.info(f"Player made move:\n{json.dumps(data, indent=2)}")
        try:
            self.game.move(data["playerid"], data["move"])
            self.emit(
                "gameupdate",
                {
                    "visibility": "broadcast",
                    "roomid": data["roomid"],
                    "board": self.game.show_board(),
                    "turn": self.game.players[self.game.turn],
                    "epoch": self.game.movenumber,
                    "stateid": data["stateid"],
                },
            )
        except GameCompleted:
            self.game.playing = False
            self.emit(
                "gameupdate",
                {
                    "visibility": "broadcast",
                    "roomid": data["roomid"],
                    "board": self.game.show_board(),
                    "turn": None,
                    "epoch": self.game.movenumber,
                    "stateid": data["stateid"],
                },
            )
            self.emit(
                "finish",
                {"normal": True, "scores": self.game.score(), "roomid": self.server_id},
            )
            if RUN_ONCE:
                sio.disconnect()
            else:
                self.game = all_games[self.game_name]()
                self.on_connect()

        except AsimovServerError as e:
            logger.error(e)

    def on_fail(self, data):
        logger.error("error received:\n" + json.dumps(data, indent=2))


if __name__ == "__main__":
    sio = socketio.Client()
    server = GameServer()
    sio.register_namespace(server)
    sio.connect(ASIMOV_URL)
