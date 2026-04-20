import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class OfficerAction(Base):
    __tablename__ = "officer_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("adr_reports.id", ondelete="CASCADE"))
    action_type: Mapped[str] = mapped_column(
        Enum("approve", "reject", "modify_term", "modify_relation", name="action_type_enum"),
        nullable=False,
    )
    original_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    corrected_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    officer_id: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    report: Mapped["ADRReport"] = relationship("ADRReport", back_populates="officer_actions")
