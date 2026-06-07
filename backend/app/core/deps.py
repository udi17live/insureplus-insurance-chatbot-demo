from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repository.user import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def _get_user_from_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    token: str | None = None

    # 1. Bearer header (forwarded from Next.js)
    if credentials:
        token = credentials.credentials

    # 2. HttpOnly cookie fallback for direct calls
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub", "")
        if not user_id:
            return None
    except JWTError:
        return None

    repo = UserRepository(db)
    return await repo.get_by_id(user_id)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user = await _get_user_from_request(request, credentials, db)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_optional_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    user = await _get_user_from_request(request, credentials, db)
    if user and not user.is_active:
        return None
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def verify_agent_key(request: Request) -> None:
    key = request.headers.get("x-api-key", "") or request.headers.get("x-agent-key", "")
    if not key or key != settings.agent_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid agent key")


AgentAuth = Annotated[None, Depends(verify_agent_key)]
