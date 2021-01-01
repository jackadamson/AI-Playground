import logging
from secrets import token_hex
from typing import Optional, List

from fastapi import Depends, APIRouter, Response, Cookie, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from starlette import status

from aiplayground.logging import logger
from redorm import InstanceNotFound
from redorm.exceptions import UniqueContstraintViolation

from aiplayground.api.auth.models import User, Role
from aiplayground.api.auth.schemas import AuthSchema, RegisterSchema
from aiplayground.settings import settings

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


def set_tokens(response: Response, user: User, extra_scopes: List[str] = None) -> dict:
    if extra_scopes is None:
        extra_scopes = []
    access_token = user.create_token(extra_scopes=extra_scopes, expires_delta=settings.ACCESS_TOKEN_EXPIRES)
    refresh_token = user.create_token(expires_delta=settings.REFRESH_TOKEN_EXPIRES, refresh=True)
    # TODO: Add Cookie URL to refresh_token
    response.set_cookie(
        "refresh_token", value=refresh_token, max_age=int(settings.REFRESH_TOKEN_EXPIRES.total_seconds()), httponly=True
    )
    return {"success": True, "access_token": access_token}


@auth_router.post("/login", response_model=AuthSchema)
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = User.get(email=form_data.username)
    except InstanceNotFound:
        logging.info("Login with incorrect email: %s", form_data.username)
        return {"success": False, "message": "Incorrect email or password"}
    if user.guest or not user.check_password(password=form_data.password):
        logging.info("Login with incorrect password: %s", form_data.username)
        return {"success": False, "message": "Incorrect email or password"}
    if not user.verified:
        return {"success": False, "message": "User not activated"}
    return set_tokens(response, user, extra_scopes=["fresh"])


@auth_router.post("/register", response_model=AuthSchema)
def register(response: Response, registration: RegisterSchema):
    try:
        user = User.create(username=registration.username, email=registration.email, password=registration.password)
    except UniqueContstraintViolation as e:
        logging.error(f"Registration failed with email {registration.email}")
        logging.error(e)
        return {"success": False, "message": "Email or username already in use"}
    if user.verified:
        return set_tokens(response, user, extra_scopes=["fresh"])
    return {"success": True, "message": "User created, awaiting approval"}


@auth_router.post("/guest", response_model=AuthSchema)
def guest_login(response: Response):
    guest_id = token_hex(6)
    username = f"Guest-{guest_id}"
    user: User = User.create(username=username, email=f"guest{guest_id}@guest", verified=False)
    guest_role = Role.get(name="guest")
    user.update(roles=[guest_role])
    return set_tokens(response, user, extra_scopes=["fresh"])


@auth_router.post("/refresh", response_model=AuthSchema)
def refresh(response: Response, refresh_token: Optional[str] = Cookie(None)):
    if refresh_token is None:
        logger.debug("No refresh token")
        return {"success": False}
    try:
        claims = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        if claims["type"] != "refresh":
            logger.warning("Attempted refresh with not refresh token")
            return {"success": False}
        try:
            user = User.get(claims["sub"])
            return set_tokens(response, user)
        except InstanceNotFound:
            logger.warning(f"User from refresh token not found: {claims['sub']}")
            return {"success": False}
    except JWTError as e:
        logger.warning(f"JWT Error in refresh token: {e!r}")
        return {"success": False}


@auth_router.post("/logout", response_model=AuthSchema)
def refresh(response: Response):
    response.set_cookie("refresh_token", value="", max_age=0, httponly=True)
    return {"success": True}


# @auth_api.route("/me")
# class Me(Resource):
#     @auth_api.doc(security="bearertoken")
#     @auth_api.marshal_with(user_schema)
#     @require_auth
#     def get(self):
#         """
#         Create new access token
#         """
#         current_user = get_jwt_identity()
#         return User.get(current_user)
#
#
# @auth_api.route("/logout")
# class Logout(Resource):
#     def post(self):
#         """
#         Removes access and refresh tokens
#         """
#         resp = jsonify({"logout": True})
#         unset_jwt_cookies(resp)
#         return resp
