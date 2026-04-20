from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class NarrativeCreate(BaseModel):
    source_text: str = Field(..., min_length=10, max_length=5000)
    source_type: Literal["manual", "csv_batch", "api_webhook", "patient_portal"] = "manual"
    customer_id: str | None = None


class NarrativeResponse(BaseModel):
    id: UUID
    source_text: str
    source_type: str
    language_mix_ratio: float | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NarrativeStatus(BaseModel):
    id: UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
