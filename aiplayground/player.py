from typing import Optional, Type
from time import sleep
import socketio
from socketio.exceptions import ConnectionError
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
    LEEROY_JENKINS,
)
from aiplayground.players import all_players, BasePlayer
from aiplayground.utils.expect import expect
from aiplayground.messages import (
    GamestateMessage,
    JoinMessage,
    JoinedMessage,
    FinishMessage,
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
        logger.info("Connected to broker")
        self.room_id = None
        self.player_id = None
        self.game_name = None
        self.lobby_name = None
        self.player = None
        ListMessage().send(sio=self)

    @expect(RoomsMessage)
    def on_rooms(self, msg: RoomsMessage):
        if self.room_id is not None:
            return
        lobbies = [
            (k, v["game"], v["name"])
            for k, v in msg.rooms.items()
            if v["status"] == "lobby" and v["game"] in all_players
        ]
        if not lobbies:
            logger.warning("No active lobbies found, sleeping for 2s")
            time.sleep(2)
            ListMessage().send(sio=self)
            return
        self.room_id, self.game_name, self.lobby_name = lobbies[0]
        JoinMessage(roomid=self.room_id, name="Some Player").send(sio=self)

    @expect(JoinedMessage)
    def on_joined(self, msg: JoinedMessage):
        self.player_id = msg.playerid
        self.room_id = msg.roomid
        logger.info(f"Joined Game: {self.lobby_name}({self.game_name})")
        player: Type[BasePlayer] = all_players[self.game_name]
        self.player = player(gamerole=msg.gamerole, player_id=msg.playerid)

    @expect(GamestateMessage)
    def on_gamestate(self, msg: GamestateMessage):
        move = self.player.update(board=msg.board, turn=msg.turn)
        if move is not None:
            MoveMessage(roomid=self.room_id, playerid=self.player_id, move=move).send(
                sio=self
            )

    @expect(FinishMessage)
    def on_finish(self, msg: FinishMessage):
        if msg.normal:
            logger.debug("Game finished normally")
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
            if msg.fault == self.player_id:
                logger.error("AND IT WAS ALL OUR FAULT D:")
                if LEEROY_JENKINS:
                    logger.error("But YOLO I'll try again")
                    self.on_connect()
                else:
                    self.disconnect()

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
                f"Connection failed (attempt {i + 1} of {CONNECTION_RETRIES}), waiting 2 secs..."
            )
            sleep(2)


if __name__ == "__main__":
    main()
