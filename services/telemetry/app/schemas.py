from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DeviceBase(BaseModel):
    name: str
    device_type: str

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TelemetryBase(BaseModel):
    device_id: int
    timestamp: datetime
    energy_watts: float = Field(ge=0)  # Must be non-negative

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryResponse(TelemetryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TelemetryStats(BaseModel):
    device_id: int
    period: str
    avg_energy_watts: float
    max_energy_watts: float
    min_energy_watts: float
    total_energy_watt_hours: float 