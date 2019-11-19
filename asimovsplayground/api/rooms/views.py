from flask_restplus import Namespace, Resource
from asimovsplayground.api.rooms.models import Room
from asimovsplayground.api.rooms.schemas import room_schema

rooms_api = Namespace("Room", description="Game Rooms")


@rooms_api.route("/")
class RoomsView(Resource):
    @rooms_api.marshal_with(room_schema, as_list=True)
    def get(self):
        return Room.list()
