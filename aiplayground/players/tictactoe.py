from aiplayground.players.base import BasePlayer
import random


class TicTacToeRandomPlayer(BasePlayer):
    gamename = "TicTacToe"
    description = "A random player for tic tac toe"

    def get_move(self) -> dict:
        available_moves = [
            {"row": row, "col": col}
            for row in range(3)
            for col in range(3)
            if self.board[row][col] is None
        ]
        random.choice(available_moves)
        return random.choice(available_moves)
