# app/services/user_service.py
"""
Lógica de negocio de usuarios.
Registro y autenticación.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.core.security import hash_password, verify_password
from app.core.enums import UserRole


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Registra un nuevo usuario.
    - Verifica que el email y username no existan.
    - Hashea la contraseña antes de guardar.
    """
    # Verificar email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{user_data.email}' ya está registrado"
        )

    # Verificar username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El username '{user_data.username}' ya está en uso"
        )

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Autentica un usuario por email y contraseña.
    Retorna el usuario si las credenciales son válidas, None si no.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if user.is_active != 1:
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Obtiene un usuario por su ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user