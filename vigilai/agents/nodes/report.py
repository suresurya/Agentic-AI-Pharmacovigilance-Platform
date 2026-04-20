import os
import sys
import asyncio
from agents.state import AgentState

# Add backend to path so we can use app models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../backend"))


def report_node(state: AgentState) -> AgentState:
    """Write ADR reports to MongoDB via motor (sync wrapper around async)."""
    narrative_id = state["narrative_id"]
    normalized_pairs = state.get("normalized_pairs", [])

    if not normalized_pairs:
        return {**state, "report_id": None}

    try:
        report_ids = asyncio.run(_write_reports(narrative_id, normalized_pairs))
        return {**state, "report_id": report_ids[0] if report_ids else None}
    except RuntimeError:
        # If event loop already running (inside FastAPI), use a thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, _write_reports(narrative_id, normalized_pairs))
            report_ids = future.result()
        return {**state, "report_id": report_ids[0] if report_ids else None}


async def _write_reports(narrative_id: str, pairs: list[dict]) -> list[str]:
    from motor.motor_asyncio import AsyncIOMotorClient
    import json

    mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db = os.environ.get("MONGODB_DB", "vigilai")

    client = AsyncIOMotorClient(mongodb_url)
    db = client[mongodb_db]
    collection = db["adr_reports"]

    report_ids = []
    for pair in pairs:
        doc = {
            "narrative_id": narrative_id,
            "relation_type": pair.get("relation_type", "Causes-ADR"),
            "confidence": pair.get("confidence", 0.5),
            "evidence": pair.get("evidence", {}),
            "normalized_term": pair.get("normalized_term"),
            "whoart_code": pair.get("whoart_code"),
            "officer_status": "pending",
        }
        result = await collection.insert_one(doc)
        report_ids.append(str(result.inserted_id))

    client.close()
    return report_ids
