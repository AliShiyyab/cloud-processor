from fastapi import FastAPI

from app.controller.routes import user, websocket, resources, logs, attacks, countermeasures
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(user.router, prefix="/api/users", tags=["users"])
app.include_router(websocket.router, prefix="/api/ws", tags=["websocker"])

app.include_router(resources.router, prefix="/api/resources", tags=["resources"])

app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(attacks.router, prefix="/api/attacks", tags=["attacks"])
app.include_router(countermeasures.router, prefix="/api/countermeasures", tags=["countermeasures"])
