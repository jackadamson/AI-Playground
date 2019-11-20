from abc import ABC, abstractmethod
from typing import Optional


class BasePlayer(ABC):
    gamename: str
    gamerole: Optional[str]
    board: Optional[dict] = None

    def __init__(self, gamerole: Optional[str] = None):
        self.gamerole = gamerole

    def update_board(self, board: dict) -> None:
        """
        Can be overridden to do processing even when not the player's turn
        Also can be overridden if players want to keep track of previous states
        :param board: New board state
        """
        self.board = board

    @abstractmethod
    def get_move(self) -> dict:
        pass
