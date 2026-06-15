from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Response, Request, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

COOKIE_ACCESS = "access_token"
COOKIE_REFRESH = "refresh_token"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_access_token(user_id: int) -> str:
    return _create_token({"sub": str(user_id), "type": "access"},
                         timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(user_id: int) -> str:
    return _create_token({"sub": str(user_id), "type": "refresh"},
                         timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")


def set_auth_cookies(response: Response, user_id: int) -> None:
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    _set_cookie(response, COOKIE_ACCESS, access,
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    _set_cookie(response, COOKIE_REFRESH, refresh,
                max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400)


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(COOKIE_ACCESS)
    response.delete_cookie(COOKIE_REFRESH)


def _set_cookie(response: Response, name: str, value: str, max_age: int) -> None:
    is_prod = settings.environment != "development"
    response.set_cookie(
        key=name,
        value=value,
        max_age=max_age,
        httponly=True,
        secure=is_prod,
        # SameSite=None required for cross-origin AJAX (frontend/backend on separate Railway subdomains)
        # SameSite=Strict is safe for local dev where both run on localhost
        samesite="none" if is_prod else "strict",
    )


def get_user_id_from_request(request: Request, token_type: str = "access") -> int:
    cookie_name = COOKIE_ACCESS if token_type == "access" else COOKIE_REFRESH
    token = request.cookies.get(cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    payload = decode_token(token)
    if payload.get("type") != token_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token type")
    return int(payload["sub"])
