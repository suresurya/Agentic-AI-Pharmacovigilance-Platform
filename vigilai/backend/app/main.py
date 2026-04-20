from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.websocket.manager import ws_manager
from app.api import narratives, reports, hitl, whoart, auth

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}. Server will continue without database.")
    yield


app = FastAPI(
    title="VigilAI 2.0",
    description="Hinglish Pharmacovigilance Intelligence Platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(narratives.router)
app.include_router(reports.router)
app.include_router(hitl.router)
app.include_router(whoart.router)


@app.websocket("/ws/pipeline/{narrative_id}")
async def websocket_pipeline(websocket: WebSocket, narrative_id: str):
    await ws_manager.connect(narrative_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(narrative_id, websocket)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "VigilAI 2.0"}
