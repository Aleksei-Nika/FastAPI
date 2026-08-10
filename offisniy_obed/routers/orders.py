from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import List
from crud import add_order_item, delete_order_item
from schemas import OrderItemCreate, OrderItemResponse

router = APIRouter(prefix='/orders', tags=['Формирование корзины заказа'])

# POST /orders
@router.post('/', response_model=OrderItemResponse, status_code=201)
async def add_item_to_order(
    data: OrderItemCreate,
    db: AsyncSession = Depends(get_db)
):
    order_item = await add_order_item(db, data)
    from crud import get_menu_item_by_id
    menu_item = await get_menu_item_by_id(db, order_item.menu_item_id)
    return {
        'id': order_item.id,
        'user_id': order_item.user_id,
        'menu_item_id': order_item.menu_item_id,
        'quantity': order_item.quantity,
        'name': menu_item.name,
        'price': menu_item.price
    }
    
# DELETE /orders/{order_item_id}
@router.delete('/{order_item_id}')
async def remove_item_from_order(
    order_item_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await delete_order_item(db, order_item_id)
    return result