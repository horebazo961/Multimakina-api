# app/api/vehicle_router.py
"""
Endpoints del Expediente Técnico de Vehículos.
Todos los endpoints están protegidos con JWT.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.vehicle_schema import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse
)
from app.services.vehicle_service import (
    create_vehicle,
    get_vehicle_by_id,
    get_vehicle_by_vin,
    list_vehicles,
    update_vehicle,
    delete_vehicle
)
from app.services.pdf_service import generate_vehicle_pdf
from app.core.enums import TipoIntervencion

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear expediente técnico"
)
def create_new_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo expediente técnico.
    El campo created_by se asigna automáticamente con el usuario autenticado.
    """
    return create_vehicle(db, vehicle_data, current_user.id)


@router.get(
    "/",
    response_model=List[VehicleResponse],
    summary="Listar vehículos"
)
def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    programa: Optional[str] = Query(None, description="Filtrar por programa_adjuntar"),
    intervencion: Optional[TipoIntervencion] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista los expedientes técnicos.
    Soporta filtros por programa e intervención.
    """
    return list_vehicles(db, skip=skip, limit=limit, programa=programa, intervencion=intervencion)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Obtener vehículo por ID"
)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_vehicle_by_id(db, vehicle_id)


@router.get(
    "/vin/{vin}",
    response_model=VehicleResponse,
    summary="Obtener vehículo por VIN"
)
def get_vehicle_vin(
    vin: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca un vehículo por su VIN.
    Clave para futuras intervenciones del mismo vehículo.
    """
    return get_vehicle_by_vin(db, vin)


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Actualizar expediente (parcial)"
)
def update_existing_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_vehicle(db, vehicle_id, vehicle_data)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar expediente"
)
def remove_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_vehicle(db, vehicle_id)


@router.get(
    "/{vehicle_id}/pdf",
    summary="Descargar PDF del expediente técnico",
    response_class=StreamingResponse
)
def download_vehicle_pdf(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera y descarga el PDF del expediente técnico del vehículo.
    """
    vehicle = get_vehicle_by_id(db, vehicle_id)
    pdf_buffer = generate_vehicle_pdf(vehicle)

    filename = f"Expediente_{vehicle.vin}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )