from pydantic import BaseModel, Field
from typing import Optional

class VehicleCreate(BaseModel):
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    vin: str = Field(..., min_length=17, max_length=17)
    status: Optional[str] = "Diagnóstico"

class VehicleUpdate(BaseModel):
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    status: Optional[str] = None

class VehicleResponse(VehicleCreate):
    id: int
    user_id: int
    dtc_codes: Optional[str] = None

    class Config:
        from_attributes = True