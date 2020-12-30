import random
from typing import Dict, Optional, List, Union, Iterator
import itertools

from aiplayground.exceptions import GameCompleted, IllegalMove
from aiplayground.gameservers.base import BaseGameServer
from aiplayground.logging import logger
from aiplayground.types import GameRole, PlayerId, Move, Board

player_a = GameRole("a")
player_b = GameRole("b")


def other(current: GameRole) -> GameRole:
    return player_a if current == player_b else player_b


def getter(state, path: List[Union[int, str]]):
    if len(path):
        [idx, *path_rem] = path
        return getter(state[idx], path_rem)
    return state


def setter(state, path: List[Union[int, str]], value):
    assert len(path) > 0
    if len(path) > 1:
        [idx, *path_rem] = path
        setter(state[idx], path_rem, value)
    else:
        state[path[0]] = value


path_orders: List[List[Union[str, int]]] = [
    *[["pits_a", i] for i in range(6)],
    ["bank_a"],
    *[["pits_b", i] for i in range(6)],
    ["bank_b"],
]


def skip(itera: Iterator, c: int):
    for i in range(c):
        next(itera)


class KalahaServer(BaseGameServer):
    gamename = "Kalaha"
    max_players = 2
    description = "Kalaha - (6, 6)"
    winner: Optional[PlayerId] = None
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["move"],
        "properties": {
            "move": {"type": "integer", "min": 0, "max": 5},
        },
        "additionalProperties": False,
    }

    def init_game(self):
        self.board = Board({"bank_a": 0, "bank_b": 0, "pits_a": [6] * 6, "pits_b": [6] * 6})
        self.turn = self.roles[player_a]

    def asign_role(self, player_id: PlayerId) -> Optional[GameRole]:
        logger.debug(f"Currently assigned roles: {self.roles}")
        available = list({player_a, player_b} - set(self.roles))
        logger.debug(f"Available roles: {available}")
        role = random.choice(available)
        logger.debug(f"Assigning role {player_id} -> {role}")
        self.players[player_id] = role
        self.roles[role] = player_id
        return role

    def make_move(self, player_id: PlayerId, player_role: Optional[GameRole], move: Move):
        logger.debug(f"Making move for role: {player_role}")
        if player_role is None:
            raise IllegalMove("Require game role")
        selected = move["move"]
        offset = 0 if player_role == player_a else 7
        board_positions = itertools.cycle(path_orders)
        skip(board_positions, selected + offset)
        current_path = next(board_positions)
        pips = getter(self.board, current_path)
        if pips == 0:
            raise IllegalMove("Empty pit chosen")
        setter(self.board, current_path, 0)
        other_bank = f"bank_{other(player_role)}"
        player_bank = f"bank_{player_role}"
        current_pips = 0
        # Distribute Pips
        for pip in range(pips):
            current_path = next(board_positions)
            if current_path[0] == other_bank:
                # Skip opponent bank
                current_path = next(board_positions)
            current_pips = getter(self.board, current_path)
            setter(self.board, current_path, current_pips + 1)

        if current_pips == 0 and current_path[0] == f"pits_{player_role}":
            pit = current_path[1]
            opposite_path = [f"pits_{other(player_role)}", 5 - pit]
            opposite_pips = getter(self.board, opposite_path)
            if opposite_pips > 0:
                bank_balance = getter(self.board, [player_bank])
                # Bank balance gains opposite pips and the pip just placed
                setter(self.board, [player_bank], bank_balance + opposite_pips + 1)
                setter(self.board, opposite_path, 0)
                setter(self.board, current_path, 0)

        next_role = player_role if current_path[0] == f"bank_{player_role}" else other(player_role)
        self.turn = self.roles[next_role]

        if sum(self.board["pits_a"]) == 0 or sum(self.board["pits_b"]) == 0:
            # End of game
            bank_a = sum(self.board["pits_a"]) + self.board["bank_a"]
            bank_b = sum(self.board["pits_b"]) + self.board["bank_b"]
            if bank_a > bank_b:
                self.winner = self.roles[player_a]
            elif bank_b > bank_a:
                self.winner = self.roles[player_b]
            else:
                self.winner = None
            raise GameCompleted

    def score(self) -> Dict[PlayerId, int]:
        if self.winner is None:
            # Draw
            return {k: 0 for k in self.players}
        else:
            return {k: 1 if k == self.winner else -1 for k in self.players}

    def show_board(self) -> Board:
        top_border = ">" * 25
        a_row = "| B|" + "|".join(f"{x: >2}" for x in self.board["pits_a"]) + "| A|"
        bank_row = f"|{self.board['bank_b']: >2}+" + ("--|" * 6) + f"{self.board['bank_a']: >2}|"
        b_row = "|  |" + "|".join(f"{x: >2}" for x in reversed(self.board["pits_b"])) + "|  |"
        bottom_border = "<" * 25
        board_repr = "\n".join([top_border, a_row, bank_row, b_row, bottom_border])
        logger.debug(f"Board:\n{board_repr}")
        return self.board
