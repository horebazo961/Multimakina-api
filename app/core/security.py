# app/core/security.py
"""
Única fuente de funciones de seguridad.
Hash de contraseñas + creación y verificación de JWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano."""
    if isinstance(password, bytes):
        password = password.decode("utf-8")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode("utf-8")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Genera un JWT firmado.
    Payload típico: {"sub": email, "id": user_id, "role": role}
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida el JWT.
    Retorna el payload si es válido, None si es inválido o expiró.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None