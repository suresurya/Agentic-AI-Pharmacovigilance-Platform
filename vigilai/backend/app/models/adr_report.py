from datetime import datetime, timezone
from typing import Optional, Any
from beanie import Document
from pydantic import Field


class ADRReport(Document):
    narrative_id: str
    drug_entity_id: Optional[str] = None
    symptom_entity_id: Optional[str] = None
    relation_type: str  # Causes-ADR | Possible-ADR
    confidence: float
    evidence: Optional[dict[str, Any]] = None
    normalized_term: Optional[str] = None
    whoart_code: Optional[str] = None
    officer_status: str = "pending"  # pending | approved | rejected | modified
    officer_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "adr_reports"
