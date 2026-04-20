from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Any


class EvidenceObject(BaseModel):
    drug_span: str | None = None
    reaction_span: str | None = None
    temporal_marker: str | None = None
    temporal_marker_translation: str | None = None
    causal_pattern: str | None = None
    negation_detected: bool = False
    plain_language_reason: str | None = None


class ReportOut(BaseModel):
    id: UUID
    narrative_id: UUID
    drug_entity_id: UUID | None
    symptom_entity_id: UUID | None
    relation_type: str
    confidence: float
    evidence: dict[str, Any] | None
    normalized_term: str | None
    whoart_code: str | None
    officer_status: str
    officer_notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportReviewRequest(BaseModel):
    action: Literal["approve", "reject", "modify_term", "modify_relation"]
    notes: str | None = None
    corrected_term: str | None = None
    corrected_whoart_code: str | None = None
    corrected_relation: str | None = None
