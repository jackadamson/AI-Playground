from flask_restplus import Namespace, Resource
from aiplayground.api.players.models import Player

players_api = Namespace("Player", description="Game Players")


@players_api.route("/")
class PlayersView(Resource):
    @players_api.marshal_with(Player.schema, as_list=True)
    def get(self):
        return Player.list()
