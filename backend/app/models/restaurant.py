# backend/app/models/restaurant.py

from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)  # URL en Object Storage
    phone = Column(String, nullable=True)
    horarios = Column(JSONB, nullable=True)  # ej: {"lunes": "12:00-22:00", "martes": "12:00-22:00"}
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")