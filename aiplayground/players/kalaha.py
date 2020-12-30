import logging
import random
from time import sleep

from aiplayground.logging import logger
from aiplayground.players.base import BasePlayer
from aiplayground.types import GameName, Move


class KalahaRandomPlayer(BasePlayer):
    gamename: GameName = GameName("Kalaha")
    description = "A random player for Kalaha"

    def get_move(self) -> Move:
        assert self.board is not None
        assert self.gamerole is not None
        player_pits = self.board[f"pits_{self.gamerole}"]
        legal_moves = [{"move": idx} for idx, pits in enumerate(player_pits) if pits > 0]
        logger.debug(self.board)
        if logger.isEnabledFor(logging.DEBUG):
            sleep(1.5)
        return Move(random.choice(legal_moves))
