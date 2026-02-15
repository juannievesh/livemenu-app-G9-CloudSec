from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from decimal import Decimal


class DishBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    price: Decimal = Field(..., gt=0)
    offer_price: Optional[Decimal] = Field(None, gt=0)
    available: bool = True
    featured: bool = False
    tags: List[str] = []


class DishCreate(DishBase):
    category_id: UUID


class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    price: Optional[Decimal] = Field(None, gt=0)
    offer_price: Optional[Decimal] = Field(None, gt=0)
    available: Optional[bool] = None
    featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    category_id: Optional[UUID] = None


class DishInDB(DishBase):
    id: UUID
    category_id: UUID
    image_url: Optional[str]
    position: int

    class Config:
        from_attributes = True