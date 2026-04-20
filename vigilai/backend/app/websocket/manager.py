import json
from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, narrative_id: str, websocket: WebSocket):
        await websocket.accept()
        self._connections[narrative_id].append(websocket)

    def disconnect(self, narrative_id: str, websocket: WebSocket):
        self._connections[narrative_id].remove(websocket)
        if not self._connections[narrative_id]:
            del self._connections[narrative_id]

    async def send_to_narrative(self, narrative_id: str, event: dict):
        dead = []
        for ws in self._connections.get(narrative_id, []):
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections[narrative_id].remove(ws)

    async def broadcast(self, event: dict):
        for narrative_id in list(self._connections.keys()):
            await self.send_to_narrative(narrative_id, event)


ws_manager = ConnectionManager()
