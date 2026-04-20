from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.database import Base


class WHOARTTerm(Base):
    __tablename__ = "whoart_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    term: Mapped[str] = mapped_column(String(300), nullable=False)
    system_organ_class: Mapped[str | None] = mapped_column(String(200), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
