class AsimovApiExceptionBase(Exception):
    details = "Base exception inherited by all other Asimov API exceptions"


class AsimovServerError(AsimovApiExceptionBase):
    details = "Base exception for when a game server behaves incorrectly"


class AsimovPlayerError(AsimovApiExceptionBase):
    details = "Base exception for when a player behaves incorrectly"


class NoSuchRoom(AsimovApiExceptionBase):
    details = "The specified roomid does not correspond to an existing room"


class NoSuchPlayer(AsimovApiExceptionBase):
    details = "The specified playerid does not correspond to an existing player"


class GameAlreadyStarted(AsimovPlayerError):
    details = "The specified room cannot be joined as the game has already begun"


class UnauthorizedGameServer(AsimovServerError):
    details = "The specified room is owned by a different server"


class UnauthorizedPlayer(AsimovPlayerError):
    details = "The specified player is owned by a different user"


class PlayerNotInRoom(AsimovServerError):
    details = "The specified player is in a different room"


class GameNotRunning(AsimovPlayerError):
    details = (
        "The game in the specified room has either not started, or is already completed"
    )


class NotPlayersTurn(AsimovPlayerError):
    details = "It is not currently your turn"
