from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.vehicle import Vehicle
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate
from app.services.pdf_service import PDFService
from typing import List, Optional

class VehicleService:
    @staticmethod
    def create_vehicle(db: Session, vehicle_data: VehicleCreate, user_id: int) -> Vehicle:
        db_vehicle = Vehicle(
            user_id=user_id,
            brand=vehicle_data.brand,
            model=vehicle_data.model,
            vin=vehicle_data.vin,
            status=vehicle_data.status
        )
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle

    @staticmethod
    def get_vehicle_by_id(db: Session, vehicle_id: int) -> Vehicle:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise ValueError("Vehículo no encontrado en el sistema.")
        return vehicle

    @staticmethod
    def get_vehicle_by_vin(db: Session, vin: str) -> Vehicle:
        return db.query(Vehicle).filter(Vehicle.vin == vin).first()

    @staticmethod
    def list_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        return db.query(Vehicle).offset(skip).limit(limit).all()

    @staticmethod
    def update_vehicle(db: Session, vehicle_id: int, vehicle_data: VehicleUpdate) -> Vehicle:
        vehicle = VehicleService.get_vehicle_by_id(db, vehicle_id)
        
        update_data = vehicle_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vehicle, key, value)
            
        db.commit()
        db.refresh(vehicle)
        return vehicle

    @staticmethod
    def delete_vehicle(db: Session, vehicle_id: int) -> bool:
        vehicle = VehicleService.get_vehicle_by_id(db, vehicle_id)
        db.delete(vehicle)
        db.commit()
        return True

    @staticmethod
    def attach_obd_report(db: Session, vehicle_id: int, pdf_bytes: bytes) -> Vehicle:
        vehicle = VehicleService.get_vehicle_by_id(db, vehicle_id)
        
        dtc_results = PDFService.extract_obd_dtc_from_pdf(pdf_bytes)
        
        vehicle.dtc_codes = dtc_results
        vehicle.status = "Diagnóstico"
        db.commit()
        db.refresh(vehicle)
        return vehicle

# Funciones de conveniencia expuestas a nivel de módulo
def create_vehicle(db: Session, vehicle_data: VehicleCreate, user_id: int) -> Vehicle:
    return VehicleService.create_vehicle(db, vehicle_data, user_id)

def get_vehicle_by_id(db: Session, vehicle_id: int) -> Vehicle:
    return VehicleService.get_vehicle_by_id(db, vehicle_id)

def get_vehicle_by_vin(db: Session, vin: str) -> Vehicle:
    return VehicleService.get_vehicle_by_vin(db, vin)

def list_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
    return VehicleService.list_vehicles(db, skip, limit)

def update_vehicle(db: Session, vehicle_id: int, vehicle_data: VehicleUpdate) -> Vehicle:
    return VehicleService.update_vehicle(db, vehicle_id, vehicle_data)

def delete_vehicle(db: Session, vehicle_id: int) -> bool:
    return VehicleService.delete_vehicle(db, vehicle_id)

def attach_obd_report(db: Session, vehicle_id: int, pdf_bytes: bytes) -> Vehicle:
    return VehicleService.attach_obd_report(db, vehicle_id, pdf_bytes)
