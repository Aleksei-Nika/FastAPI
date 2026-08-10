from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from routers import users, session, menu, orders, summary
from fastapi.middleware.cors import CORSMiddleware


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

app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        '*'
    ],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

app.include_router(users.router)
app.include_router(session.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(summary.router)

@app.get('/', tags=['Служебное'])
async def root():
    return {'message': 'Добро пожаловать в сервис "Офисный обед"'}
