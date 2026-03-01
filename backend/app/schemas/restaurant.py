from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RestaurantCreate(BaseModel):
    name: str = Field(
        ...,
        max_length=100,
        description="Nombre del restaurante",
        json_schema_extra={"examples": ["La Trattoria"]},
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Descripción breve del restaurante",
        json_schema_extra={"examples": ["Auténtica cocina italiana en el corazón de la ciudad"]},
    )
    address: str | None = Field(
        None,
        max_length=200,
        description="Dirección física del restaurante",
        json_schema_extra={"examples": ["Calle Mayor 12, Madrid"]},
    )
    logo_url: str | None = Field(
        None,
        description="URL del logotipo (obtenida tras subir imagen con /upload)",
        json_schema_extra={"examples": ["https://storage.googleapis.com/bucket/logo.webp"]},
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="Teléfono de contacto",
        json_schema_extra={"examples": ["+34 612 345 678"]},
    )
    horarios: dict | None = Field(
        None,
        description="Horarios de apertura por día de la semana",
        json_schema_extra={"examples": [{"lunes": "12:00-22:00", "martes": "12:00-22:00", "miércoles": "12:00-22:00"}]},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "La Trattoria",
                    "description": "Auténtica cocina italiana en el corazón de la ciudad",
                    "address": "Calle Mayor 12, Madrid",
                    "phone": "+34 612 345 678",
                    "horarios": {
                        "lunes": "12:00-22:00",
                        "martes": "12:00-22:00",
                        "miércoles": "12:00-22:00",
                        "jueves": "12:00-23:00",
                        "viernes": "12:00-23:00",
                        "sábado": "13:00-23:30",
                        "domingo": "13:00-22:00",
                    },
                }
            ]
        }
    }


class RestaurantUpdate(BaseModel):
    name: str | None = Field(
        None,
        max_length=100,
        description="Nuevo nombre del restaurante",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Nueva descripción",
    )
    address: str | None = Field(
        None,
        max_length=200,
        description="Nueva dirección",
    )
    logo_url: str | None = Field(
        None,
        description="Nueva URL del logotipo",
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="Nuevo teléfono de contacto",
    )
    horarios: dict | None = Field(
        None,
        description="Nuevos horarios de apertura",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "La Trattoria Renovada",
                    "phone": "+34 699 999 999",
                }
            ]
        }
    }


class RestaurantInDB(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    address: str | None = None
    logo_url: str | None = None
    phone: str | None = None
    horarios: dict | None = None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
