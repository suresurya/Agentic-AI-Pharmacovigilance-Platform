from pydantic import BaseModel
from typing import Literal


class EntityOut(BaseModel):
    id: str
    narrative_id: str
    entity_text: str
    entity_type: Literal["drug", "symptom", "dosage"]
    char_start: int
    char_end: int
    confidence: float
    source_model: str
