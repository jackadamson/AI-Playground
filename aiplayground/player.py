import socketio
import random
import json
import time
import requests
from aiplayground.settings import ASIMOV_URL, EMAIL, PASSWORD

sio = socketio.Client()
player_id = None
server_id = None


@sio.on("connect")
def on_connect():
    print("I'm connected!")
    sio.emit("list")


@sio.on("rooms")
def on_rooms(data: dict):
    print(f"Received list of rooms:\n{json.dumps(data, indent=2)}")
    global server_id
    if server_id:
        return
    lobbies = [
        (k, v["game"], v["name"]) for k, v in data.items() if v["status"] == "lobby"
    ]
    if not lobbies:
        print("No active lobbies found, sleeping for 10s")
        time.sleep(10)
        sio.emit("list")
        return
    server_id, game, lobby = lobbies[0]
    sio.emit("join", {"roomid": server_id, "name": "Some Player"})


@sio.on("joined")
def on_joined(data):
    print(f"I received a joined message:\n{json.dumps(data, indent=2)}")
    global player_id
    player_id = data["playerid"]


@sio.on("gamestate")
def on_gamestate(data):
    print(f"I received a board message:\n{json.dumps(data['board'], indent=2)}")
    if data["turn"] == player_id:
        print("It's my move!")
        move = random.choice(["scissors", "paper", "rock"])
        sio.emit(
            "move", {"roomid": server_id, "playerid": player_id, "move": {"move": move}}
        )


@sio.on("finished")
def on_finished(data):
    if data["normal"]:
        print("Game finished normally")
        score = data["scores"][player_id]
        if score > 0:
            print("We won :)")
        elif score == 0:
            print("We tied :|")
        else:
            print("We lost :(")
    else:
        print(f"Game finished with error: {data['reason']}")


@sio.on("fail")
def on_fail(data):
    print(f"Received fail:\n{json.dumps(data, indent=2)}")


@sio.on("disconnect")
def on_disconnect():
    print("I'm disconnected!")


if EMAIL and PASSWORD:
    r = requests.post(ASIMOV_URL + "/auth/login", auth=(EMAIL, PASSWORD))
    token = r.json()["payload"]
    headers = {"Authorization": f"Bearer {token}"}
else:
    headers = {}
sio.connect(ASIMOV_URL, headers=headers)
