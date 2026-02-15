from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    active: Optional[bool] = None


class CategoryInDB(CategoryBase):
    id: UUID
    restaurant_id: UUID
    position: int

    class Config:
        from_attributes = True


class CategoryReorderItem(BaseModel):
    id: UUID
    position: int


class CategoryReorder(BaseModel):
    order: list[CategoryReorderItem]