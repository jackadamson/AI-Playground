from flask_restplus import Namespace, Resource
from aiplayground.api.rooms.models import Room
from aiplayground.api.rooms.schemas import room_schema, room_schema_brief

rooms_api = Namespace("Room", description="Game Rooms")


@rooms_api.route("/")
class RoomsView(Resource):
    @rooms_api.marshal_with(room_schema_brief, as_list=True)
    def get(self):
        return Room.list()


@rooms_api.route("/<room_id>")
class RoomView(Resource):
    @rooms_api.marshal_with(room_schema)
    def get(self, room_id):
        return Room.get(room_id)
