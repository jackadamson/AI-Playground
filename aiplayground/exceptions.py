class AsimovExceptionBase(Exception):
    details = "Base exception inherited by all other Asimov API exceptions"


class AsimovErrorBase(AsimovExceptionBase):
    details = "Base error inherited by all other Asimov API errors"


class AsimovServerError(AsimovErrorBase):
    details = "Base exception for when a gameAsimovExceptionBase server behaves incorrectly"


class AsimovPlayerError(AsimovErrorBase):
    details = "Base exception for when a player behaves incorrectly"


class NoSuchRoom(AsimovErrorBase):
    """
    Raised by broker
    """
    details = "The specified roomid does not correspond to an existing room"


class NoSuchPlayer(AsimovErrorBase):
    """
    Raised by broker
    """
    details = "The specified playerid does not correspond to an existing player"


class GameAlreadyStarted(AsimovPlayerError):
    """
    Raised by broker
    """
    details = "The specified room cannot be joined as the game has already begun"


class UnauthorizedGameServer(AsimovServerError):
    """
    Raised by broker
    """
    details = "The specified room is owned by a different server"


class UnauthorizedPlayer(AsimovPlayerError):
    """
    Raised by broker
    """
    details = "The specified player is owned by a different user"


class PlayerNotInRoom(AsimovServerError):
    """
    Raised by broker
    """
    details = "The specified player is in a different room"


class GameNotRunning(AsimovPlayerError):
    """
    Raised by broker or gameserver
    """
    details = (
        "The game in the specified room has either not started, or is already completed"
    )


class NotPlayersTurn(AsimovPlayerError):
    """
    Raised by broker or gameserver
    """
    details = "It is not currently your turn"


class GameFull(AsimovPlayerError):
    """
    Raised by gameserver
    """
    details = "Player tried to join full game"


class ExistingPlayer(AsimovServerError):
    """
    Raised by gameserver
    """
    details = "Player tried to join game they are already in"


class GameCompleted(AsimovExceptionBase):
    """
    Not propogated
    """

    details = "The game has just completed"


class IllegalMove(AsimovServerError):
    """
    Raised by gameserver
    """

    details = "Player attempted a move that is not a legal move"

all_exceptions = {"IllegalMove": IllegalMove}
