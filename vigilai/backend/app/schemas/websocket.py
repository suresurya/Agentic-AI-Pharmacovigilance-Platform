from pydantic import BaseModel
from typing import Any


class WSNodeComplete(BaseModel):
    event: str = "node_complete"
    node: str
    status: str
    output_preview: str | None = None
    timestamp: str
    next_node: str | None = None


class WSHITLRequired(BaseModel):
    event: str = "hitl_required"
    node: str = "Normalize"
    report_id: str
    candidates: list[dict[str, Any]]
    message: str = "Confidence below threshold. Officer selection required."


class WSPipelineError(BaseModel):
    event: str = "pipeline_error"
    node: str
    error: str
    timestamp: str
