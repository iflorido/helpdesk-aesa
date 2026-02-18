"""
Schemas Pydantic para Usuario.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    """Schema base para usuario."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear un usuario."""
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")


class UserLogin(BaseModel):
    """Schema para login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema para actualizar usuario."""
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """Schema de usuario en base de datos."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserResponse(UserInDB):
    """Schema de respuesta pública de usuario."""
    pass


class Token(BaseModel):
    """Schema de token JWT."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema de datos dentro del token."""
    user_id: Optional[str] = None