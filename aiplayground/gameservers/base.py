from typing import Optional, Dict
from abc import ABC, abstractmethod
from jsonschema import validate, ValidationError
from aiplayground.exceptions import (
    GameFull,
    ExistingPlayer,
    NotPlayersTurn,
    GameNotRunning,
    IllegalMove,
)
from aiplayground.types import GameRole, PlayerId, Board, Move


class BaseGameServer(ABC):
    board: Optional[dict] = None
    playing: bool = False
    movenumber: int = 0
    max_players: int = 2
    players: Dict[PlayerId, Optional[GameRole]]
    roles: Dict[GameRole, PlayerId]
    turn: Optional[PlayerId] = None
    gamename: str = "BaseGame"
    description: str = "A base game"
    schema: dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players = dict()
        self.roles = dict()

    def add_player(self, player_id: PlayerId) -> Optional[GameRole]:
        if player_id in self.players:
            raise ExistingPlayer
        if len(self.players) >= self.max_players:
            raise GameFull
        return self.asign_role(player_id)

    def asign_role(self, player_id: PlayerId) -> Optional[GameRole]:
        return None

    def move(self, player_id: PlayerId, move: Move) -> Board:
        if not self.playing:
            raise GameNotRunning
        if player_id != self.turn:
            raise NotPlayersTurn
        try:
            validate(move, self.schema)
        except ValidationError as e:
            raise IllegalMove(details=e.message) from e
        self.movenumber += 1
        self.make_move(
            player_id=player_id, player_role=self.players.get(player_id), move=move
        )
        return self.show_board()

    def start(self):
        self.playing = True
        self.init_game()

    @abstractmethod
    def init_game(self):
        """
        Sets the board as needed and sets who's turn it is
        """
        raise NotImplementedError

    @abstractmethod
    def make_move(
        self, player_id: PlayerId, player_role: Optional[GameRole], move: Move
    ):
        """
        :param player_id: ID of the player moving
        :param player_role: Game assigned role for player
        :param move: Move for player to make
        :raises IllegalMove: If player attempts an illegal move
        """
        raise NotImplementedError

    @abstractmethod
    def score(self) -> Dict[PlayerId, int]:
        """
        Returns the score dictionary of a completed game
        The score dictionary has a key per player_id
        and the value is a 1,0 or -1 to indicate win/loss/draw
        """
        raise NotImplementedError

    def show_board(self) -> Optional[Board]:
        """
        Returns a dictionary representing the game state if the game
        If the game is waiting for more players to join, returns None
        """
        return self.board
