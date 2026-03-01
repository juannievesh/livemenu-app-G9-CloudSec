from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(
        ...,
        max_length=50,
        description="Nombre de la categoría",
        json_schema_extra={"examples": ["Entrantes"]},
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Descripción de la categoría",
        json_schema_extra={"examples": ["Platos para compartir antes del principal"]},
    )
    active: bool = Field(True, description="Si la categoría es visible en el menú público")


class CategoryCreate(CategoryBase):
    """Datos para crear una nueva categoría en el menú."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Entrantes",
                    "description": "Platos para compartir antes del principal",
                    "active": True,
                }
            ]
        }
    }


class CategoryUpdate(BaseModel):
    """Datos para actualizar una categoría. Solo se modifican los campos enviados."""

    name: str | None = Field(None, max_length=50, description="Nuevo nombre")
    description: str | None = Field(None, max_length=500, description="Nueva descripción")
    active: bool | None = Field(None, description="Cambiar visibilidad")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Postres caseros",
                }
            ]
        }
    }


class CategoryInDB(CategoryBase):
    id: UUID
    restaurant_id: UUID
    position: int = Field(..., description="Posición de la categoría en el menú")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryReorderItem(BaseModel):
    id: UUID = Field(..., description="UUID de la categoría")
    position: int = Field(..., ge=0, description="Nueva posición (0 = primera)")


class CategoryReorder(BaseModel):
    """Reordena las categorías del menú enviando la lista completa con las nuevas posiciones."""

    order: list[CategoryReorderItem] = Field(..., description="Lista de categorías con su nueva posición")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order": [
                        {"id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "position": 0},
                        {"id": "b2c3d4e5-f6a7-8901-bcde-f12345678901", "position": 1},
                    ]
                }
            ]
        }
    }
