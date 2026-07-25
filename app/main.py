from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from . import models
from .database import engine, get_db

# Inicializar seguridad de contraseñas con Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multimakina Cloud Secure API", version="2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ESQUEMAS PYDANTIC ---
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "TECNICO"
    taller_nombre: str = "Taller Central"

class UserLogin(BaseModel):
    username: str
    password: str

class VehicleCreate(BaseModel):
    brand: str
    model: str
    vin: str
    status: str = "Diagnóstico"
    taller_propietario: str = "Taller Central"

class StatusUpdate(BaseModel):
    is_active: bool

# --- RUTAS DE AUTENTICACIÓN SEGURA ---
@app.post("/auth/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
    
    # Encriptar contraseña antes de guardarla (Cumplimiento de Privacidad)
    hashed_password = pwd_context.hash(user.password)
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role,
        taller_nombre=user.taller_nombre,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Operador y taller registrado con éxito", "id": new_user.id, "taller": new_user.taller_nombre}

@app.post("/auth/login")
def login_user(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == creds.username).first()
    
    # Verificar usuario y contraseña mediante hash seguro
    if not user or not pwd_context.verify(creds.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta cuenta se encuentra bloqueada por seguridad.")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "taller_nombre": user.taller_nombre
    }

@app.get("/auth/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role,
        "taller_nombre": u.taller_nombre,
        "is_active": u.is_active
    } for u in users]

@app.patch("/auth/users/{user_id}/status")
def update_user_status(user_id: int, status_data: StatusUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user.is_active = status_data.is_active
    db.commit()
    return {"message": "Estado de seguridad actualizado", "is_active": user.is_active}

# --- RUTAS DE VEHÍCULOS Y DIAGNÓSTICO MULTI-TALLER ---
@app.post("/vehicles/")
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    new_vehicle = models.Vehicle(
        brand=vehicle.brand,
        model=vehicle.model,
        vin=vehicle.vin,
        status=vehicle.status,
        taller_propietario=vehicle.taller_propietario
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return {"message": "Vehículo registrado de forma segura", "id": new_vehicle.id, "taller": new_vehicle.taller_propietario}

@app.get("/vehicles/")
def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles

@app.post("/vehicles/{vehicle_id}/upload-obd-pdf")
def upload_obd_pdf(vehicle_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    
    simulated_dtc = "P0300 (Fallo encendido múltiple), P0171 (Mezcla pobre banco 1)"
    vehicle.dtc_codes = simulated_dtc
    db.commit()
    
    return {
        "message": f"Expediente del taller procesado de forma segura para la unidad {vehicle_id}",
        "dtc_codes": simulated_dtc
    }