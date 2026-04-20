from uuid import UUID
from pydantic import BaseModel
from typing import Literal


class EntityOut(BaseModel):
    id: UUID
    narrative_id: UUID
    entity_text: str
    entity_type: Literal["drug", "symptom", "dosage"]
    char_start: int
    char_end: int
    confidence: float
    source_model: str

    model_config = {"from_attributes": True}
