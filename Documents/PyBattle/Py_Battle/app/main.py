from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.routers import auth, battle, stats, comments
from app.websockets.battle_ws import manager

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Py_Battle",
    description="A real-time 1v1 python coding battle platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://pybattle.vercel.app",
        "https://pybattle-git-main-roy-flemings-projects.vercel.app",
        "https://pybattle-roy-flemings-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(battle.router)
app.include_router(stats.router)
app.include_router(comments.router)

@app.websocket("/ws/battle/{battle_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, battle_id: int, player_id: str):
    await manager.connect(battle_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("JOIN:"):
                name = data.replace("JOIN:", "")
                manager.set_name(battle_id, websocket, name)
                other_names = manager.get_all_names(battle_id, websocket)
                for n in other_names:
                    await websocket.send_text(f"JOIN:{n}")
                if manager.get_room_size(battle_id) >= 2:
                    for conn in manager.rooms[battle_id]:
                        others = manager.get_all_names(battle_id, conn)
                        for n in others:
                            await conn.send_text(f"JOIN:{n}")
                    await manager.broadcast_to_all(battle_id, "BATTLE_READY")
            elif data.startswith("CODE:"):
                await manager.broadcast(battle_id, data, sender=websocket)
            elif data.startswith("SUBMITTED:"):
                await manager.broadcast(battle_id, data, sender=websocket)
            else:
                await manager.broadcast(battle_id, data, sender=websocket)
                await websocket.send_text(f"you: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(battle_id, websocket)

@app.get("/")
def home():
    return {"message": "Battle API is Alive!"}
