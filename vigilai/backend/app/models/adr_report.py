import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Enum, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ADRReport(Base):
    __tablename__ = "adr_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    narrative_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("narratives.id", ondelete="CASCADE"))
    drug_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    symptom_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    relation_type: Mapped[str] = mapped_column(
        Enum("Causes-ADR", "Possible-ADR", name="relation_type_enum"), nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=True)
    normalized_term: Mapped[str | None] = mapped_column(String(300), nullable=True)
    whoart_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    officer_status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", "modified", name="officer_status_enum"),
        default="pending",
    )
    officer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    narrative: Mapped["Narrative"] = relationship("Narrative", back_populates="reports")
    officer_actions: Mapped[list["OfficerAction"]] = relationship("OfficerAction", back_populates="report", cascade="all, delete-orphan")
