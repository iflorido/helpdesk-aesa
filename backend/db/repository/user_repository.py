"""
Repositorio para operaciones de Usuario en la base de datos.
Patrón Repository para separar lógica de negocio del ORM.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.models import User
from core.security import get_password_hash, verify_password


class UserRepository:
    """Repositorio para gestionar usuarios."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, email: str, password: str, full_name: Optional[str] = None, is_admin: bool = False) -> Optional[User]:
        """
        Crea un nuevo usuario.
        
        Returns:
            User creado o None si el email ya existe.
        """
        # Verificar si el email ya existe
        if self.get_by_email(email):
            return None
        
        try:
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                is_admin=is_admin,
                is_active=True,
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            return user
        
        except IntegrityError:
            self.db.rollback()
            return None
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Autentica un usuario con email y contraseña.
        
        Returns:
            User si las credenciales son correctas, None en caso contrario.
        """
        user = self.get_by_email(email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def update(self, user_id: UUID, full_name: Optional[str] = None, password: Optional[str] = None) -> Optional[User]:
        """
        Actualiza los datos de un usuario.
        
        Returns:
            User actualizado o None si no existe.
        """
        user = self.get_by_id(user_id)
        
        if not user:
            return None
        
        if full_name is not None:
            user.full_name = full_name
        
        if password is not None:
            user.hashed_password = get_password_hash(password)
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            return None
    
    def deactivate(self, user_id: UUID) -> bool:
        """
        Desactiva un usuario (soft delete).
        
        Returns:
            True si se desactivó correctamente, False en caso contrario.
        """
        user = self.get_by_id(user_id)
        
        if not user:
            return False
        
        user.is_active = False
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lista todos los usuarios (paginado)."""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Cuenta el total de usuarios."""
        return self.db.query(User).count()