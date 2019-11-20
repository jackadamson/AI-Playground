from aiplayground.gameservers.base import BaseGameServer
from aiplayground.gameservers.spr import ScissorsPaperRockServer
from aiplayground.gameservers.tictactoe import TicTacToeServer

all_games = {
    ScissorsPaperRockServer.gamename: ScissorsPaperRockServer,
    TicTacToeServer.gamename: TicTacToeServer,
}
