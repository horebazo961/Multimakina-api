"""
Multimakina Cloud API
Backend FastAPI limpio, listo para Render (Free) + Supabase (Free).
"""

import os
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db

logger = logging.getLogger("multimakina")

# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    vin = Column(String, unique=True, index=True)
    status = Column(String, default="Diagnóstico")
    maintenance_type = Column(String, default="Preventivo")
    taller_propietario = Column(String, default="Taller Central")


# Crear tablas al arrancar
try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.execute(
            text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS maintenance_type VARCHAR DEFAULT 'Preventivo'")
        )
        connection.execute(
            text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS taller_propietario VARCHAR DEFAULT 'Taller Central'")
        )
        connection.commit()
    logger.info("Tablas verificadas/creadas correctamente")
except Exception as e:
    logger.error("No se pudieron crear/actualizar tablas al inicio: %s", e)

# ---------------------------------------------------------------------------
# App + CORS
# ---------------------------------------------------------------------------

CORS_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Multimakina Cloud API",
    version="3.0.2",
    description="API de gestión vehicular para talleres - Multimakina",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://[a-zA-Z0-9-]+(?:-[a-zA-Z0-9-]+)*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


def duplicate_vin_error() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "code": "DUPLICATE_VIN",
            "field": "vin",
            "message": "El número VIN ingresado ya se encuentra registrado en el sistema.",
        },
    )


@app.get("/")
def health():
    db_ok = False
    db_error = None
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_error = str(e)
    return {
        "status": "online",
        "system": "Multimakina Cloud API",
        "version": "3.0.2",
        "database": "ok" if db_ok else "error",
        "database_error": db_error,
    }


@app.get("/api/v1/vehicles", tags=["Vehicles"])
@app.get("/api/v1/vehicles/", tags=["Vehicles"])
def list_vehicles(db: Session = Depends(get_db)):
    try:
        return db.query(VehicleModel).order_by(VehicleModel.id.desc()).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}") from e


@app.post("/api/v1/vehicles", tags=["Vehicles"])
@app.post("/api/v1/vehicles/", tags=["Vehicles"])
def create_vehicle(payload: dict, db: Session = Depends(get_db)):
    vin = (payload.get("vin") or "").strip().upper()
    if not vin:
        raise HTTPException(status_code=400, detail="VIN es obligatorio.")

    try:
        exists = db.query(VehicleModel).filter(VehicleModel.vin == vin).first()
        if exists:
            raise duplicate_vin_error()

        vehicle = VehicleModel(
            brand=(payload.get("brand") or "").strip(),
            model=(payload.get("model") or "").strip(),
            vin=vin,
            status=payload.get("status") or "Diagnóstico",
            maintenance_type=payload.get("maintenance_type") or "Preventivo",
            taller_propietario=payload.get("taller_propietario") or "Taller Central",
        )
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
        return {"message": "Unidad registrada con éxito", "id": vehicle.id}
    except HTTPException:
        raise
    except IntegrityError as error:
        db.rollback()
        if "vin" in str(error.orig).lower() or "unique" in str(error.orig).lower():
            raise duplicate_vin_error() from error
        raise HTTPException(status_code=400, detail=f"No se pudo registrar: {str(error.orig)}") from error
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}") from e


@app.patch("/api/v1/vehicles/{vehicle_id}", tags=["Vehicles"])
def update_vehicle(vehicle_id: int, payload: dict, db: Session = Depends(get_db)):
    try:
        vehicle = db.query(VehicleModel).filter(VehicleModel.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado en el sistema.")

        if "vin" in payload:
            new_vin = (payload["vin"] or "").strip().upper()
            payload["vin"] = new_vin
            duplicate = (
                db.query(VehicleModel)
                .filter(VehicleModel.vin == new_vin, VehicleModel.id != vehicle_id)
                .first()
            )
            if duplicate:
                raise duplicate_vin_error()

        for field in ("brand", "model", "vin", "status", "maintenance_type", "taller_propietario"):
            if field in payload:
                setattr(vehicle, field, payload[field])

        db.commit()
        db.refresh(vehicle)
        return vehicle
    except HTTPException:
        raise
    except IntegrityError as error:
        db.rollback()
        if "vin" in str(error.orig).lower() or "unique" in str(error.orig).lower():
            raise duplicate_vin_error() from error
        raise HTTPException(status_code=400, detail=str(error.orig)) from error
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}") from e
