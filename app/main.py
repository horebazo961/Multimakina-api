from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
# Importa tus modelos y schemas según tu estructura actual
# from app.models.vehicle import VehicleModel
# from app.schemas.vehicle_schema import VehicleCreate

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multimakina Cloud Secure API",
    version="2.5",
    description="API de diagnóstico y gestión de flotas para Multimakina Cloud"
)

# Configuración obligatoria de CORS para permitir peticiones desde Vercel y dispositivos móviles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "system": "Multimakina Cloud API", "version": "2.5"}

# Endpoints de Vehículos con soporte flexible para barras finales
@app.get("/vehicles", tags=["Vehicles"])
@app.get("/vehicles/", tags=["Vehicles"])
def get_vehicles(db: Session = Depends(get_db)):
    # Ejemplo de consulta a la base de datos (ajusta según tus modelos reales)
    # vehicles = db.query(VehicleModel).all()
    # return vehicles
    return []  # Reemplaza con tu lista de vehículos de SQLAlchemy

@app.post("/vehicles", tags=["Vehicles"])
@app.post("/vehicles/", tags=["Vehicles"])
def create_vehicle(payload: dict, db: Session = Depends(get_db)):
    # Lógica para registrar el vehículo en Supabase
    try:
        # nuevo_vehiculo = VehicleModel(**payload)
        # db.add(nuevo_vehiculo)
        # db.commit()
        # db.refresh(nuevo_vehiculo)
        return {"message": "Unidad de diagnóstico registrada exitosamente", "id": 1}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))