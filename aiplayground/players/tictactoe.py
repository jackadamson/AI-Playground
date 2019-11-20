from aiplayground.players.base import BasePlayer
import random
from flaskplusplus.logging import logger


class TicTacToeRandomPlayer(BasePlayer):
    gamename = "TicTacToe"
    description = "A random player for tic tac toe"

    def get_move(self) -> dict:
        logger.debug(self.board)
        available_moves = [
            {"row": row, "col": col}
            for row in range(3)
            for col in range(3)
            if self.board["grid"][row][col] is None
        ]
        random.choice(available_moves)
        return random.choice(available_moves)
