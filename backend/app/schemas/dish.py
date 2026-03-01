from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class DishBase(BaseModel):
    name: str = Field(
        ...,
        max_length=100,
        description="Nombre del plato",
        json_schema_extra={"examples": ["Pasta Carbonara"]},
    )
    description: str | None = Field(
        None,
        max_length=300,
        description="Descripción del plato",
        json_schema_extra={"examples": ["Pasta fresca con huevo, guanciale y pecorino romano"]},
    )
    price: Decimal = Field(
        ...,
        gt=0,
        description="Precio en la moneda local",
        json_schema_extra={"examples": [12.50]},
    )
    offer_price: Decimal | None = Field(
        None,
        gt=0,
        description="Precio de oferta (debe ser menor que price)",
        json_schema_extra={"examples": [9.99]},
    )
    available: bool = Field(True, description="Si el plato está disponible para pedir")
    featured: bool = Field(False, description="Si el plato es destacado / recomendado")
    tags: list[str] = Field(
        default=[],
        description="Etiquetas del plato (ej: vegetariano, sin gluten)",
        json_schema_extra={"examples": [["italiano", "pasta"]]},
    )


class DishCreate(DishBase):
    """Datos para crear un nuevo plato. Se debe indicar la categoría a la que pertenece."""

    category_id: UUID = Field(..., description="UUID de la categoría a la que pertenece el plato")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Pasta Carbonara",
                    "description": "Pasta fresca con huevo, guanciale y pecorino romano",
                    "price": 12.50,
                    "category_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "tags": ["italiano", "pasta"],
                }
            ]
        }
    }


class DishUpdate(BaseModel):
    """Datos para actualizar un plato. Solo se modifican los campos enviados."""

    name: str | None = Field(None, max_length=100, description="Nuevo nombre")
    description: str | None = Field(None, max_length=300, description="Nueva descripción")
    price: Decimal | None = Field(None, gt=0, description="Nuevo precio")
    offer_price: Decimal | None = Field(None, gt=0, description="Nuevo precio de oferta")
    available: bool | None = Field(None, description="Cambiar disponibilidad")
    featured: bool | None = Field(None, description="Cambiar si es destacado")
    tags: list[str] | None = Field(None, description="Nuevas etiquetas")
    category_id: UUID | None = Field(None, description="Mover a otra categoría")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "price": 14.00,
                    "offer_price": 11.50,
                }
            ]
        }
    }


class DishInDB(DishBase):
    id: UUID
    category_id: UUID
    image_urls: dict | None = Field(None, description="URLs de las imágenes procesadas (original, thumbnail, medium)")
    position: int = Field(..., description="Posición del plato dentro de su categoría")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
