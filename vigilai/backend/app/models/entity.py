from typing import Optional
from beanie import Document
from pydantic import Field
from bson import ObjectId


class Entity(Document):
    narrative_id: str
    entity_text: str
    entity_type: str  # drug | symptom | dosage
    char_start: int
    char_end: int
    confidence: float
    source_model: str = "rule-based"

    class Settings:
        name = "entities"
