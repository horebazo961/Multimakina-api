import re
from typing import Optional

from pydantic import BaseModel, Field, validator

VIN_PATTERN = re.compile(r"^[A-Z0-9]{17}$")


def normalize_vin(value: str) -> str:
    normalized = value.strip().upper()
    if not VIN_PATTERN.fullmatch(normalized):
        raise ValueError("El VIN debe contener exactamente 17 caracteres alfanuméricos.")
    return normalized


class VehicleCreate(BaseModel):
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    vin: str = Field(..., min_length=17, max_length=17)
    status: Optional[str] = "Diagnóstico"

    _normalize_vin = validator("vin", allow_reuse=True)(normalize_vin)


class VehicleUpdate(BaseModel):
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    status: Optional[str] = None

    _normalize_vin = validator("vin", allow_reuse=True)(normalize_vin)


class VehicleResponse(VehicleCreate):
    id: int
    user_id: int
    dtc_codes: Optional[str] = None

    class Config:
        from_attributes = True
