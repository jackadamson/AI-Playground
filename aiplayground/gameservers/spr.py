from typing import Dict
from aiplayground.gameservers.base import BaseGame
from aiplayground.exceptions import GameCompleted


class ScissorsPaperRock(BaseGame):
    max_players = 2
    description = "Scissors beats Paper, Paper beats Rock, Rock beats Scissors."
    move_map = {"scissors": 0, "paper": 1, "rock": 2}

    def init_game(self):
        self.board = {"choices": [None, None]}

    def show_board(self):
        return (
            {
                "choices": {
                    self.players[i]: None if self.playing else v
                    for i, v in enumerate(self.board["choices"])
                }
            }
            if self.board is not None
            else None
        )

    def make_move(self, move):
        m: str = move["move"]
        if m not in ["scissors", "paper", "rock"]:
            raise ValueError
        if self.turn == 0:
            self.board["choices"][0] = m
            self.turn = True
        else:
            if m == self.board["choices"][0]:
                self.board["choices"] = [None, None]
                self.turn = 0
            else:
                self.board["choices"][1] = m
                raise GameCompleted

    def score(self) -> Dict[str, int]:
        first_move = self.move_map[self.board["choices"][0]]
        second_move = self.move_map[self.board["choices"][1]]
        if second_move == (first_move + 1) % 3:
            self.winner = 0
        else:
            self.winner = 1
        return {p: 1 if i == self.winner else -1 for i, p in enumerate(self.players)}
