from functools import partial
from typing import Any, Dict, Tuple

import socketio

from aiplayground.api.bot import Bot
from aiplayground.api.players import Player
from aiplayground.api.rooms import Room, GameState
from aiplayground.settings import settings
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
from aiplayground.types import (
    GameServerSID,
    PlayerSID,
    SpectatorSID,
    RoomId,
    PlayerId,
)
from aiplayground.utils.broker import get_room_player
from aiplayground.utils.expect import expect
from aiplayground.logging import logger
from redorm import InstanceNotFound

# TODO: Confirm CORS isn't being problematic
if settings.SOCKETIO_REDIS_URL is None:
    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
else:
    logger.info("Creating Redis Manager")
    sio_manager = socketio.AsyncRedisManager(settings.SOCKETIO_REDIS_URL)
    logger.info("Creating Socketio Server")
    sio = socketio.AsyncServer(async_mode="asgi", client_manager=sio_manager, cors_allowed_origins="*")
    logger.info("Created Socketio Server")


class GameBroker(socketio.AsyncNamespace):
    async def acknowledge_join(self, room_id: RoomId, player_id: PlayerId) -> None:
        room = Room.get(room_id)
        await JoinAcknowledgementMessage(roomid=room_id, playerid=player_id).send(sio=self, to=room.server_sid)

    @expect(CreateRoomMessage)
    async def on_createroom(self, sid: GameServerSID, msg: CreateRoomMessage) -> None:
        """
        Server requests to create a game room
        """
        room = Room.create(name=msg.name, game=msg.game, maxplayers=msg.maxplayers, server_sid=sid)
        logger.debug(f"Registered Gameserver with room: {room.id}")
        await RoomCreatedMessage(roomid=room.id).send(self, to=sid)

    @expect(JoinMessage)
    async def on_join(self, sid: PlayerSID, msg: JoinMessage) -> None:
        """
        Player requests to join a game room
        """
        # TODO: Fix join ID
        identity = {"id": "FIXME"}
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
            await RegisterMessage(roomid=msg.roomid, playerid=player_id).send(self, to=room.server_sid)

    @expect(JoinSuccessMessage)
    async def on_joinsuccess(self, sid: GameServerSID, msg: JoinSuccessMessage) -> None:
        """
        Server confirmed a player joining the lobby
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        assert player is not None
        player.update(joined=True, gamerole=msg.gamerole)
        self.enter_room(player.sid, room.broadcast_sid)
        await JoinedMessage(
            roomid=msg.roomid,
            playerid=msg.playerid,
            name=player.name,
            gamerole=msg.gamerole,
            broadcast=False,
        ).send(
            self,
            to=player.sid,
            callback=partial(self.acknowledge_join, room_id=msg.roomid, player_id=msg.playerid),
        )
        await JoinedMessage(
            roomid=msg.roomid,
            playerid=msg.playerid,
            name=player.name,
            gamerole=msg.gamerole,
            broadcast=True,
        ).send(
            self,
            to=room.broadcast_sid,
        )

    @expect(JoinFailMessage)
    async def on_joinfail(self, sid: GameServerSID, msg: JoinFailMessage) -> None:
        """
        Server responds that a player failed to join the lobby
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        assert player is not None
        await self.emit(
            "fail",
            {"error": "registrationFailed", "reason": msg.reason},
            room=player.sid,
        )

    @expect(GameUpdateMessage)
    async def on_gameupdate(self, sid: GameServerSID, msg: GameUpdateMessage) -> None:
        """
        Server notifies of a game state change
        """
        if msg.visibility == "private":
            if msg.playerid is None:
                raise InputValidationError(details="error: 'playerid' must be provided when visibility is private")
        else:
            if msg.playerid is not None:
                raise InputValidationError(details="error: 'playerid' cannot be provided unless visibility is private")
            if msg.epoch is None:
                raise InputValidationError(details="error: 'epoch' is required for non-private messages")
        room, player = get_room_player(sid, msg.roomid, msg.playerid)
        with room.lock(timeout=0.5, sleep=0.02):
            if msg.finish is not None:
                logger.info("Game finished")
                await GamestateMessage.parse_obj(msg.to_dict()).send(self, to=room.broadcast_sid)
                room.update(status="finished")
            new_status = "finished" if room.status == "finished" else "playing"
            if msg.visibility == "private":
                room.update(status=new_status, turn=msg.turn)
                assert player is not None
                await GamestateMessage(
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
                    logger.debug(f"room.id={room.id}, room.broadcast_sid={room.broadcast_sid}")
                    await r.send(sio=self, to=room.broadcast_sid)
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
                    GameState.create(**{k: v for k, v in state_args.items() if v is None})
                else:
                    state.update(epoch=msg.epoch, board=msg.board, turn=msg.turn)
                room.update(
                    status=new_status,
                    board=msg.board,
                    turn=msg.turn,
                )

    @expect(MoveMessage)
    async def on_move(self, sid: PlayerSID, msg: MoveMessage) -> None:
        """
        Player sends a move request
        """
        room, player = get_room_player(sid, msg.roomid, msg.playerid, check_server=False)
        if room.status != "playing":
            raise GameNotRunning
        elif room.turn != msg.playerid:
            raise NotPlayersTurn
        else:
            state = GameState.create(player_id=msg.playerid, room=msg.roomid, move=msg.move)
            await PlayerMoveMessage(
                roomid=msg.roomid,
                playerid=msg.playerid,
                move=msg.move,
                stateid=state.id,
            ).send(self, to=room.server_sid)

    @expect(ListMessage)
    async def on_list(self, sid: PlayerSID, msg: ListMessage) -> Tuple[str, Dict[RoomId, Dict[str, Any]]]:
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
    async def on_spectate(self, sid: SpectatorSID, msg: SpectateMessage) -> Tuple[str, Dict]:
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

    async def on_connect(self, sid, environ):
        headers = {k.decode(): v.decode() for k, v in environ["asgi.scope"]["headers"]}
        if headers.get("x-role") == "gameserver":
            await self.save_session(sid, {"role": "gameserver"})
            return
        else:
            try:
                api_key = headers["x-api-key"]
                bot = Bot.get(api_key=api_key)
                await self.save_session(sid, {"role": "player", "id": bot.id, "name": bot.name})
                return
            except KeyError:
                await self.emit(
                    "fail",
                    {"error": "connectFailed", "reason": "missing x-api-key"},
                    room=sid,
                )
            except InstanceNotFound:
                await self.emit(
                    "fail",
                    {"error": "connectFailed", "reason": "invaid api key"},
                    room=sid,
                )
            await self.disconnect(sid)


sio.register_namespace(GameBroker())
