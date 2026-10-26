"""
Multimakina Cloud API
MVP orientado a kartódromo / preparación de carrera (Quito).
Backend FastAPI + Render Free + Supabase Session Pooler.
"""

import os
import logging
import secrets
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db

logger = logging.getLogger("multimakina")

# ---------------------------------------------------------------------------
# Constantes MVP kartódromo (Fase I/II)
# ---------------------------------------------------------------------------

ALLOWED_STATUSES = {
    "En box",
    "En preparación",
    "Listo para pista",
    "En pista",
    "Fuera de servicio",
}

ALLOWED_MAINTENANCE = {
    "Preventivo",
    "Correctivo",
    "Diagnóstico Electrónico",
    "Setup de carrera",
}

ALLOWED_CATEGORIES = {
    "Rental",
    "Competición",
    "Escuela",
    "Otro",
}

DEFAULT_STATUS = "En box"
DEFAULT_MAINTENANCE = "Preventivo"
DEFAULT_CATEGORY = "Rental"
DEFAULT_ESCUDERIA = "Kartódromo Quito"

# API_WRITE_KEY: si está definida en Render, POST/PATCH exigen header X-API-Key
API_WRITE_KEY = (os.getenv("API_WRITE_KEY") or "").strip()


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    vin = Column(String, unique=True, index=True)  # VIN o código técnico único
    internal_code = Column(String, unique=True, index=True, nullable=True)  # código de pista/box
    category = Column(String, default=DEFAULT_CATEGORY)
    status = Column(String, default=DEFAULT_STATUS)
    maintenance_type = Column(String, default=DEFAULT_MAINTENANCE)
    taller_propietario = Column(String, default=DEFAULT_ESCUDERIA)  # escudería / taller


try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.execute(
            text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS maintenance_type VARCHAR DEFAULT 'Preventivo'")
        )
        connection.execute(
            text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS taller_propietario VARCHAR DEFAULT 'Kartódromo Quito'")
        )
        connection.execute(
            text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS internal_code VARCHAR")
        )
        connection.execute(
            text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'Rental'")
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
        "http://localhost:3000,http://127.0.0.1:3000,https://multimakinaapi.vercel.app",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Multimakina Cloud API",
    version="3.1.0",
    description="API de gestión de flota — MVP kartódromo / preparación de carrera",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://[a-zA-Z0-9-]+(?:-[a-zA-Z0-9-]+)*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)


def require_write_access(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    """Si API_WRITE_KEY está configurada, exige la misma clave en escritura."""
    if not API_WRITE_KEY:
        return
    if not x_api_key or not secrets.compare_digest(x_api_key, API_WRITE_KEY):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Se requiere X-API-Key válida para crear o modificar unidades.",
            },
        )


def duplicate_identifier_error(field: str = "vin") -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "code": "DUPLICATE_IDENTIFIER",
            "field": field,
            "message": f"El identificador ({field}) ya está registrado en la flota.",
        },
    )


def normalize_status(value: Optional[str]) -> str:
    status = (value or DEFAULT_STATUS).strip()
    if status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_STATUS",
                "message": f"Estado no permitido. Use uno de: {', '.join(sorted(ALLOWED_STATUSES))}",
            },
        )
    return status


def normalize_maintenance(value: Optional[str]) -> str:
    item = (value or DEFAULT_MAINTENANCE).strip()
    if item not in ALLOWED_MAINTENANCE:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_MAINTENANCE",
                "message": f"Tipo no permitido. Use: {', '.join(sorted(ALLOWED_MAINTENANCE))}",
            },
        )
    return item


def normalize_category(value: Optional[str]) -> str:
    item = (value or DEFAULT_CATEGORY).strip()
    if item not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_CATEGORY",
                "message": f"Categoría no permitida. Use: {', '.join(sorted(ALLOWED_CATEGORIES))}",
            },
        )
    return item


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
        "version": "3.1.0",
        "profile": "kartodromo-mvp",
        "database": "ok" if db_ok else "error",
        "database_error": db_error,
        "write_protection": "api_key" if API_WRITE_KEY else "open",
        "allowed_statuses": sorted(ALLOWED_STATUSES),
    }


@app.get("/api/v1/meta/statuses", tags=["Meta"])
def list_statuses():
    return {
        "statuses": sorted(ALLOWED_STATUSES),
        "maintenance_types": sorted(ALLOWED_MAINTENANCE),
        "categories": sorted(ALLOWED_CATEGORIES),
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
def create_vehicle(
    payload: dict,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
):
    vin = (payload.get("vin") or "").strip().upper()
    internal_code = (payload.get("internal_code") or "").strip().upper() or None

    if not vin and not internal_code:
        raise HTTPException(
            status_code=400,
            detail="Debe indicar VIN o internal_code (código de pista/box).",
        )

    # Si no hay VIN, usar el código interno como identificador único técnico
    if not vin and internal_code:
        vin = f"INT-{internal_code}"

    try:
        if db.query(VehicleModel).filter(VehicleModel.vin == vin).first():
            raise duplicate_identifier_error("vin")
        if internal_code and db.query(VehicleModel).filter(VehicleModel.internal_code == internal_code).first():
            raise duplicate_identifier_error("internal_code")

        vehicle = VehicleModel(
            brand=(payload.get("brand") or "").strip() or "Sin marca",
            model=(payload.get("model") or "").strip() or "Sin modelo",
            vin=vin,
            internal_code=internal_code,
            category=normalize_category(payload.get("category")),
            status=normalize_status(payload.get("status")),
            maintenance_type=normalize_maintenance(payload.get("maintenance_type")),
            taller_propietario=(
                (payload.get("taller_propietario") or payload.get("escuderia") or DEFAULT_ESCUDERIA).strip()
            ),
        )
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
        return {
            "message": "Unidad registrada con éxito",
            "id": vehicle.id,
            "vin": vehicle.vin,
            "internal_code": vehicle.internal_code,
            "status": vehicle.status,
        }
    except HTTPException:
        raise
    except IntegrityError as error:
        db.rollback()
        raise duplicate_identifier_error("vin") from error
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}") from e


@app.patch("/api/v1/vehicles/{vehicle_id}", tags=["Vehicles"])
def update_vehicle(
    vehicle_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
):
    try:
        vehicle = db.query(VehicleModel).filter(VehicleModel.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Unidad no encontrada en la flota.")

        if "vin" in payload:
            new_vin = (payload["vin"] or "").strip().upper()
            payload["vin"] = new_vin
            dup = (
                db.query(VehicleModel)
                .filter(VehicleModel.vin == new_vin, VehicleModel.id != vehicle_id)
                .first()
            )
            if dup:
                raise duplicate_identifier_error("vin")

        if "internal_code" in payload:
            new_code = (payload["internal_code"] or "").strip().upper() or None
            payload["internal_code"] = new_code
            if new_code:
                dup = (
                    db.query(VehicleModel)
                    .filter(VehicleModel.internal_code == new_code, VehicleModel.id != vehicle_id)
                    .first()
                )
                if dup:
                    raise duplicate_identifier_error("internal_code")

        if "status" in payload:
            payload["status"] = normalize_status(payload.get("status"))
        if "maintenance_type" in payload:
            payload["maintenance_type"] = normalize_maintenance(payload.get("maintenance_type"))
        if "category" in payload:
            payload["category"] = normalize_category(payload.get("category"))
        if "escuderia" in payload and "taller_propietario" not in payload:
            payload["taller_propietario"] = payload["escuderia"]

        for field in (
            "brand",
            "model",
            "vin",
            "internal_code",
            "category",
            "status",
            "maintenance_type",
            "taller_propietario",
        ):
            if field in payload:
                setattr(vehicle, field, payload[field])

        db.commit()
        db.refresh(vehicle)
        return vehicle
    except HTTPException:
        raise
    except IntegrityError as error:
        db.rollback()
        raise duplicate_identifier_error("vin") from error
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}") from e
