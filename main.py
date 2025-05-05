from fastapi import FastAPI
from app.controller.routes import user, websocket
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router, prefix="/api/users", tags=["users"])
app.include_router(websocket.router, prefix="api/ws", tags=["websocker"])
