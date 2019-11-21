from typing import Dict, Optional, List
import random
from aiplayground.logging import logger
from aiplayground.gameservers.base import BaseGameServer
from aiplayground.exceptions import GameCompleted, IllegalMove
from aiplayground.types import GameRole, PlayerId, Move, Board

player_x = GameRole("x")
player_o = GameRole("o")


class TicTacToeServer(BaseGameServer):
    gamename = "TicTacToe"
    max_players = 2
    description = "Naughts and crosses"
    winner: Optional[str] = None
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["row", "col"],
        "properties": {
            "row": {"type": "integer", "min": 0, "max": 2},
            "col": {"type": "integer", "min": 0, "max": 2},
        },
        "additionalProperties": False,
    }

    def init_game(self):
        self.board = Board({"grid": [[None for _i in range(3)] for _j in range(3)]})
        self.turn = self.roles[player_x]

    def asign_role(self, player_id: PlayerId) -> Optional[GameRole]:
        logger.debug(f"Currently assigned roles: {self.roles}")
        available = list({player_o, player_x} - set(self.roles))
        logger.debug(f"Available roles: {available}")
        role = random.choice(available)
        logger.debug(f"Assigning role {player_id} -> {role}")
        self.players[player_id] = role
        self.roles[role] = player_id
        return role

    def make_move(
        self, player_id: PlayerId, player_role: Optional[GameRole], move: Move
    ):
        logger.debug(f"Making move for role: {player_role}")
        col: int = move["col"]
        row: int = move["row"]
        grid: List[List[Optional[GameRole]]] = self.board["grid"]
        if grid[row][col] is not None:
            raise IllegalMove(
                details="Attempted to play in square that is already occupied"
            )
        grid[row][col] = player_role

        if (
            all(grid[row][i] == player_role for i in range(3))
            or all(grid[i][col] == player_role for i in range(3))
            or all(grid[i][i] == player_role for i in range(3))
            or all(grid[i][2 - i] == player_role for i in range(3))
        ):
            # Player won
            self.winner = player_id
            raise GameCompleted
        elif all(cell is not None for row in grid for cell in row):
            # Match is a draw
            self.winner = None
            raise GameCompleted
        else:
            next_role = player_o if player_role == player_x else player_x
            self.turn = self.roles[next_role]

    def score(self) -> Dict[PlayerId, int]:
        if self.winner is None:
            # Draw
            return {k: 0 for k in self.players}
        else:
            return {k: 1 if k == self.winner else -1 for k in self.players}

    def show_board(self) -> Board:
        board_repr = "\n -+-+-\n ".join(
            "|".join(" " if cell is None else cell for cell in row)
            for row in self.board["grid"]
        )
        logger.debug(f"Board:\n {board_repr}")
        return self.board
