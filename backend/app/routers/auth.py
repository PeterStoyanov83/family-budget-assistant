from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select

from app.core.database import get_session
from app.core.deps import CurrentUser, SessionDep
from app.core.security import (clear_auth_cookies, get_user_id_from_request,
                                hash_password, set_auth_cookies, verify_password)
from app.models.user import User
from app.schemas.auth import LoginRequest, MessageResponse, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, response: Response, session: SessionDep):
    existing = await session.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        household_size=body.household_size,
        city=body.city,
        has_car=body.has_car,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    set_auth_cookies(response, user.id)
    return user


@router.post("/login", response_model=UserResponse)
async def login(body: LoginRequest, response: Response, session: SessionDep):
    result = await session.execute(
        select(User).where(User.email == body.email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    set_auth_cookies(response, user.id)
    return user


@router.post("/refresh", response_model=UserResponse)
async def refresh(request: Request, response: Response, session: SessionDep):
    user_id = get_user_id_from_request(request, token_type="refresh")
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    set_auth_cookies(response, user.id)
    return user


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.delete("/account", response_model=MessageResponse)
async def delete_account(current_user: CurrentUser, session: SessionDep):
    # GDPR: soft delete — personal data anonymized within 30 days via Celery task
    current_user.deleted_at = datetime.now(timezone.utc)
    current_user.is_active = False
    await session.commit()
    return {"message": "Account scheduled for deletion within 30 days"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user


@router.get("/gdpr/export")
async def gdpr_export(current_user: CurrentUser, session: SessionDep):
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.shopping_list import ShoppingList
    from app.models.price import PurchaseHistory

    lists_result = await session.execute(
        select(ShoppingList)
        .options(selectinload(ShoppingList.items))
        .where(ShoppingList.user_id == current_user.id)
    )
    lists = lists_result.scalars().all()

    history_result = await session.execute(
        select(PurchaseHistory).where(PurchaseHistory.user_id == current_user.id)
    )
    history = history_result.scalars().all()

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "household_size": current_user.household_size,
            "plan": current_user.plan,
            "city": current_user.city,
            "has_car": current_user.has_car,
            "created_at": current_user.created_at.isoformat(),
        },
        "shopping_lists": [
            {
                "id": sl.id,
                "name": sl.name,
                "budget": sl.budget,
                "status": sl.status,
                "created_at": sl.created_at.isoformat(),
                "items": [{"name": i.name, "quantity": i.quantity} for i in sl.items],
            }
            for sl in lists
        ],
        "purchase_history": [
            {
                "product_id": ph.product_id,
                "store_id": ph.store_id,
                "price_paid": ph.price_paid,
                "quantity": ph.quantity,
                "purchased_at": ph.purchased_at.isoformat(),
            }
            for ph in history
        ],
    }
