from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import List 
from crud import add_menu_item
from schemas import MenuItemCreate, MenuItemRestaurant

router = APIRouter(tags=['Управление меню сессии'])

# POST /sessions/{session_id}/menu

@router.post(
    '/sessions/{session_id}/menu',
    response_model=List[MenuItemRestaurant],
    status_code=201,
)
async def add_menu(
    session_id: int,
    items: List[MenuItemCreate],
    db: AsyncSession = Depends(get_db),
):
    created_items = await add_menu_item(db, session_id, items)
    return created_items