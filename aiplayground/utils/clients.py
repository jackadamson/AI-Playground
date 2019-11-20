from jsonschema import validate, ValidationError
from functools import wraps
from typing import TYPE_CHECKING, Callable, Type
from flask import request
from flaskplusplus import logger
from aiplayground.exceptions import AsimovErrorBase
from aiplayground.messages import MessageBase

if TYPE_CHECKING:
    from aiplayground.broker import GameBroker


# Useful for gameservers and players
def expect(message_type: Type[MessageBase]):
    def decorator(f: Callable[..., None]):
        @wraps(f)
        def wrapper(self: "GameBroker", data: dict):
            try:
                validate(data, message_type.schema)
            except ValidationError as e:
                logger.error(f"Validation encountered for {f.__name__}: {e.message}")
                self.emit(
                    "fail",
                    {
                        "reason": "InputValidationError",
                        "details": e.message,
                        "respondingTo": f.__name__[3:],
                    },
                )
                return
            try:
                msg = message_type(**data)
                logger.debug(f"Receieved message:\n{msg!r}")
                return f(self, msg=msg)
            except AsimovErrorBase as e:
                logger.exception(e)
                self.emit(
                    "fail",
                    {
                        "reason": e.__class__.__name__,
                        "details": e.details,
                        "respondingTo": f.__name__[3:],
                    },
                    room=request.sid,
                )

        return wrapper

    return decorator
