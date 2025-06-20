from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

from app.database import get_db, init_db
from app.models import Device, Telemetry
from app.schemas import (
    DeviceCreate,
    DeviceResponse,
    TelemetryCreate,
    TelemetryResponse,
    TelemetryStats
)
from app.auth import get_current_user, User

app = FastAPI(
    title="Smart Home Telemetry Service",
    description="Telemetry service for Smart Home Energy Monitoring",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/api/devices", response_model=DeviceResponse)
def create_device(
    device: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_device = Device(
        name=device.name,
        device_type=device.device_type,
        user_id=current_user.id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.get("/api/devices", response_model=List[DeviceResponse])
def get_user_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Device).filter(Device.user_id == current_user.id).all()

@app.post("/api/telemetry", response_model=TelemetryResponse)
def create_telemetry(
    telemetry: TelemetryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify device belongs to user
    device = db.query(Device).filter(
        Device.id == telemetry.device_id,
        Device.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by user"
        )
    
    db_telemetry = Telemetry(
        device_id=telemetry.device_id,
        timestamp=telemetry.timestamp,
        energy_watts=telemetry.energy_watts
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

@app.get("/api/telemetry/{device_id}", response_model=List[TelemetryResponse])
def get_device_telemetry(
    device_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify device belongs to user
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by user"
        )
    
    query = db.query(Telemetry).filter(Telemetry.device_id == device_id)
    
    if start_time:
        query = query.filter(Telemetry.timestamp >= start_time)
    if end_time:
        query = query.filter(Telemetry.timestamp <= end_time)
    
    return query.order_by(Telemetry.timestamp.desc()).all()

@app.get("/api/telemetry/{device_id}/stats", response_model=TelemetryStats)
def get_device_stats(
    device_id: int,
    period: str = "24h",  # Supports: 24h, 7d, 30d
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify device belongs to user
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by user"
        )
    
    # Calculate time range
    end_time = datetime.utcnow()
    if period == "24h":
        start_time = end_time - timedelta(hours=24)
    elif period == "7d":
        start_time = end_time - timedelta(days=7)
    elif period == "30d":
        start_time = end_time - timedelta(days=30)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid period. Supported values: 24h, 7d, 30d"
        )
    
    # Get telemetry data
    telemetry_data = db.query(Telemetry).filter(
        Telemetry.device_id == device_id,
        Telemetry.timestamp >= start_time,
        Telemetry.timestamp <= end_time
    ).all()
    
    if not telemetry_data:
        return TelemetryStats(
            device_id=device_id,
            period=period,
            avg_energy_watts=0,
            max_energy_watts=0,
            min_energy_watts=0,
            total_energy_watt_hours=0
        )
    
    # Convert to pandas DataFrame for easy calculations
    df = pd.DataFrame([{
        'timestamp': t.timestamp,
        'energy_watts': t.energy_watts
    } for t in telemetry_data])
    
    # Calculate statistics
    avg_energy = df['energy_watts'].mean()
    max_energy = df['energy_watts'].max()
    min_energy = df['energy_watts'].min()
    
    # Calculate total energy (watt-hours) using trapezoidal integration
    df = df.sort_values('timestamp')
    total_energy = 0
    if len(df) > 1:
        time_diff_hours = [(t2 - t1).total_seconds() / 3600 
                          for t1, t2 in zip(df['timestamp'][:-1], df['timestamp'][1:])]
        avg_power = [(p1 + p2) / 2 
                    for p1, p2 in zip(df['energy_watts'][:-1], df['energy_watts'][1:])]
        total_energy = sum(t * p for t, p in zip(time_diff_hours, avg_power))
    
    return TelemetryStats(
        device_id=device_id,
        period=period,
        avg_energy_watts=avg_energy,
        max_energy_watts=max_energy,
        min_energy_watts=min_energy,
        total_energy_watt_hours=total_energy
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 