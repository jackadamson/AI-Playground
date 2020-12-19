import random
import logging
from time import sleep
from aiplayground.logging import logger
from aiplayground.types import GameName, Move
from aiplayground.players.base import BasePlayer


class TicTacToeRandomPlayer(BasePlayer):
    gamename: GameName = GameName("TicTacToe")
    description = "A random player for tic tac toe"

    def get_move(self) -> Move:
        assert self.board is not None
        logger.debug(self.board)
        if logger.isEnabledFor(logging.DEBUG):
            sleep(1.5)
        available_moves = [
            {"row": row, "col": col} for row in range(3) for col in range(3) if self.board["grid"][row][col] is None
        ]
        random.choice(available_moves)
        return Move(random.choice(available_moves))
