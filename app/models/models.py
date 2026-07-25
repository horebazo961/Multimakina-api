from sqlalchemy import Column, Integer, String, Boolean, Text
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    password = Column(String) # Almacena el hash seguro de bcrypt
    role = Column(String, default="TECNICO") # ADMIN, TECNICO
    taller_nombre = Column(String, default="Taller Central") # Identifica la sucursal del taller
    is_active = Column(Boolean, default=True)

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model = Column(String)
    vin = Column(String, unique=True, index=True)
    status = Column(String, default="Diagnóstico")
    dtc_codes = Column(Text, nullable=True)
    taller_propietario = Column(String, index=True, default="Taller Central") # Blindaje para filtrar datos por taller vecino