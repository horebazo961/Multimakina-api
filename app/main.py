from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./multimakina.db")

# Orígenes explícitos para producción; los previews de Vercel se cubren con
# allow_origin_regex sin abrir CORS a cualquier sitio.
CORS_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    vin = Column(String, unique=True, index=True)
    status = Column(String, default="Diagnóstico")
    maintenance_type = Column(String, default="Preventivo")
    taller_propietario = Column(String, default="Taller Central")

# Crear tablas y asegurar columnas nuevas en Supabase
Base.metadata.create_all(bind=engine)
with engine.connect() as connection:
    try:
        connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS maintenance_type VARCHAR DEFAULT 'Preventivo';"))
        connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS taller_propietario VARCHAR DEFAULT 'Taller Central';"))
        connection.commit()
    except Exception:
        pass

app = FastAPI(title="Multimakina Cloud Secure API", version="2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # Autoriza únicamente dominios Vercel y los orígenes explícitos configurados.
    allow_origin_regex=r"https://[a-zA-Z0-9-]+(?:-[a-zA-Z0-9-]+)*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "online", "system": "Multimakina Cloud API"}

@app.get("/vehicles", tags=["Vehicles"])
@app.get("/vehicles/", tags=["Vehicles"])
def get_vehicles(db: Session = Depends(get_db)):
    try:
        return db.query(VehicleModel).all()
    except Exception:
        return []

def duplicate_vin_error() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "code": "DUPLICATE_VIN",
            "field": "vin",
            "message": "El número VIN ingresado ya se encuentra registrado en el sistema.",
        },
    )


@app.post("/vehicles", tags=["Vehicles"])
@app.post("/vehicles/", tags=["Vehicles"])
def create_vehicle(payload: dict, db: Session = Depends(get_db)):
    vin = (payload.get("vin") or "").strip().upper()
    if db.query(VehicleModel).filter(VehicleModel.vin == vin).first():
        raise duplicate_vin_error()

    nuevo_vehiculo = VehicleModel(
        brand=payload.get("brand"),
        model=payload.get("model"),
        vin=vin,
        status=payload.get("status", "Diagnóstico"),
        maintenance_type=payload.get("maintenance_type", "Preventivo"),
        taller_propietario=payload.get("taller_propietario", "Taller Central"),
    )
    try:
        db.add(nuevo_vehiculo)
        db.commit()
        db.refresh(nuevo_vehiculo)
        return {"message": "Unidad registrada con éxito", "id": nuevo_vehiculo.id}
    except IntegrityError as error:
        db.rollback()
        if "vin" in str(error.orig).lower() or "unique" in str(error.orig).lower():
            raise duplicate_vin_error() from error
        raise HTTPException(status_code=400, detail="No se pudo registrar la unidad.") from error


@app.patch("/vehicles/{vehicle_id}", tags=["Vehicles"])
def update_vehicle(vehicle_id: int, payload: dict, db: Session = Depends(get_db)):
    vehicle = db.query(VehicleModel).filter(VehicleModel.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado en el sistema.")

    if "vin" in payload:
        payload["vin"] = (payload["vin"] or "").strip().upper()
        duplicate = db.query(VehicleModel).filter(
            VehicleModel.vin == payload["vin"], VehicleModel.id != vehicle_id
        ).first()
        if duplicate:
            raise duplicate_vin_error()

    for field in ("brand", "model", "vin", "status", "maintenance_type", "taller_propietario"):
        if field in payload:
            setattr(vehicle, field, payload[field])
    try:
        db.commit()
        db.refresh(vehicle)
        return vehicle
    except IntegrityError as error:
        db.rollback()
        if "vin" in str(error.orig).lower() or "unique" in str(error.orig).lower():
            raise duplicate_vin_error() from error
        raise HTTPException(status_code=400, detail="No se pudo actualizar la unidad.") from error
