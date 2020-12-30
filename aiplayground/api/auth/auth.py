from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from aiplayground.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_claims(token: str = Depends(oauth2_scheme)):
    try:
        claims = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        if claims["type"] != "access":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires access token")
        return claims
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id(claims: dict = Depends(get_claims)):
    return claims["sub"]
