# app/core/enums.py
"""
Enumeraciones del dominio.
Usamos str, Enum para que Pydantic y SQLAlchemy las serialicen correctamente.
"""

from enum import Enum


class TipoIntervencion(str, Enum):
    """Tipos de intervención permitidos en el expediente técnico."""
    MANTENIMIENTO = "Mantenimiento"
    DIAGNOSTICO = "Diagnóstico"
    REPARACION = "Reparación"
    REVISION = "Revisión"
    INSTALACION = "Instalación"
    OTROS = "Otros"


class UserRole(str, Enum):
    """Roles de usuario del sistema."""
    ADMIN = "admin"
    TECNICO = "tecnico"
    RECEPCION = "recepcion"