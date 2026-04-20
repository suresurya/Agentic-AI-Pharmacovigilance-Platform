from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Any, Optional


class EvidenceObject(BaseModel):
    drug_span: Optional[str] = None
    reaction_span: Optional[str] = None
    temporal_marker: Optional[str] = None
    temporal_marker_translation: Optional[str] = None
    causal_pattern: Optional[str] = None
    negation_detected: bool = False
    plain_language_reason: Optional[str] = None


class ReportOut(BaseModel):
    id: str
    narrative_id: str
    drug_entity_id: Optional[str] = None
    symptom_entity_id: Optional[str] = None
    relation_type: str
    confidence: float
    evidence: Optional[dict[str, Any]] = None
    normalized_term: Optional[str] = None
    whoart_code: Optional[str] = None
    officer_status: str
    officer_notes: Optional[str] = None
    created_at: datetime


class ReportReviewRequest(BaseModel):
    action: Literal["approve", "reject", "modify_term", "modify_relation"]
    notes: Optional[str] = None
    corrected_term: Optional[str] = None
    corrected_whoart_code: Optional[str] = None
    corrected_relation: Optional[str] = None
