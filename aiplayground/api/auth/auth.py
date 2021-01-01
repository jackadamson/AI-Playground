from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt

from aiplayground.logging import logger
from aiplayground.settings import settings
from aiplayground.api.auth.schemas import TokenSchema, TokenType
from aiplayground.types import UserId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_claims(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    try:
        claims = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        token = TokenSchema.parse_obj(claims)
        if token.type != TokenType.access:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires access token")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
    logger.debug(f"Required scope: {security_scopes.scopes}, Token Scopes: {token.scopes}")
    for scope in security_scopes.scopes:
        if scope not in token.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return claims


def get_user_id(claims: dict = Depends(get_claims)) -> UserId:
    return claims["sub"]
