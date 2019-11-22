from flask import Blueprint
from flask_restplus import Api
from flaskplusplus.auth import auth_api, all_schemas as auth_schemas
from aiplayground.api.rooms import rooms_api, all_schemas as rooms_schemas
from aiplayground.api.players import players_api, all_schemas as players_schemas

authorizations = {
    "basicauth": {"type": "basic"},
    "bearertoken": {"type": "apiKey", "in": "header", "name": "Authorization"},
}
blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(
    blueprint,
    title="Asimov's Playground",
    version="0.1.0",
    description="A tournament server for AI agents to play board games",
    authorizations=authorizations,
    security=["bearertoken"],
    base_url="/api/v1",
)
for schema in auth_schemas + players_schemas + rooms_schemas:
    api.models[schema.name] = schema
api.add_namespace(auth_api, "/auth")
api.add_namespace(rooms_api, "/rooms")
api.add_namespace(players_api, "/players")
