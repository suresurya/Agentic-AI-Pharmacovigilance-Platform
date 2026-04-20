import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../agents"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../ml"))

from app.websocket.manager import ws_manager
from app.database import AsyncSessionLocal
from app.models.narrative import Narrative
from sqlalchemy import select

# thread_id → asyncio.Event for HITL resume
_hitl_events: dict[str, asyncio.Event] = {}
_hitl_selections: dict[str, dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _update_narrative_status(narrative_id: str, status: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Narrative).where(Narrative.id == narrative_id))
        narrative = result.scalar_one_or_none()
        if narrative:
            narrative.status = status
            await db.commit()


async def run_pipeline(narrative_id: str, source_text: str):
    await _update_narrative_status(narrative_id, "processing")
    await ws_manager.send_to_narrative(narrative_id, {
        "event": "pipeline_started",
        "narrative_id": narrative_id,
        "timestamp": _now(),
    })

    try:
        from agents.graph import build_graph
        graph = build_graph()

        config = {"configurable": {"thread_id": narrative_id}}
        initial_state = {
            "narrative_id": narrative_id,
            "raw_text": source_text,
            "clean_text": None,
            "language_mix_ratio": 0.0,
            "entities": [],
            "relations": [],
            "normalized_pairs": [],
            "report_id": None,
            "hitl_required": False,
            "hitl_candidates": [],
            "hitl_pending_report_id": None,
            "ws_narrative_id": narrative_id,
        }

        # Run graph — may interrupt at Normalize node
        result = await asyncio.to_thread(graph.invoke, initial_state, config)

        if result.get("hitl_required"):
            # Graph paused — wait for officer resolution
            event = asyncio.Event()
            _hitl_events[narrative_id] = event
            await event.wait()

            # Resume with officer selection
            selection = _hitl_selections.pop(narrative_id, {})
            resume_state = {**result, "hitl_required": False, "hitl_selection": selection}
            await asyncio.to_thread(graph.invoke, resume_state, config)

        await _update_narrative_status(narrative_id, "pending_review")
        await ws_manager.send_to_narrative(narrative_id, {
            "event": "pipeline_complete",
            "narrative_id": narrative_id,
            "timestamp": _now(),
        })

    except Exception as e:
        await _update_narrative_status(narrative_id, "failed")
        await ws_manager.send_to_narrative(narrative_id, {
            "event": "pipeline_error",
            "error": str(e),
            "timestamp": _now(),
        })
        raise


async def resume_pipeline(narrative_id: str, report_id: str, selection: dict):
    _hitl_selections[narrative_id] = selection
    event = _hitl_events.pop(narrative_id, None)
    if event:
        event.set()
