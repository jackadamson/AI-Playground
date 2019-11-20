from aiplayground.players.base import BasePlayer
import random


class ScissorsPaperRockPlayer(BasePlayer):
    gamename = "ScissorsPaperRock"
    description = "A random player for scissors paper rock"

    def get_move(self) -> dict:
        move = random.choice(["scissors", "paper", "rock"])
        return {"move": move}
