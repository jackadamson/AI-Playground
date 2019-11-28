from functools import partial
from typing import Any, Dict, Tuple

from flask_socketio import Namespace
from flaskplusplus import logger
from flaskplusplus.utils import optional_jwt_in_request
from redorm import InstanceNotFound
from aiplayground.utils.broker import get_room_player
from aiplayground.utils.expect import expect
from aiplayground.exceptions import (
    GameNotRunning,
    GameAlreadyStarted,
    NotPlayersTurn,
    NoSuchRoom,
    InputValidationError,
)
from aiplayground.messages import (
    CreateRoomMessage,
    GameUpdateMessage,
    JoinMessage,
    JoinFailMessage,
    JoinSuccessMessage,
    MoveMessage,
    ListMessage,
    GamestateMessage,
    JoinedMessage,
    PlayerMoveMessage,
    RegisterMessage,
    RoomCreatedMessage,
    JoinAcknowledgementMessage,
    SpectateMessage,
)
from aiplayground.api.rooms import Room, GameState
from aiplayground.api.players import Player
from aiplayground.types import (
    GameServerSID,
    PlayerSID,
    SpectatorSID,
    RoomId,
    PlayerId,
)


class GameBroker(Namespace):
    def acknowledge_join(self, room_id: RoomId, player_id: PlayerId) -> None:
        room = Room.get(room_id)
        JoinAcknowledgementMessage(roomid=room_id, playerid=player_id).send(
            sio=self, to=room.server_sid
        )

    @expect(CreateRoomMessage)
    def on_createroom(self, sid: GameServerSID, msg: CreateRoomMessage) -> None:
        """
        Server requests to create a game room
        """
        room = Room.create(
            name=msg.name, game=msg.game, maxplayers=msg.maxplayers, server_sid=sid
        )
        logger.debug(f"Registered Gameserver with room: {room.id}")
        RoomCreatedMessage(roomid=room.id).send(self, to=sid)

    @expect(JoinMessage)
    def on_join(self, sid: PlayerSID, msg: JoinMessage) -> None:
        """
        Player requests to join a game room
        """
        identity = optional_jwt_in_request()
        player: Player = Player.create(
            name=msg.name,
            room=msg.roomid,
            user_id=identity["id"] if identity is not None else None,
            sid=sid,
        )
        logger.debug("Player requested to join a room")
        player_id = player.id
        try:
            room: Room = Room.get(msg.roomid)
        except InstanceNotFound as e:
            raise NoSuchRoom from e
        if room.status != "lobby":
            raise GameAlreadyStarted
        else:
            logger.debug(f"Registering user")
            RegisterMessage(roomid=msg.roomid, playerid=player_id).send(
                self, to=room.server_sid
            )

    @expect(JoinSuccessMessage)
    def on_joinsuccess(self, sid: GameServerSID, msg: JoinSuccessMessage) -> None:
        """
        Server confirmed a player joining the lobby
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        assert player is not None
        player.update(joined=True, gamerole=msg.gamerole)
        self.enter_room(player.sid, room.broadcast_sid)
        JoinedMessage(
            roomid=msg.roomid,
            playerid=msg.playerid,
            name=player.name,
            gamerole=msg.gamerole,
            broadcast=False,
        ).send(
            self,
            to=player.sid,
            callback=partial(
                self.acknowledge_join, room_id=msg.roomid, player_id=msg.playerid
            ),
        )
        JoinedMessage(
            roomid=msg.roomid,
            playerid=msg.playerid,
            name=player.name,
            gamerole=msg.gamerole,
            broadcast=True,
        ).send(
            self, to=room.broadcast_sid,
        )

    @expect(JoinFailMessage)
    def on_joinfail(self, sid: GameServerSID, msg: JoinFailMessage) -> None:
        """
        Server responds that a player failed to join the lobby
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        assert player is not None
        self.emit(
            "fail",
            {"error": "registrationFailed", "reason": msg.reason},
            room=player.sid,
        )

    @expect(GameUpdateMessage)
    def on_gameupdate(self, sid: GameServerSID, msg: GameUpdateMessage) -> None:
        """
        Server notifies of a game state change
        """
        if msg.visibility == "private":
            if msg.playerid is None:
                raise InputValidationError(
                    details="error: 'playerid' must be provided when visibility is private"
                )
        else:
            if msg.playerid is not None:
                raise InputValidationError(
                    details="error: 'playerid' cannot be provided unless visibility is private"
                )
            if msg.epoch is None:
                raise InputValidationError(
                    details="error: 'epoch' is required for non-private messages"
                )
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        with room.lock(timeout=0.5, sleep=0.02):
            if msg.finish is not None:
                logger.info("Game finished")
                GamestateMessage.from_dict(msg.to_dict()).send(
                    self, to=room.broadcast_sid
                )
                room.update(status="finished")
            new_status = "finished" if room.status == "finished" else "playing"
            if msg.visibility == "private":
                room.update(status=new_status, turn=msg.turn)
                assert player is not None
                GamestateMessage(
                    board=msg.board,
                    turn=msg.turn,
                    roomid=msg.roomid,
                    playerid=msg.playerid,
                    epoch=msg.epoch,
                ).send(self, to=player.sid)
            else:
                if room.status == "finished":
                    room.update(board=msg.board, turn=None)
                else:
                    room.update(status=new_status, turn=msg.turn)
                if msg.visibility == "broadcast":
                    r = GamestateMessage(
                        board=msg.board,
                        turn=msg.turn,
                        roomid=msg.roomid,
                        playerid=msg.playerid,
                        epoch=msg.epoch,
                    )
                    logger.debug(
                        f"room.id={room.id}, room.broadcast_sid={room.broadcast_sid}"
                    )
                    r.send(sio=self, to=room.broadcast_sid)
                try:
                    state = GameState.get(msg.stateid)
                    if state.room is not None and state.room.id != msg.roomid:
                        raise InstanceNotFound
                except InstanceNotFound:
                    state_args = {
                        "room_id": msg.roomid,
                        "epoch": msg.epoch,
                        "board": msg.board,
                        "turn": msg.turn,
                    }
                    GameState.create(
                        **{k: v for k, v in state_args.items() if v is None}
                    )
                else:
                    state.update(epoch=msg.epoch, board=msg.board, turn=msg.turn)
                room.update(
                    status=new_status, board=msg.board, turn=msg.turn,
                )

    @expect(MoveMessage)
    def on_move(self, sid: PlayerSID, msg: MoveMessage) -> None:
        """
        Player sends a move request
        """
        room, player = get_room_player(
            sid, msg.roomid, msg.playerid, check_server=False
        )
        if room.status != "playing":
            raise GameNotRunning
        elif room.turn != msg.playerid:
            raise NotPlayersTurn
        else:
            state = GameState.create(
                player_id=msg.playerid, room=msg.roomid, move=msg.move
            )
            PlayerMoveMessage(
                roomid=msg.roomid,
                playerid=msg.playerid,
                move=msg.move,
                stateid=state.id,
            ).send(self, to=room.server_sid)

    @expect(ListMessage)
    def on_list(
        self, sid: PlayerSID, msg: ListMessage
    ) -> Tuple[str, Dict[RoomId, Dict[str, Any]]]:
        return (
            "message",
            {
                room.id: {
                    "name": room.name,
                    "game": room.game,
                    "maxplayers": room.maxplayers,
                    "players": len(room.players),
                    "status": room.status,
                }
                for room in Room.list(status="lobby")
            },
        )

    @expect(SpectateMessage)
    def on_spectate(self, sid: SpectatorSID, msg: SpectateMessage) -> Tuple[str, Dict]:
        room, _ = get_room_player(sid, msg.roomid, None, check_server=False)
        self.enter_room(sid, room.broadcast_sid)
        self.enter_room(sid, room.spectator_sid)
        return (
            "message",
            {
                "board": room.board,
                "status": room.status,
                "players": {player.id: player.name for player in room.players},
                "turn": room.turn,
                "states": [
                    {
                        "id": state.id,
                        "timestamp": state.timestamp.isoformat(),
                        "epoch": state.epoch,
                        "move": state.move,
                        "board": state.board,
                        "turn": state.turn,
                    }
                    for state in room.states
                ],
            },
        )
