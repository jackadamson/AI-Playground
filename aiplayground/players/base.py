from abc import ABC, abstractmethod
from typing import Optional
from flaskplusplus.logging import logger


class BasePlayer(ABC):
    gamename: str
    gamerole: Optional[str]
    player_id: str
    board: Optional[dict] = None

    def __init__(self, player_id: str, gamerole: Optional[str] = None):
        self.gamerole = gamerole
        self.player_id = player_id

    def update(self, board: dict, turn: Optional[str] = None) -> Optional[dict]:
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
    def get_move(self) -> dict:
        pass
