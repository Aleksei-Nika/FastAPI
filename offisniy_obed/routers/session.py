from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import List
from crud import create_session, get_session_by_id, get_active_sessions, update_session_status
from schemas import SessionCreate, SessionRespone, SessionStatusUpdate
from sqlalchemy import select
from models import MenuItem

router = APIRouter(prefix="/session", tags=['Управление сессиями заказа'])

#POST /session
@router.post('/', response_model=SessionRespone, status_code=201)
async def create_new_session(session_data: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = await create_session(db, session_data)
    return session

#GET /sessions
@router.get('/', response_model=List[SessionRespone])
async def list_active_sessions(db: AsyncSession = Depends(get_db)):
    sessions = await get_active_sessions(db)
    return sessions 

# GET /sessions/{session_id}
@router.get('/{session_id}', response_model=SessionRespone)
async def get_session_detail(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await get_session_by_id(db, session_id)
    result = await db.execute(
        select(MenuItem).where(MenuItem.session_id == session_id)
    )
    session.menu_items = result.scalars().all()
    return session

# PATCH /sessions/{session_id}/status
@router.patch('/{session_id}/status', response_model=SessionRespone)
async def change_session_status(
    session_id: int,
    status_data: SessionStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    session = await update_session_status(db, session_id, status_data.status)
    result = await db.execute(
            select(MenuItem).where(MenuItem.session_id == session_id)
        )
    session.menu_items = result.scalars().all()
    return session

