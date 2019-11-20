from flask import request
from flask_socketio import Namespace
from flaskplusplus import logger
from flaskplusplus.utils import optional_jwt_in_request
from aiplayground.utils.broker import expect, get_room_player
from aiplayground.exceptions import (
    GameNotRunning,
    GameAlreadyStarted,
    NotPlayersTurn,
    NoSuchRoom,
)
from aiplayground.messages import (
    CreateRoomMessage,
    GameUpdateMessage,
    JoinMessage,
    JoinFailMessage,
    JoinSuccessMessage,
    MoveMessage,
    FinishMessage,
    ListMessage,
    RoomsMessage,
    FinishedMessage,
    GamestateMessage,
    JoinedMessage,
    PlayerMoveMessage,
    RegisterMessage,
    RoomCreatedMessage,
)
from aiplayground.api.rooms import Room, GameState, BoardState
from aiplayground.api.players import Player


class GameRoom(Namespace):
    def on_connect(self):
        logger.debug(f"Connection: sid={request.sid!r}")

    def on_disconnect(self):
        logger.debug(f"Disconnect: sid={request.sid!r}")

    @expect(CreateRoomMessage)
    def on_createroom(self, sid: str, msg: CreateRoomMessage):
        """
        Server requests to create a game room
        """
        room = Room.create(
            name=msg.name, game=msg.game, maxplayers=msg.maxplayers, sid=sid
        )
        logger.info(f"Registered Gameserver with room: {room.id}")
        RoomCreatedMessage(roomid=room.id).send(self, to=sid)

    @expect(JoinMessage)
    def on_join(self, sid: str, msg: JoinMessage):
        """
        Player requests to join a game room
        """
        identity = optional_jwt_in_request()
        player: Player = Player.create(
            name=msg.name,
            room_id=msg.roomid,
            user_id=identity["id"] if identity is not None else None,
            sid=sid,
        )
        logger.info("Player requested to join a room")
        player_id = player.id
        room: Room = Room.get(msg.roomid, relax=True)
        if room is None:
            raise NoSuchRoom
        elif room.status != "lobby":
            raise GameAlreadyStarted
        else:
            logger.info(f"Registering user")
            RegisterMessage(roomid=msg.roomid, playerid=player_id).send(
                self, to=room.sid
            )

    @expect(JoinSuccessMessage)
    def on_joinsuccess(self, sid, msg: JoinSuccessMessage):
        """
        Server confirmed a player joining the lobby
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        player.update(joined=True, game_role=msg.gamerole)
        self.enter_room(player.sid, room.id)
        JoinedMessage(
            roomid=msg.roomid, playerid=msg.playerid, gamerole=msg.gamerole
        ).send(self, to=player.sid)

    @expect(JoinFailMessage)
    def on_joinfail(self, sid, msg: JoinFailMessage):
        """
        Server responds that a player failed to join the lobby
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        self.emit(
            "fail",
            {"error": "registrationFailed", "reason": msg.reason},
            room=player.sid,
        )

    @expect(GameUpdateMessage)
    def on_gameupdate(self, sid: str, msg: GameUpdateMessage):
        """
        Server notifies of a game state change
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        if room.status == "finished":
            room.update(board=msg.board, turn=None)

        if msg.visibility == "private":
            room.update(status="playing", turn=msg.turn)
            GamestateMessage(
                board=msg.board, turn=msg.turn, roomid=msg.roomid, playerid=msg.playerid
            ).send(self, to=player.sid)
        else:
            room.update(status="playing", turn=msg.turn)
            if msg.visibility == "broadcast":
                r = GamestateMessage(
                    board=msg.board,
                    turn=msg.turn,
                    roomid=msg.roomid,
                    playerid=msg.playerid,
                )
                r.send(sio=self, to=room.id)
            state = GameState.get(id=msg.stateid, room_id=msg.roomid, relax=True)
            if state is None:
                GameState.create(
                    room_id=msg.roomid, epoch=msg.epoch, board=msg.board, turn=msg.turn
                )
            else:
                state.update(epoch=msg.epoch, board=msg.board, turn=msg.turn)
            room.update(status="playing", board=msg.board, turn=msg.turn)

    @expect(MoveMessage)
    def on_move(self, sid: str, msg: MoveMessage):
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
                player_id=msg.playerid, room_id=msg.roomid, move=msg.move
            )
            PlayerMoveMessage(
                roomid=msg.roomid,
                playerid=msg.playerid,
                move=msg.move,
                stateid=state.id,
            ).send(self, to=room.sid)

    @expect(FinishMessage)
    def on_finish(self, sid: str, msg: FinishMessage):
        """
        Server notifies that the game has finished
        """
        # TODO: Validation around server sending back acceptable scores
        logger.info("Received finish event")
        room, _ = get_room_player(sid, msg.roomid, None)
        if room.status == "finished":
            raise GameNotRunning
        else:
            room.update(status="finished")
            FinishedMessage(
                normal=msg.normal,
                reason=msg.reason,
                scores=msg.scores,
                roomid=msg.roomid,
            ).send(self, to=room.id)

    @expect(ListMessage)
    def on_list(self, sid: str, msg: ListMessage):
        RoomsMessage(
            rooms={
                room.id: {
                    "name": room.name,
                    "game": room.game,
                    "maxplayers": room.maxplayers,
                    "players": len(room.players),
                    "status": room.status,
                }
                for room in Room.list(status="lobby")
            }
        ).send(sio=self, to=sid)
