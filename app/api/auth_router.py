from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, UserUpdateStatus
from passlib.context import CryptContext
from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario o el correo electrónico ya están registrados.")
    
    hashed_password = pwd_context.hash(payload.password)
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
        role=payload.role.upper(),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta bloqueada por el Administrador.")
        
    return {
        "message": "Login exitoso",
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(user_id: int, payload: UserUpdateStatus, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user