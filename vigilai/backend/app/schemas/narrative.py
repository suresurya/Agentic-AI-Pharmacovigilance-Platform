from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional


class NarrativeCreate(BaseModel):
    source_text: str = Field(..., min_length=10, max_length=5000)
    source_type: Literal["manual", "csv_batch", "api_webhook", "patient_portal"] = "manual"
    customer_id: Optional[str] = None


class NarrativeResponse(BaseModel):
    id: str
    source_text: str
    source_type: str
    language_mix_ratio: Optional[float] = None
    status: str
    created_at: datetime


class NarrativeStatus(BaseModel):
    id: str
    status: str
    created_at: datetime
