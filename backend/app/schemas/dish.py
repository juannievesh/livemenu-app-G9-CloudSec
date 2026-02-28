from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class DishBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = Field(None, max_length=300)
    price: Decimal = Field(..., gt=0)
    offer_price: Decimal | None = Field(None, gt=0)
    available: bool = True
    featured: bool = False
    tags: list[str] = []


class DishCreate(DishBase):
    category_id: UUID


class DishUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=300)
    price: Decimal | None = Field(None, gt=0)
    offer_price: Decimal | None = Field(None, gt=0)
    available: bool | None = None
    featured: bool | None = None
    tags: list[str] | None = None
    category_id: UUID | None = None


class DishInDB(DishBase):
    id: UUID
    category_id: UUID
    image_urls: dict | None
    position: int

    class Config:
        from_attributes = True
