import json
from dataclasses_jsonschema import JsonSchemaValidationError
from functools import wraps
from typing import TYPE_CHECKING, Callable, Type, Union, Tuple, Optional
from flask import request, has_request_context
from flaskplusplus import logger
from aiplayground.exceptions import AsimovErrorBase
from aiplayground.messages import MessageBase

if TYPE_CHECKING:
    from aiplayground.broker import GameBroker
    from aiplayground.player import PlayerClient
    from aiplayground.gameserver import GameServer

SocketioType = Union["GameBroker", "PlayerClient", "GameServer"]


def expect(
    message_type: Type[MessageBase],
) -> Callable[[Callable], Callable[[SocketioType], Optional[Tuple]]]:
    def decorator(f: Callable[..., None]):
        @wraps(f)
        def wrapper(self: SocketioType, data: dict = None):
            if data is None:
                data = dict()
            m = {k: v for k, v in data.items() if v is not None}
            try:
                msg = message_type.from_dict(m)
            except JsonSchemaValidationError as e:
                logger.debug(f"Receieved invalid data:\n{json.dumps(data, indent=2)}")
                logger.warning(f"Validation encountered for {f.__name__}: {e.message}")
                return (
                    "fail",
                    {
                        "error": "InputValidationError",
                        "details": e.message,
                        # "respondingTo": f.__name__[3:],
                    },
                )

            try:
                logger.debug(f"Receieved message:\n{msg!r}")
                if has_request_context():
                    return f(self, sid=request.sid, msg=msg)
                else:
                    return f(self, msg=msg)

            except AsimovErrorBase as e:
                logger.exception(e)
                return (
                    "fail",
                    {
                        "error": e.__class__.__name__,
                        "details": e.details,
                        # "respondingTo": f.__name__[3:],
                    },
                )

        return wrapper

    return decorator
