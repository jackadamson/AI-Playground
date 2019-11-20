from typing import Optional
from time import sleep
import socketio
from socketio.exceptions import ConnectionError
import random
import json
import time
import requests
from flaskplusplus.logging import logger
from aiplayground.settings import (
    ASIMOV_URL,
    EMAIL,
    PASSWORD,
    RUN_ONCE,
    CONNECTION_RETRIES,
)
from aiplayground.players import all_players, BasePlayer
from aiplayground.utils.clients import expect
from aiplayground.messages import (
    GamestateMessage,
    JoinMessage,
    JoinedMessage,
    FinishedMessage,
    ListMessage,
    RoomsMessage,
    MoveMessage,
)


class PlayerClient(socketio.ClientNamespace):
    player_id: Optional[str] = None
    room_id: Optional[str] = None
    game_name: Optional[str] = None
    lobby_name: Optional[str] = None
    player: Optional[BasePlayer] = None

    def __init__(self, namespace=None):
        super().__init__(namespace=namespace)

    def on_connect(self):
        # TODO: Handle reconnection properly
        logger.info("I'm connected!")
        self.room_id = None
        self.player_id = None
        self.game_name = None
        self.lobby_name = None
        self.player = None
        self.emit("list")

    @expect(RoomsMessage)
    def on_rooms(self, msg: RoomsMessage):
        if self.room_id is not None:
            return
        lobbies = [
            (k, v["game"], v["name"])
            for k, v in msg.rooms.items()
            if v["status"] == "lobby"
        ]
        if not lobbies:
            logger.warning("No active lobbies found, sleeping for 10s")
            time.sleep(10)
            ListMessage().send(sio=self)
            return
        self.room_id, self.game_name, self.lobby_name = lobbies[0]
        JoinMessage(roomid=self.room_id, name="Some Player").send(sio=self)

    @expect(JoinedMessage)
    def on_joined(self, msg: JoinedMessage):
        self.player_id = msg.playerid
        self.room_id = msg.roomid
        self.player = all_players[self.game_name](gamerole=msg.gamerole)

    @expect(GamestateMessage)
    def on_gamestate(self, msg: GamestateMessage):
        if msg.turn == self.player_id and msg.turn is not None:
            logger.debug("Our move to play")
            move = random.choice(["scissors", "paper", "rock"])
            MoveMessage(
                roomid=self.room_id, playerid=self.player_id, move={"move": move}
            ).send(sio=self)

    @expect(FinishedMessage)
    def on_finished(self, msg: FinishedMessage):
        if msg.normal:
            logger.info("Game finished normally")
            score = msg.scores[self.player_id]
            if score > 0:
                logger.info("We won :)")
            elif score == 0:
                logger.info("We tied :|")
            else:
                logger.info("We lost :(")

            if RUN_ONCE:
                self.disconnect()
            else:
                self.on_connect()
        else:
            logger.error(f"Game finished with error: {msg.reason}")

    def on_fail(self, data):
        logger.error(f"Received fail:\n{json.dumps(data, indent=2)}")

    def on_disconnect(self):
        logger.error("Disconnected!")


def main():
    for i in range(CONNECTION_RETRIES):
        try:
            if EMAIL and PASSWORD:
                r = requests.post(ASIMOV_URL + "/auth/login", auth=(EMAIL, PASSWORD))
                token = r.json()["payload"]
                headers = {"Authorization": f"Bearer {token}"}
            else:
                headers = {}
            sio = socketio.Client(reconnection_attempts=CONNECTION_RETRIES)
            player_client = PlayerClient()
            sio.register_namespace(player_client)
            sio.connect(ASIMOV_URL, headers=headers)
            sio.wait()
            break
        except ConnectionError:
            logger.warning(
                f"Connection failed (attempt {i + 1} of {CONNECTION_RETRIES}), waiting 5 secs..."
            )
            sleep(5)


if __name__ == "__main__":
    main()
