from typing import Dict, Optional

from aiplayground.types import GameRole, PlayerId, Board, Move
from flaskplusplus.logging import logger
from aiplayground.gameservers.base import BaseGameServer
from aiplayground.exceptions import GameCompleted

player_a = GameRole("a")
player_b = GameRole("b")


class ScissorsPaperRockServer(BaseGameServer):
    max_players = 2
    gamename = "ScissorsPaperRock"
    description = "Scissors beats Paper, Paper beats Rock, Rock beats Scissors."
    move_map = {"scissors": 0, "paper": 1, "rock": 2}
    winner: Optional[PlayerId] = None
    board: Dict[GameRole, Optional[str]]

    def init_game(self):
        self.board = {player_a: None, player_b: None}
        self.turn = self.roles[player_a]

    def show_board(self) -> Board:
        return Board(
            {k: None if self.playing else v for k, v in self.board.items()}
            if self.board is not None
            else None
        )

    def asign_role(self, player_id: PlayerId) -> Optional[GameRole]:
        if player_a in self.roles:
            role = player_b
        else:
            role = player_a
        self.players[player_id] = role
        self.roles[role] = player_id
        return role

    def make_move(
        self, player_id: PlayerId, player_role: Optional[GameRole], move: Move
    ):
        m: str = move["move"]
        if m not in ["scissors", "paper", "rock"]:
            raise ValueError
        logger.debug(f"Player Role: {player_role}")
        if player_role == player_a:
            self.board[player_a] = m
            self.turn = self.roles[player_b]
        elif m == self.board[player_b]:
            self.board = {player_a: None, player_b: None}
            self.turn = self.roles[player_a]
        else:
            self.board[player_b] = m
            raise GameCompleted

    def score(self) -> Dict[str, int]:
        first_move = self.move_map[self.board[player_a]]
        second_move = self.move_map[self.board[player_b]]
        if second_move == (first_move + 1) % 3:
            self.winner = self.roles[player_a]
        else:
            self.winner = self.roles[player_b]
        return {k: 1 if k == self.winner else -1 for k in self.players}
