from typing import Optional, Dict
from flask import request
from flask_socketio import Namespace
from flaskplusplus import logger
from flaskplusplus.utils import optional_jwt_in_request
from aiplayground.schemas import (
    createroom_schema,
    gameupdate_schema,
    join_schema,
    joinfail_schema,
    move_schema,
    finish_schema,
    joinsuccess_schema,
)
from aiplayground.utils.broker import expect, get_room_player
from aiplayground.exceptions import (
    GameNotRunning,
    GameAlreadyStarted,
    NotPlayersTurn,
    NoSuchRoom,
)
from aiplayground.messages import (
    FinishedMessage,
    GamestateMessage,
    JoinedMessage,
    PlayerMoveMessage,
    RegisterMessage,
    RoomCreatedMessage,
)
from aiplayground.api.rooms import Room, GameState
from aiplayground.api.players import Player


class GameRoom(Namespace):
    def on_connect(self):
        logger.debug(f"Connection: sid={request.sid!r}")

    def on_disconnect(self):
        logger.debug(f"Disconnect: sid={request.sid!r}")

    @expect(createroom_schema)
    def on_createroom(self, sid: str, name: str, game: str, maxplayers: str):
        """
        :from gameserver
        :param sid
        :param name
        :param game
        :param maxplayers
        """
        room = Room.create(name=name, game=game, maxplayers=maxplayers, sid=sid)
        logger.info(f"Registered Gameserver with room: {room.id}")
        RoomCreatedMessage(self, to=sid, roomid=room.id)

    @expect(join_schema)
    def on_join(self, sid: str, roomid: str, name: str):
        """
        :from player
        :param name: Player provided name to use within the game
        :param sid: Socket.io session id of the player
        :param roomid: ID of room player wishes to join
        """
        identity = optional_jwt_in_request()
        player: Player = Player.create(
            name=name,
            room_id=roomid,
            user_id=identity["id"] if identity is not None else None,
            sid=sid,
        )
        logger.info("Player requested to join a room")
        player_id = player.id
        room: Room = Room.get(roomid, relax=True)
        if room is None:
            raise NoSuchRoom
        elif room.status != "lobby":
            raise GameAlreadyStarted
        else:
            logger.info(f"Registering user")
            RegisterMessage(self, to=room.sid, roomid=roomid, playerid=player_id)

    @expect(joinsuccess_schema)
    def on_joinsuccess(self, sid, playerid, roomid):
        """
        :from gameserver
        :param sid: Socket.io session ID of the gameserver
        :param playerid: ID of player that has been accepted into the room
        :param roomid: ID of the room
        """
        room, player = get_room_player(sid, roomid, playerid)
        player.update(joined=True)
        self.enter_room(player.sid, room.id)
        JoinedMessage(self, to=player.sid, roomid=roomid, playerid=playerid)

    @expect(joinfail_schema)
    def on_joinfail(
        self, sid, playerid: str, roomid: str, reason: Optional[str] = None
    ):
        """
        :from gameserver
        :param sid
        :param playerid
        :param roomid
        :param reason
        """
        room, player = get_room_player(sid, roomid, playerid)
        self.emit(
            "fail", {"error": "registrationFailed", "reason": reason}, room=player.sid
        )

    @expect(gameupdate_schema)
    def on_gameupdate(
        self,
        sid: str,
        visibility: str,
        roomid: str,
        board: dict,
        turn: str,
        playerid: Optional[str] = None,
        stateid: Optional[str] = None,
        epoch: Optional[int] = None,
    ):
        """
        :from gameserver
        :param sid: Session ID of the game server
        :param visibility: Who to show update to, spectator doesn't send to players, broadcast is all players, private is specified user
        :param roomid: ID of game server sending update
        :param board: Dict of board state
        :param turn: Player ID of who next to play
        :param playerid: If visibility is private, the playerid to send update to
        :param stateid: The ID of the game state to correlate a player action
        :param epoch: The number of state changes before this one
        """
        logger.info("Received Game Update")
        room, player = get_room_player(sid, roomid, playerid)
        if room.status == "finished":
            room.update(board=board, turn=None)

        if visibility == "private":
            room.update(status="playing", turn=turn)
            GamestateMessage(
                self,
                to=player.sid,
                board=board,
                turn=turn,
                roomid=roomid,
                playerid=playerid,
            )
        else:
            if visibility == "broadcast":
                GamestateMessage(
                    self,
                    to=room.id,
                    board=board,
                    turn=turn,
                    roomid=roomid,
                    playerid=playerid,
                )
            state = GameState.get(id=stateid, room_id=roomid, relax=True)
            if state is None:
                GameState.create(room_id=roomid, epoch=epoch, board=board, turn=turn)
            else:
                state.update(epoch=epoch, board=board, turn=turn)
            room.update(status="playing", board=board, turn=turn)

    @expect(move_schema)
    def on_move(self, sid: str, playerid: str, roomid: str, move: dict):
        """
        :from player
        :param sid: Player Session ID
        :param playerid: Player ID
        :param roomid: Room ID
        :param move: Arbitrary dictionary that serializes the players move
        """
        room, player = get_room_player(sid, roomid, playerid, check_server=False)
        if room.status != "playing":
            raise GameNotRunning
        elif room.turn != playerid:
            raise NotPlayersTurn
        else:
            logger.debug(
                f"------\nUser made move\n-------\nplayer_id={playerid!r}, room_id={roomid!r}, move={move!r}"
            )
            state = GameState.create(player_id=playerid, room_id=roomid, move=move)
            PlayerMoveMessage(
                self,
                to=room.sid,
                roomid=roomid,
                playerid=playerid,
                move=move,
                stateid=state.id,
            )

    @expect(finish_schema)
    def on_finish(
        self,
        sid: str,
        roomid: str,
        normal: bool,
        scores: Optional[Dict[str, int]] = None,
        reason: Optional[str] = None,
    ):
        """
        :from player
        :param sid: Session ID of the game server
        :param roomid: ID of the game server
        :param normal: Whether the game finished properly (not errored)
        :param scores: Dictionary of playerid to their score (1,0,-1)
        :param reason: What error occurred (timeout, serverError etc)
        """
        # TODO: Add validation of game state (eg. not finished)
        # TODO: Just a ton of validation here in general
        logger.info("Received finish event")
        room, _ = get_room_player(sid, roomid, None)
        if room.status == "finished":
            raise GameNotRunning
        else:
            room.update(status="finished")
            FinishedMessage(
                self, to=room.id, normal=normal, reason=reason, scores=scores
            )

    def on_list(self):
        self.emit(
            "rooms",
            {
                room.id: {
                    "name": room.name,
                    "game": room.game,
                    "maxplayers": room.maxplayers,
                    "players": len(room.players),
                    "status": room.status,
                }
                for room in Room.list()
            },
            room=request.sid,
        )
