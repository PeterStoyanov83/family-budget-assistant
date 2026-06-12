from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_user_id_from_request
from app.models.user import User

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(request: Request, session: SessionDep) -> User:
    user_id = get_user_id_from_request(request)
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
