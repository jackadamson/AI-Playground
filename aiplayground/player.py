from typing import Optional
import socketio
import random
import json
import time
import requests
from flaskplusplus.logging import logger
from aiplayground.settings import ASIMOV_URL, EMAIL, PASSWORD, RUN_ONCE


class PlayerClient(socketio.ClientNamespace):
    player_id: Optional[str] = None
    server_id: Optional[str] = None
    game_name: Optional[str] = None
    lobby_name: Optional[str] = None

    def __init__(self, namespace=None):
        super().__init__(namespace=namespace)

    def on_connect(self):
        logger.info("I'm connected!")
        self.server_id = None
        self.player_id = None
        self.game_name = None
        self.lobby_name = None
        self.emit("list")

    def on_rooms(self, data: dict):
        logger.info(f"Received list of rooms:\n{json.dumps(data, indent=2)}")
        if self.server_id is not None:
            return
        lobbies = [
            (k, v["game"], v["name"]) for k, v in data.items() if v["status"] == "lobby"
        ]
        if not lobbies:
            logger.info("No active lobbies found, sleeping for 10s")
            time.sleep(10)
            self.emit("list")
            return
        self.server_id, self.game_name, self.lobby_name = lobbies[0]
        self.emit("join", {"roomid": self.server_id, "name": "Some Player"})

    def on_joined(self, data):
        logger.info(f"I received a joined message:\n{json.dumps(data, indent=2)}")
        self.player_id = data["playerid"]

    def on_gamestate(self, data):
        logger.info(f"I received a board message:\n{json.dumps(data['board'], indent=2)}")
        if data["turn"] == self.player_id:
            logger.info("It's my move!")
            move = random.choice(["scissors", "paper", "rock"])
            self.emit(
                "move", {"roomid": self.server_id, "playerid": self.player_id, "move": {"move": move}}
            )

    def on_finished(self, data):
        if data["normal"]:
            logger.info("Game finished normally")
            score = data["scores"][self.player_id]
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
            logger.info(f"Game finished with error: {data['reason']}")

    def on_fail(self, data):
        logger.info(f"Received fail:\n{json.dumps(data, indent=2)}")

    def on_disconnect(self):
        logger.info("I'm disconnected!")


def main():
    if EMAIL and PASSWORD:
        r = requests.post(ASIMOV_URL + "/auth/login", auth=(EMAIL, PASSWORD))
        token = r.json()["payload"]
        headers = {"Authorization": f"Bearer {token}"}
    else:
        headers = {}
    sio = socketio.Client()
    player_client = PlayerClient()
    sio.register_namespace(player_client)
    sio.connect(ASIMOV_URL, headers=headers)


if __name__ == "__main__":
    main()
