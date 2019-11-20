from aiplayground.players.base import BasePlayer
from aiplayground.types import GameName, Move
import random


class ScissorsPaperRockPlayer(BasePlayer):
    gamename: GameName = GameName("ScissorsPaperRock")
    description = "A random player for scissors paper rock"

    def get_move(self) -> Move:
        move = random.choice(["scissors", "paper", "rock"])
        return Move({"move": move})
