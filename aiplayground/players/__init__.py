from aiplayground.players.base import BasePlayer
from aiplayground.players.spr import ScissorsPaperRockPlayer
from aiplayground.players.tictactoe import TicTacToeRandomPlayer

all_players = {
    ScissorsPaperRockPlayer.gamename: ScissorsPaperRockPlayer,
    TicTacToeRandomPlayer.gamename: TicTacToeRandomPlayer,
}
