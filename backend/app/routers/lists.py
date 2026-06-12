from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, SessionDep
from app.models.shopping_list import ListItem, ShoppingList
from app.schemas.shopping_list import (ListItemCreate, ListItemOut, ListItemUpdate,
                                        ShoppingListCreate, ShoppingListOut,
                                        ShoppingListSummary, ShoppingListUpdate)

router = APIRouter(prefix="/lists", tags=["lists"])


@router.get("", response_model=list[ShoppingListSummary])
async def get_lists(session: SessionDep, current_user: CurrentUser):
    result = await session.execute(
        select(ShoppingList)
        .where(ShoppingList.user_id == current_user.id, ShoppingList.deleted_at.is_(None))
        .order_by(ShoppingList.updated_at.desc())
    )
    lists = result.scalars().all()
    return [
        ShoppingListSummary(
            id=sl.id,
            name=sl.name,
            budget=sl.budget,
            status=sl.status,
            item_count=0,  # loaded lazily — not needed for list view
            created_at=sl.created_at,
        )
        for sl in lists
    ]


@router.post("", response_model=ShoppingListOut, status_code=status.HTTP_201_CREATED)
async def create_list(body: ShoppingListCreate, session: SessionDep, current_user: CurrentUser):
    sl = ShoppingList(user_id=current_user.id, name=body.name, budget=body.budget)
    session.add(sl)
    await session.commit()
    await session.refresh(sl)
    return sl


@router.get("/{list_id}", response_model=ShoppingListOut)
async def get_list(list_id: int, session: SessionDep, current_user: CurrentUser):
    sl = await _get_owned_list(list_id, current_user.id, session)
    return sl


@router.patch("/{list_id}", response_model=ShoppingListOut)
async def update_list(
    list_id: int, body: ShoppingListUpdate, session: SessionDep, current_user: CurrentUser
):
    sl = await _get_owned_list(list_id, current_user.id, session)
    if body.name is not None:
        sl.name = body.name
    if body.budget is not None:
        sl.budget = body.budget
    if body.status is not None:
        sl.status = body.status
    await session.commit()
    await session.refresh(sl)
    return sl


@router.delete("/{list_id}", response_model=dict)
async def delete_list(list_id: int, session: SessionDep, current_user: CurrentUser):
    sl = await _get_owned_list(list_id, current_user.id, session)
    sl.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return {"message": "List deleted"}


@router.post("/{list_id}/items", response_model=ListItemOut, status_code=status.HTTP_201_CREATED)
async def add_item(
    list_id: int, body: ListItemCreate, session: SessionDep, current_user: CurrentUser
):
    await _get_owned_list(list_id, current_user.id, session)
    item = ListItem(list_id=list_id, **body.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.patch("/{list_id}/items/{item_id}", response_model=ListItemOut)
async def update_item(
    list_id: int, item_id: int, body: ListItemUpdate,
    session: SessionDep, current_user: CurrentUser,
):
    await _get_owned_list(list_id, current_user.id, session)
    item = await session.get(ListItem, item_id)
    if not item or item.list_id != list_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    await session.commit()
    await session.refresh(item)
    return item


@router.delete("/{list_id}/items/{item_id}", response_model=dict)
async def delete_item(
    list_id: int, item_id: int, session: SessionDep, current_user: CurrentUser
):
    await _get_owned_list(list_id, current_user.id, session)
    item = await session.get(ListItem, item_id)
    if not item or item.list_id != list_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    await session.delete(item)
    await session.commit()
    return {"message": "Item deleted"}


async def _get_owned_list(list_id: int, user_id: int, session: SessionDep) -> ShoppingList:
    result = await session.execute(
        select(ShoppingList)
        .options(selectinload(ShoppingList.items))
        .where(ShoppingList.id == list_id, ShoppingList.user_id == user_id,
               ShoppingList.deleted_at.is_(None))
    )
    sl = result.scalar_one_or_none()
    if not sl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    return sl
