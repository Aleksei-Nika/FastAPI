from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional, List

class SessionStatus(str, Enum):
    active = 'active'
    ordered = 'ordered'
    delivered = 'delivered'
    cancelled = 'cancelled'


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description='Имя или никнейм пользователя')
    email: EmailStr = Field(..., description='Электронная почта пользователя')

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    creator_id: int = Field(..., description='ID пользователя, организующего сбор')
    restaurant_name: str = Field(..., min_length=1, description='Название ресторана')
    deadline: datetime = Field(..., description='Крайний срок приема заказов')

class SessionStatusUpdate(BaseModel):
    status: SessionStatus = Field(..., description='Новый статус сессии')

class MenuItemRestaurant(BaseModel):
    id: int
    name: str 
    price: float
    model_config = ConfigDict(from_attributes=True)

class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, description='Название блюда')
    price: float = Field(..., gt=0, description='Цена блюда')

class SessionRespone(BaseModel):
    id: int
    creator_id: int 
    restaurant_name: str 
    status: SessionStatus
    created_at: datetime
    deadline: datetime 
    menu_items: List[MenuItemRestaurant] = []
    model_config = ConfigDict(from_attributes=True)

class OrderItemCreate(BaseModel):
    user_id: int = Field(..., description='ID пользователя')
    menu_item_id: int = Field(..., description='ID блюда из меню')
    quantity: int = Field(default=1, gt=0, description='Количество порций')

class OrderItemResponse(BaseModel):
    id: int 
    user_id: int 
    menu_item_id: int 
    quantity: int 
    name: Optional[str] = None
    price: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class SummaryMenuItem(BaseModel):
    name: str 
    total_quantity: int
    price: float 
    total_price: float 

class UserSplit(BaseModel):
    user_id: int 
    username: str 
    items: List[OrderItemResponse]
    total: float

class SessionSummary(BaseModel):
    session_id: int 
    restaurant_name: str 
    status: SessionStatus
    grand_total: float 
    restaurant_order: List[SummaryMenuItem]
    split_check: List[UserSplit]