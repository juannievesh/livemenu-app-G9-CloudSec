from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Correo electrónico del usuario",
        json_schema_extra={"examples": ["chef@mirestaurante.com"]},
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="Contraseña (mínimo 6 caracteres)",
        json_schema_extra={"examples": ["miPassword123"]},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "chef@mirestaurante.com",
                    "password": "miPassword123",
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Correo electrónico registrado",
        json_schema_extra={"examples": ["chef@mirestaurante.com"]},
    )
    password: str = Field(
        ...,
        description="Contraseña del usuario",
        json_schema_extra={"examples": ["miPassword123"]},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "chef@mirestaurante.com",
                    "password": "miPassword123",
                }
            ]
        }
    }


class UserResponse(BaseModel):
    id: UUID
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT token para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token (siempre 'bearer')")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                }
            ]
        }
    }
