from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from routers import users 


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield 

app = FastAPI(
    title='Офисный обед API',
    description='RESTful API для совместного заказа еды внутри закрытых групп',
    version='1.0.0',
    lifespan=lifespan
)

app.include_router(users.router)