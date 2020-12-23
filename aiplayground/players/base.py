from abc import ABC, abstractmethod
from typing import Optional

from aiplayground.logging import logger
from aiplayground.types import Move, PlayerId, GameName, Board, GameRole


class BasePlayer(ABC):
    gamename: GameName
    gamerole: Optional[GameRole]
    player_id: PlayerId
    board: Optional[Board] = None

    def __init__(self, player_id: PlayerId, gamerole: Optional[GameRole] = None):
        self.gamerole = gamerole
        self.player_id = player_id

    def update(self, board: Board, turn: Optional[PlayerId] = None) -> Optional[Move]:
        """
        Can be overridden to do processing even when not the player's turn
        Also can be overridden if players want to keep track of previous states
        :param turn: ID of player who'd turn it is
        :param board: New board state
        """
        self.board = board
        if turn == self.player_id and turn is not None:
            logger.debug("Our move to play")
            return self.get_move()
        else:
            return None

    @abstractmethod
    def get_move(self) -> Move:
        pass
