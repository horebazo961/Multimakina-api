from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres.ditabcbswzrwmkeudspu:k9Navzh42qmeX6-@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
)

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
    maintenance_type = Column(String, default="Preventivo") # Nuevo campo
    taller_propietario = Column(String, default="Taller Central")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multimakina Cloud Secure API", version="2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.post("/vehicles", tags=["Vehicles"])
@app.post("/vehicles/", tags=["Vehicles"])
def create_vehicle(payload: dict, db: Session = Depends(get_db)):
    try:
        nuevo_vehiculo = VehicleModel(
            brand=payload.get("brand"),
            model=payload.get("model"),
            vin=payload.get("vin"),
            status=payload.get("status", "Diagnóstico"),
            maintenance_type=payload.get("maintenance_type", "Preventivo"),
            taller_propietario=payload.get("taller_propietario", "Taller Central")
        )
        db.add(nuevo_vehiculo)
        db.commit()
        db.refresh(nuevo_vehiculo)
        return {"message": "Unidad registrada con éxito", "id": nuevo_vehiculo.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))