import uuid
from datetime import datetime
from sqlalchemy import String, Text, Numeric, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(300), nullable=True)

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    offer_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    available: Mapped[bool] = mapped_column(Boolean, default=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)

    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    category = relationship("Category", back_populates="dishes")
