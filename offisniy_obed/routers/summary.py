from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func 
from database import get_db 
from crud import get_session_by_id
from models import Session, MenuItem, OrderItem, User
from schemas import SessionSummary, SummaryMenuItem, UserSplit, OrderItemResponse

router = APIRouter(tags=['Агрегационные отчеты'])

# GET /sessions/{session_id}/summary
@router.get('/sessions/{session_id}/summary', response_model=SessionSummary)
async def get_session_summary(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_by_id(db, session_id)

# Сгруппированный список блюд для ресторана

# SELECT menu_items.name, menu_items.price, 
#        SUM(order_items.quantity) as total_quantity,
#        SUM(order_items.quantity * menu_items.price) as total_price
# FROM order_items
# JOIN menu_items ON order_items.menu_item_id = menu_items.id
# WHERE menu_items.session_id = :session_id 
# GROUP BY menu_items.id  
    restaurant_query = (
        select(
            MenuItem.name,
            MenuItem.price,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.quantity * MenuItem.price).label('total_price')
        )
        .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
        .where(MenuItem.session_id == session_id)
        .group_by(MenuItem.id, MenuItem.name, MenuItem.price)
    )
    result = await db.execute(restaurant_query)
    restaurant_rows = result.all()
    restaurant_order = [
        SummaryMenuItem(
            name=row.name,
            total_quantity=row.total_quantity,
            price=row.price,
            total_price=row.total_price,
        )
        for row in restaurant_rows
    ]
    # Общая стоимость заказа
    total_query = (
        select(func.sum(OrderItem.quantity * MenuItem.price))
        .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
        .where(MenuItem.session_id == session_id) 
    )
    total_result = await db.execute(total_query)
    grand_total = total_result.scalar() or 0

    split_query = (
        select(
            User.id.label('user_id'),
            User.username,
            OrderItem.id.label('order_item_id'),
            OrderItem.quantity,
            MenuItem.id.label('menu_item_id'),
            MenuItem.name,
            MenuItem.price,
        )
        .join(User, OrderItem.user_id == User.id)
        .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
        .where(MenuItem.session_id == session_id)
        .group_by(User.id)
    ) 
    split_result = await db.execute(split_query)
    split_rows = split_result.all()

    user_dict: dict[int, dict] = {}
    for row in split_rows:
        uid = row.user_id 
        if uid not in user_dict:
            user_dict[uid] = {
                'user_id': uid,
                'username': row.username,
                'items': [],
                'total': 0,
            }
        user_dict[uid]['items'].append(
            OrderItemResponse(
                id=row.order_item_id,
                user_id=uid,
                menu_item_id=row.menu_item_id,
                quantity=row.quantity,
                name=row.name,
                price=row.price
            )
        )
        user_dict[uid]['total'] += row.quantity * row.price
        
        split_check = [
            UserSplit(
                user_id = data['user_id'],
                username = data['username'],
                items = data['items'],
                total = data['total']
            )
            for data in user_dict.values()
        ]
        
        return SessionSummary(
            session_id = session.id,
            restaurant_name = session.restaurant_name,
            status = session.status,
            grand_total = grand_total,
            restaurant_order = restaurant_order,
            split_check = split_check
        )