from flask_restplus import Model, fields
from aiplayground.api.players import player_schema

game_state_schema = Model(
    "Game State",
    {
        "id": fields.String(
            required=True,
            description="UUIDv4 uniquely identifying the game state",
            example="36cad58c-3421-4cb3-8773-cc8b0f0e808b",
        ),
        "timestamp": fields.DateTime(required=True),
        "player_id": fields.String(
            required=True,
            description="Identifies the player who made the move directly leading to the state",
            example="36cad58c-3421-4cb3-8773-cc8b0f0e808b",
        ),
        "epoch": fields.Integer(
            required=True,
            description="The index of the state within the span of the game",
        ),
        "move": fields.Raw(
            required=False, description="The actual move which lead to the state"
        ),
        "board": fields.Raw(required=False, description="Current game state",),
        "turn": fields.String(
            required=True,
            description="UUIDv4 of the player who should play next",
            example="36cad58c-3421-4cb3-8773-cc8b0f0e808b",
        ),
    },
)

room_schema = Model(
    "Room Detailed",
    {
        "id": fields.String(
            required=True,
            description="UUIDv4 uniquely identifying the room",
            example="36cad58c-3421-4cb3-8773-cc8b0f0e808b",
        ),
        "name": fields.String(
            required=True,
            description="The name of the game room",
            example="Chess Lobby 1",
        ),
        "game": fields.String(
            required=True, description="Player chosen name", example="tictactoe"
        ),
        "status": fields.String(
            required=True, description="Current game state", example="playing"
        ),
        "board": fields.Raw(
            required=True, description="Current game state", example="playing"
        ),
        "created_at": fields.DateTime(required=True),
        "players": fields.List(fields.Nested(player_schema)),
        "maxplayers": fields.Integer(required=True),
        "states": fields.List(
            fields.Nested(game_state_schema),
            attribute=lambda x: sorted(x.states, key=lambda y: y.epoch or 0),
        ),
    },
)
room_schema_brief = Model(
    "Room",
    {
        "id": fields.String(
            required=True,
            description="UUIDv4 uniquely identifying the room",
            example="36cad58c-3421-4cb3-8773-cc8b0f0e808b",
        ),
        "name": fields.String(
            required=True,
            description="The name of the game room",
            example="Chess Lobby 1",
        ),
        "game": fields.String(
            required=True, description="Player chosen name", example="tictactoe"
        ),
        "status": fields.String(
            required=True, description="Current game state", example="playing"
        ),
        "created_at": fields.DateTime(required=True),
        "players": fields.List(fields.Nested(player_schema)),
        "maxplayers": fields.Integer(required=True),
    },
)
all_schemas = [room_schema, room_schema_brief, game_state_schema]
