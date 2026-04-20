import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../agents"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../ml"))

from app.websocket.manager import ws_manager
from app.models.narrative import Narrative

_hitl_events: dict[str, asyncio.Event] = {}
_hitl_selections: dict[str, dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _update_status(narrative_id: str, status: str):
    narrative = await Narrative.get(narrative_id)
    if narrative:
        narrative.status = status
        await narrative.save()


async def run_pipeline(narrative_id: str, source_text: str):
    await _update_status(narrative_id, "processing")
    await ws_manager.send_to_narrative(narrative_id, {
        "event": "node_complete", "node": "Ingest", "status": "success",
        "output_preview": f"Narrative queued ({len(source_text)} chars)",
        "timestamp": _now(), "next_node": "Preprocess",
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

        result = await asyncio.to_thread(graph.invoke, initial_state, config)

        # Emit node complete events for each completed node
        for node in ["Preprocess", "NER", "Relation"]:
            await ws_manager.send_to_narrative(narrative_id, {
                "event": "node_complete", "node": node, "status": "success",
                "output_preview": _node_preview(node, result),
                "timestamp": _now(),
            })

        if result.get("hitl_required"):
            candidates = result.get("hitl_candidates", [])
            # Create a pending report to attach HITL to
            from app.models.adr_report import ADRReport
            pending_rel = result.get("hitl_pending_relation", {})
            report = ADRReport(
                narrative_id=narrative_id,
                relation_type=pending_rel.get("relation_type", "Causes-ADR"),
                confidence=pending_rel.get("confidence", 0.5),
                evidence=pending_rel.get("evidence"),
                officer_status="pending",
            )
            await report.insert()
            report_id = str(report.id)

            await ws_manager.send_to_narrative(narrative_id, {
                "event": "hitl_required", "node": "Normalize",
                "report_id": report_id,
                "candidates": candidates,
                "message": "Confidence below threshold. Officer selection required.",
            })

            event = asyncio.Event()
            _hitl_events[narrative_id] = event
            await event.wait()

            selection = _hitl_selections.pop(narrative_id, {})
            report.normalized_term = selection.get("selected_term")
            report.whoart_code = selection.get("selected_code")
            await report.save()

            await ws_manager.send_to_narrative(narrative_id, {
                "event": "node_complete", "node": "Normalize", "status": "success",
                "output_preview": f"WHO-ART: {report.normalized_term}",
                "timestamp": _now(), "next_node": "Report",
            })
        else:
            await ws_manager.send_to_narrative(narrative_id, {
                "event": "node_complete", "node": "Normalize", "status": "success",
                "output_preview": _node_preview("Normalize", result),
                "timestamp": _now(), "next_node": "Report",
            })

        await ws_manager.send_to_narrative(narrative_id, {
            "event": "node_complete", "node": "Report", "status": "success",
            "output_preview": f"{len(result.get('normalized_pairs', []))} ADR report(s) generated",
            "timestamp": _now(),
        })

        await _update_status(narrative_id, "pending_review")
        await ws_manager.send_to_narrative(narrative_id, {
            "event": "pipeline_complete", "narrative_id": narrative_id, "timestamp": _now(),
        })

        # Update narrative language mix ratio
        narrative = await Narrative.get(narrative_id)
        if narrative:
            narrative.language_mix_ratio = result.get("language_mix_ratio", 0.0)
            await narrative.save()

    except Exception as e:
        await _update_status(narrative_id, "failed")
        await ws_manager.send_to_narrative(narrative_id, {
            "event": "pipeline_error", "error": str(e), "timestamp": _now(),
        })
        raise


def _node_preview(node: str, result: dict) -> str:
    if node == "Preprocess":
        return f"Cleaned text ({result.get('language_mix_ratio', 0)*100:.0f}% Hinglish)"
    if node == "NER":
        entities = result.get("entities", [])
        drugs = [e for e in entities if e.get("type") == "drug"]
        symptoms = [e for e in entities if e.get("type") == "symptom"]
        return f"Found: {len(drugs)} drug(s), {len(symptoms)} symptom(s)"
    if node == "Relation":
        rels = result.get("relations", [])
        return f"{len(rels)} ADR relation(s) extracted" if rels else "No ADR relations found"
    if node == "Normalize":
        pairs = result.get("normalized_pairs", [])
        if pairs:
            return f"WHO-ART: {pairs[0].get('normalized_term', 'mapped')}"
        return "No terms to normalize"
    return ""


async def resume_pipeline(narrative_id: str, report_id: str, selection: dict):
    _hitl_selections[narrative_id] = selection
    event = _hitl_events.pop(narrative_id, None)
    if event:
        event.set()
