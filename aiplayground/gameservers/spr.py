from typing import Dict, Optional
from flaskplusplus.logging import logger
from aiplayground.gameservers.base import BaseGameServer
from aiplayground.exceptions import GameCompleted


class ScissorsPaperRockServer(BaseGameServer):
    max_players = 2
    gamename = "ScissorsPaperRock"
    description = "Scissors beats Paper, Paper beats Rock, Rock beats Scissors."
    move_map = {"scissors": 0, "paper": 1, "rock": 2}
    winner: Optional[str] = None

    def init_game(self):
        self.board = {"choices": {"a": None, "b": None}}
        self.turn = self.roles["a"]

    def show_board(self):
        return (
            {
                "choices": {
                    k: None if self.playing else v
                    for k, v in self.board["choices"].items()
                }
            }
            if self.board is not None
            else None
        )

    def asign_role(self, player_id: str) -> Optional[str]:
        if "a" in self.roles:
            role = "b"
        else:
            role = "a"
        self.players[player_id] = role
        self.roles[role] = player_id
        return role

    def make_move(self, player_id: str, player_role: Optional[str], move: dict):
        m: str = move["move"]
        if m not in ["scissors", "paper", "rock"]:
            raise ValueError
        logger.debug(f"Player Role: {player_role}")
        if player_role == "a":
            self.board["choices"]["a"] = m
            self.turn = self.roles["b"]
        elif m == self.board["choices"]["b"]:
            self.board["choices"] = {"a": None, "b": None}
            self.turn = self.roles["a"]
        else:
            self.board["choices"]["b"] = m
            raise GameCompleted

    def score(self) -> Dict[str, int]:
        first_move = self.move_map[self.board["choices"]["a"]]
        second_move = self.move_map[self.board["choices"]["b"]]
        if second_move == (first_move + 1) % 3:
            self.winner = self.roles["a"]
        else:
            self.winner = self.roles["b"]
        return {k: 1 if k == self.winner else -1 for k in self.players}
