from typing import Dict, Type
from aiplayground.types import GameName

from aiplayground.players.base import BasePlayer
from aiplayground.players.spr import ScissorsPaperRockPlayer
from aiplayground.players.tictactoe import TicTacToeRandomPlayer
from aiplayground.players.kalaha import KalahaRandomPlayer


all_players: Dict[GameName, Type[BasePlayer]] = {
    ScissorsPaperRockPlayer.gamename: ScissorsPaperRockPlayer,
    TicTacToeRandomPlayer.gamename: TicTacToeRandomPlayer,
    KalahaRandomPlayer.gamename: KalahaRandomPlayer,
}
