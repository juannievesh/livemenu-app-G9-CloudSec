from uuid import UUID

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: str | None = Field(None, max_length=500)
    active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)
    active: bool | None = None


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
