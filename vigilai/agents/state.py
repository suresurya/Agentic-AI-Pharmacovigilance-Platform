from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    narrative_id: str
    raw_text: str
    clean_text: str | None
    language_mix_ratio: float
    entities: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    normalized_pairs: list[dict[str, Any]]
    report_id: str | None
    hitl_required: bool
    hitl_candidates: list[dict[str, Any]]
    hitl_pending_report_id: str | None
    hitl_selection: dict[str, Any] | None
    ws_narrative_id: str
