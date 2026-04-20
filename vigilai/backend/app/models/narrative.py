import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Enum, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Narrative(Base):
    __tablename__ = "narratives"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(
        Enum("manual", "csv_batch", "api_webhook", "patient_portal", name="source_type_enum"),
        default="manual",
    )
    customer_id: Mapped[str] = mapped_column(String(100), nullable=True)
    language_mix_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("queued", "processing", "pending_review", "done", "failed", name="narrative_status_enum"),
        default="queued",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    entities: Mapped[list["Entity"]] = relationship("Entity", back_populates="narrative", cascade="all, delete-orphan")
    reports: Mapped[list["ADRReport"]] = relationship("ADRReport", back_populates="narrative", cascade="all, delete-orphan")
