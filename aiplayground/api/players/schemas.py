from flask_restplus import Model, fields

player_schema = Model(
    "Player",
    {
        "id": fields.String(
            required=True,
            description="UUIDv4 uniquely identifying the player",
            example="36cad58c-3421-4cb3-8773-cc8b0f0e808b",
        ),
        "name": fields.String(
            required=True, description="Player chosen name", example="Some Player"
        ),
        "joined_at": fields.DateTime(required=False),
        "game_role": fields.String(
            required=False,
            description="Role a player has within the game, eg. in Tic Tac Toe 'x' or 'o'",
        ),
    },
)

all_schemas = [player_schema]
