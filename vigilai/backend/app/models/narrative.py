from datetime import datetime, timezone
from typing import Optional
from beanie import Document
from pydantic import Field


class Narrative(Document):
    source_text: str
    source_type: str = "manual"
    customer_id: Optional[str] = None
    language_mix_ratio: Optional[float] = None
    status: str = "queued"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "narratives"
