from datetime import datetime, timezone
from typing import Optional, Any
from beanie import Document
from pydantic import Field


class OfficerAction(Document):
    report_id: str
    action_type: str  # approve | reject | modify_term | modify_relation
    original_value: Optional[dict[str, Any]] = None
    corrected_value: Optional[dict[str, Any]] = None
    officer_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "officer_actions"
