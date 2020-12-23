import json
from functools import wraps
from pydantic import ValidationError
from typing import TYPE_CHECKING, Callable, Type, Union, Tuple, Optional, Any, Awaitable
from aiplayground.logging import logger
from aiplayground.exceptions import AsimovErrorBase
from aiplayground.messages import MessageBase

if TYPE_CHECKING:
    from aiplayground.broker import GameBroker
    from aiplayground.player import PlayerClient
    from aiplayground.gameserver import GameServer

    SocketioType = Union[GameBroker, PlayerClient, GameServer]
else:
    SocketioType = Any


def expect(
    message_type: Type[MessageBase],
) -> Callable[[Callable[..., Awaitable]], Callable[[SocketioType, str, dict], Awaitable[Optional[Tuple]]]]:
    def decorator(f: Callable[..., Awaitable]):
        @wraps(f)
        async def wrapper(sio: SocketioType, *args):
            if len(args) == 1:
                [data] = args
                sid = None
            else:
                [sid, data] = args
            if data is None:
                data = dict()
            m = {k: v for k, v in data.items() if v is not None}
            try:
                msg = message_type.parse_obj(m)
            except ValidationError as e:
                logger.debug(f"Receieved invalid data:\n{json.dumps(data, indent=2)}")
                logger.warning(f"Validation encountered for {f.__name__}: {e!r}")
                return (
                    "fail",
                    {
                        "error": "InputValidationError",
                        "details": e.json(),
                    },
                )

            try:
                if sid is None:
                    await f(sio, msg=msg)
                else:
                    return await f(sio, sid=sid, msg=msg)

            except AsimovErrorBase as e:
                logger.exception(e)
                return (
                    "fail",
                    {
                        "error": e.__class__.__name__,
                        "details": e.details,
                    },
                )

        return wrapper

    return decorator
