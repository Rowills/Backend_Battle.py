from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[int, List[WebSocket]] = {}
        self.names: Dict[WebSocket, str] = {}

    async def connect(self, battle_id: int, websocket: WebSocket):
        await websocket.accept()
        if battle_id not in self.rooms:
            self.rooms[battle_id] = []
        self.rooms[battle_id].append(websocket)

    async def disconnect(self, battle_id: int, websocket: WebSocket):
        if battle_id in self.rooms:
            self.rooms[battle_id].remove(websocket)
            if websocket in self.names:
                del self.names[websocket]
            await self.broadcast_to_all(battle_id, "OPPONENT_DISCONNECTED")

    def set_name(self, battle_id: int, websocket: WebSocket, name: str):
        self.names[websocket] = name

    def get_all_names(self, battle_id: int, exclude: WebSocket) -> List[str]:
        if battle_id not in self.rooms:
            return []
        return [self.names[ws] for ws in self.rooms[battle_id] if ws != exclude and ws in self.names]

    def get_room_size(self, battle_id: int) -> int:
        return len(self.rooms.get(battle_id, []))

    async def broadcast(self, battle_id: int, message: str, sender: WebSocket):
        if battle_id in self.rooms:
            for connection in self.rooms[battle_id]:
                if connection != sender:
                    await connection.send_text(message)

    async def broadcast_to_all(self, battle_id: int, message: str):
        if battle_id in self.rooms:
            for connection in self.rooms[battle_id]:
                await connection.send_text(message)

manager = ConnectionManager()
