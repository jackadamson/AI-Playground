from typing import Optional, Dict
from abc import ABC, abstractmethod
from aiplayground.exceptions import (
    GameFull,
    ExistingPlayer,
    NotPlayersTurn,
    GameNotRunning,
)


class BaseGameServer(ABC):
    board: Optional[dict] = None
    playing: bool = False
    winner: Optional[int] = None
    movenumber: int = 0
    max_players: int = 2
    players: list
    turn: Optional[int] = None
    gamename: str = "BaseGame"
    description: str = "A base game"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players = list()

    def add_player(self, player_id: str) -> None:
        if player_id in self.players:
            raise ExistingPlayer
        if len(self.players) >= self.max_players:
            raise GameFull
        self.players.append(player_id)
        if len(self.players) == self.max_players:
            self.playing = True
            self.init_game()
            self.turn = 0

    def move(self, player_id: str, move: dict) -> dict:
        if not self.playing:
            raise GameNotRunning

        current_id = self.players[self.turn]
        if player_id != current_id:
            raise NotPlayersTurn
        self.movenumber += 1
        self.make_move(move)
        return self.show_board()

    @abstractmethod
    def init_game(self):
        raise NotImplementedError

    @abstractmethod
    def make_move(self, move: dict):
        raise NotImplementedError

    @abstractmethod
    def score(self) -> Dict[str, int]:
        """
        Returns the score dictionary of a completed game
        The score dictionary has a key per player_id
        and the value is a 1,0 or -1 to indicate win/loss/draw
        """
        raise NotImplementedError

    def show_board(self) -> Optional[dict]:
        """
        Returns a dictionary representing the game state if the game
        If the game is waiting for more players to join, returns None
        """
        return self.board
