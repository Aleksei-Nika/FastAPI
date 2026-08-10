from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum 
from database import Base
from datetime import datetime

class SessionStatus(str, enum.Enum):
    active = 'active'
    ordered = 'ordered'
    delivered = 'delivered'
    cancelled = 'cancelled'

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(String,unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String,unique=True, nullable=False)

    # связи
    created_sessions: Mapped[list['Session']] = relationship('Session', back_populates='creator')
    order_items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='user')

class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    restaurant_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[SessionStatus] = mapped_column(SQLEnum(SessionStatus), default=SessionStatus.active, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # связи
    creator: Mapped['User'] = relationship('User', back_populates='created_sessions', lazy='selectin')
    menu_items: Mapped[list["MenuItem"]] = relationship('MenuItem', back_populates='session', lazy='selectin')

class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey('sessions.id'), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Numeric, nullable=False)

    # связи
    session: Mapped['Session'] = relationship('Session', back_populates='menu_items')
    order_items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='menu_item')

class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    menu_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('menu_items.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # связи
    user: Mapped['User'] = relationship('User', back_populates='order_items')
    menu_item: Mapped['MenuItem'] = relationship('MenuItem', back_populates='order_items')