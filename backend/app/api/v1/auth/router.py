from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.jwt import create_access_token

from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from .service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Registrar nuevo usuario",
    description="Crea una cuenta de usuario nueva. El email debe ser único en el sistema.",
    responses={
        201: {"description": "Usuario creado exitosamente"},
        400: {"description": "El email ya está registrado"},
    },
)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data.email, data.password)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario con email y contraseña. "
    "Devuelve un JWT token que debe enviarse en el header `Authorization: Bearer <token>` "
    "para acceder a los endpoints protegidos.",
    responses={
        200: {"description": "Login exitoso, devuelve JWT token"},
        401: {"description": "Credenciales incorrectas"},
    },
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    description="Devuelve los datos del usuario autenticado. "
    "Útil para verificar que el token es válido y obtener el ID del usuario.",
    responses={
        200: {"description": "Datos del usuario autenticado"},
        401: {"description": "Token inválido o expirado"},
    },
)
async def me(current_user=Depends(get_current_user)):
    return current_user
