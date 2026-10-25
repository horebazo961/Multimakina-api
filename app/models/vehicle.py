from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, event
from sqlalchemy.sql import func
from app.database.connection import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False)
    vin = Column(String(17), unique=True, index=True, nullable=False)
    status = Column(String(20), default="Diagnóstico")  # Diagnóstico, Reparado, Entregado
    dtc_codes = Column(Text, nullable=True)  # Códigos de error OBD-II en formato JSON o texto plano
    created_at = Column(DateTime(timezone=True), server_default=func.now())


@event.listens_for(Vehicle, "before_insert")
@event.listens_for(Vehicle, "before_update")
def normalize_vehicle_vin(mapper, connection, target):
    if target.vin:
        target.vin = target.vin.strip().upper()
