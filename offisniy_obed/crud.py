from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import User, Session, MenuItem, OrderItem
from schemas import UserCreate, SessionCreate, MenuItemCreate, OrderItemCreate, SessionStatus
from fastapi import HTTPException 
from datetime import datetime

async def create_user(db: AsyncSession, user_data: UserCreate)->User:
    new_user = User(username=user_data.username, email=user_data.email)
    db.add(new_user)
    await db.flush() 
    await db.refresh(new_user)
    return new_user

async def get_all_users(db: AsyncSession)->list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f'Пользователь с id {user_id} не найден')
    return user 

async def create_session(db: AsyncSession, session_data: SessionCreate)->Session:
    if session_data.deadline <= datetime.now():
        raise HTTPException(status_code=400, detail='Дедлайн должен быть строго в будущем')
    await get_user_by_id(db, session_data.creator_id)
    new_session = Session(
        creator_id=session_data.creator_id,
        restaurant_name=session_data.restaurant_name,
        deadline=session_data.deadline,
        status=SessionStatus.active,
    )
    db.add(new_session)
    await db.flush()
    await db.refresh(new_session)
    return new_session

async def get_active_sessions(db: AsyncSession)->list[Session]:
    result = await db.execute(select(Session).where(Session.status == SessionStatus.active))
    return result.scalars().all()

async def get_session_by_id(db: AsyncSession, session_id: int) -> Session:
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=f'Сессия с id {session_id} не найдена')
    return session

async def update_session_status(db: AsyncSession, session_id: int, new_status: SessionStatus) -> Session:
    session = await get_session_by_id(db, session_id)
    if new_status == SessionStatus.ordered:
        result = await db.execute(
            select(func.count(OrderItem.id))
            .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
            .where(MenuItem.session_id == session_id)
        )
        orders_count = result.scalar()
        if orders_count == 0:
            raise HTTPException(status_code=400,
                                detail='В заказе нет ни одной позиции')
    session.status = new_status
    await db.flush()
    await db.refresh(session)
    return session