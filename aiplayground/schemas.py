createroom_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "game", "maxplayers"],
    "properties": {
        "name": {
            "type": "string",
            "title": "Game Room Name",
            "examples": ["Awesome Chess"],
            "pattern": "^([a-zA-Z _0-9-]*)$",
        },
        "game": {
            "type": "string",
            "title": "Game Name",
            "examples": ["chess"],
            "pattern": "^(.*)$",
        },
        "maxplayers": {"type": "integer"},
    },
    "additionalProperties": False,
}
join_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["roomid", "name"],
    "properties": {
        "roomid": {"type": "string", "title": "Room ID", "pattern": "^([a-z0-9-]*)$"},
        "name": {
            "type": "string",
            "title": "Player Name",
            "pattern": "^([a-zA-Z0-9_ -]+)$",
        },
    },
    "additionalProperties": False,
}
joinsuccess_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["playerid", "roomid"],
    "properties": {
        "playerid": {
            "type": "string",
            "title": "Player ID",
            "pattern": "^([a-z0-9-]*)$",
        },
        "roomid": {"type": "string", "title": "Room ID", "pattern": "^([a-z0-9-]*)$"},
        "gamerole": {
            "type": "string",
            "description": "What player in game they are, eg. in Tic Tac Toe, are they O or X",
        },
    },
    "additionalProperties": False,
}
joinfail_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["playerid", "roomid"],
    "properties": {
        "playerid": {
            "type": "string",
            "title": "Player ID",
            "pattern": "^([a-z0-9-]*)$",
        },
        "roomid": {"type": "string", "title": "Room ID", "pattern": "^([a-z0-9-]*)$"},
        "reason": {
            "type": "string",
            "title": "Reason",
            "description": "Reason player failed to join room",
        },
    },
    "additionalProperties": False,
}
gameupdate_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["visibility", "roomid", "board", "epoch"],
    "allOf": [
        {
            "if": {"properties": {"visibility": {"const": "private"}}},
            "then": {"required": ["playerid"], "not": {"required": ["epoch"]}},
            "else": {"required": ["epoch"], "not": {"required": ["playerid"]}},
        }
    ],
    "properties": {
        "playerid": {
            "type": "string",
            "title": "Player ID",
            "description": "Player to send the game update to",
            "pattern": "^([a-z0-9-]*)$",
        },
        "roomid": {"type": "string", "title": "Room ID", "pattern": "^([a-z0-9-]*)$"},
        "visibility": {
            "type": "string",
            "title": "Visibility",
            "enum": ["broadcast", "spectator", "private"],
            "description": "Whether the game update should be sent to everyone (broadcast), just spectators (spectator) or a specific player (private)",
        },
        "stateid": {"type": "string", "title": "Room ID", "pattern": "^([a-z0-9-]*)$"},
        "epoch": {
            "type": "integer",
            "title": "Game Step",
            "description": "The number of previous state changes in the game",
        },
        "board": {
            "type": "object",
            "title": "Board State",
            "description": "An arbitrary representation of the board",
        },
        "turn": {
            "anyOf": [
                {"type": "null"},
                {
                    "type": "string",
                    "title": "Player ID",
                    "description": "Player who is next to move",
                    "pattern": "^([a-z0-9-]*)$",
                },
            ]
        },
    },
    "additionalProperties": False,
}
move_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["move", "playerid", "roomid"],
    "properties": {
        "playerid": {
            "type": "string",
            "title": "Player ID",
            "description": "Player who is making a move",
            "pattern": "^([a-z0-9-]*)$",
        },
        "move": {
            "type": "object",
            "title": "Player Move",
            "description": "An arbitrary representation of the player's move",
        },
        "roomid": {"type": "string", "title": "Room ID", "pattern": "^([a-z0-9-]*)$"},
    },
    "additionalProperties": False,
}
finish_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["normal", "scores", "roomid"],
    "properties": {
        "normal": {
            "type": "boolean",
            "title": "Normal Finish",
            "description": "Whether the game finished normally through gameplay (as opposed to through an error)",
            "pattern": "^([a-z0-9-]*)$",
        },
        "scores": {
            "type": "object",
            "title": "Player Move",
            "description": "An arbitrary representation of the player's move",
            "propertyNames": {"pattern": "^([a-z0-9-]*)$"},
            "additionalProperties": {"type": "integer", "minimum": -1, "maximum": 1},
        },
        "roomid": {"type": "string", "title": "Room ID", "pattern": "^([a-z0-9-]*)$"},
    },
    "additionalProperties": False,
}
