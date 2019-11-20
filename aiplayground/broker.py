from functools import partial
from flask_socketio import Namespace
from flaskplusplus import logger
from flaskplusplus.utils import optional_jwt_in_request
from aiplayground.utils.broker import get_room_player
from aiplayground.utils.expect import expect
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
    ListMessage,
    RoomsMessage,
    FinishMessage,
    GamestateMessage,
    JoinedMessage,
    PlayerMoveMessage,
    RegisterMessage,
    RoomCreatedMessage,
    JoinAcknowledgement,
)
from aiplayground.api.rooms import Room, GameState
from aiplayground.api.players import Player
from aiplayground.types import (
    GameServerSID,
    PlayerSID,
    RoomId,
    PlayerId,
)


class GameBroker(Namespace):
    def acknowledge_join(self, room_id: RoomId, player_id: PlayerId):
        room = Room.get(room_id)
        JoinAcknowledgement(roomid=room_id, playerid=player_id).send(
            sio=self, to=room.server_sid
        )

    @expect(CreateRoomMessage)
    def on_createroom(self, sid: GameServerSID, msg: CreateRoomMessage):
        """
        Server requests to create a game room
        """
        room = Room.create(
            name=msg.name, game=msg.game, maxplayers=msg.maxplayers, server_sid=sid
        )
        logger.debug(f"Registered Gameserver with room: {room.id}")
        RoomCreatedMessage(roomid=room.id).send(self, to=sid)

    @expect(JoinMessage)
    def on_join(self, sid: PlayerSID, msg: JoinMessage):
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
        logger.debug("Player requested to join a room")
        player_id = player.id
        room: Room = Room.get(msg.roomid, relax=True)
        if room is None:
            raise NoSuchRoom
        elif room.status != "lobby":
            raise GameAlreadyStarted
        else:
            logger.debug(f"Registering user")
            RegisterMessage(roomid=msg.roomid, playerid=player_id).send(
                self, to=room.server_sid
            )

    @expect(JoinSuccessMessage)
    def on_joinsuccess(self, sid: GameServerSID, msg: JoinSuccessMessage):
        """
        Server confirmed a player joining the lobby
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        assert player is not None
        player.update(joined=True, game_role=msg.gamerole)
        self.enter_room(player.sid, f"room-{room.id}")
        JoinedMessage(
            roomid=msg.roomid, playerid=msg.playerid, gamerole=msg.gamerole
        ).send(
            self,
            to=player.sid,
            callback=partial(
                self.acknowledge_join, room_id=msg.roomid, player_id=msg.playerid
            ),
        )

    @expect(JoinFailMessage)
    def on_joinfail(self, sid: GameServerSID, msg: JoinFailMessage):
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
    def on_gameupdate(self, sid: GameServerSID, msg: GameUpdateMessage):
        """
        Server notifies of a game state change
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        if room.status == "finished":
            room.update(board=msg.board, turn=None)

        if msg.visibility == "private":
            room.update(status="playing", turn=msg.turn)
            assert player is not None
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
                logger.debug(
                    f"room.id={room.id}, room.broadcast_sid={room.broadcast_sid}"
                )
                r.send(sio=self, to=room.broadcast_sid)
            state = GameState.get(id=msg.stateid, room_id=msg.roomid, relax=True)
            if state is None:
                GameState.create(
                    room_id=msg.roomid, epoch=msg.epoch, board=msg.board, turn=msg.turn
                )
            else:
                state.update(epoch=msg.epoch, board=msg.board, turn=msg.turn)
            room.update(status="playing", board=msg.board, turn=msg.turn)

    @expect(MoveMessage)
    def on_move(self, sid: PlayerSID, msg: MoveMessage):
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
            ).send(self, to=room.server_sid)

    @expect(FinishMessage)
    def on_finish(self, sid: GameServerSID, msg: FinishMessage):
        """
        Server notifies that the game has finished
        """
        # TODO: Validation around server sending back acceptable scores
        room, _ = get_room_player(sid, msg.roomid, None)
        logger.info("Game finished")
        if room.status == "finished":
            raise GameNotRunning
        else:
            room.update(status="finished")
            msg.send(self, to=room.broadcast_sid)

    @expect(ListMessage)
    def on_list(self, sid: PlayerSID, msg: ListMessage):
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
