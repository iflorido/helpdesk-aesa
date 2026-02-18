"""
Endpoints de autenticación: registro, login, perfil.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from db import get_db
from db.repository import UserRepository
from schemas import UserCreate, UserLogin, UserResponse, Token
from core.security import create_access_token, get_current_user_id

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.
    
    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 8 caracteres)
    - **full_name**: Nombre completo (opcional)
    """
    repo = UserRepository(db)
    
    # Verificar si el email ya existe
    existing_user = repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    user = repo.create(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el usuario"
        )
    
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión y retorna un token JWT.
    
    - **email**: Email del usuario
    - **password**: Contraseña
    """
    repo = UserRepository(db)
    
    # Autenticar usuario
    user = repo.authenticate(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil del usuario autenticado.
    
    Requiere: Token JWT en el header Authorization
    """
    repo = UserRepository(db)
    
    user = repo.get_by_id(UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.get("/test-auth")
async def test_auth(user_id: str = Depends(get_current_user_id)):
    """
    Endpoint de prueba para verificar que la autenticación funciona.
    
    Requiere: Token JWT en el header Authorization
    """
    return {
        "message": "Autenticación exitosa",
        "user_id": user_id
    }