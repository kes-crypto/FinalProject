# main.py - FastAPI backend for ingestion and simple queries
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
import models, db
import datetime

# Ensure tables exist
models.Base.metadata.create_all(bind=db.engine)

app = FastAPI(title="Agri Data Platform")

class IngestPayload(BaseModel):
    sensor_id: str = Field(..., example="field-1-sensor-A")
    location: Optional[str] = None
    timestamp: Optional[datetime.datetime] = None
    soil_moisture: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    ph: Optional[float] = None
    crop: Optional[str] = None

class ReadingOut(BaseModel):
    sensor_id: str
    timestamp: datetime.datetime
    soil_moisture: Optional[float]
    temperature: Optional[float]
    humidity: Optional[float]
    ph: Optional[float]
    crop: Optional[str]

def get_or_create_sensor(db: Session, sensor_id: str, location: Optional[str]=None):
    s = db.query(models.Sensor).filter(models.Sensor.sensor_id==sensor_id).first()
    if s:
        # update location if provided and changed
        if location and s.location != location:
            s.location = location
            db.commit()
            db.refresh(s)
        return s
    s = models.Sensor(sensor_id=sensor_id, location=location)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@app.post("/ingest", status_code=201)
def ingest(payload: IngestPayload, db: Session = Depends(db.get_db)):
    # Convert timestamp if provided (Pydantic will already parse ISO strings to datetime)
    ts = payload.timestamp or datetime.datetime.utcnow()
    sensor = get_or_create_sensor(db, payload.sensor_id, payload.location)
    r = models.Reading(
        sensor_id=sensor.id,
        timestamp=ts,
        soil_moisture=payload.soil_moisture,
        temperature=payload.temperature,
        humidity=payload.humidity,
        ph=payload.ph,
        crop=payload.crop
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"status":"ok","reading_id": r.id}

@app.get("/api/latest", response_model=List[ReadingOut])
def latest(limit: int = 50, db: Session = Depends(db.get_db)):
    q = db.query(models.Reading, models.Sensor).join(models.Sensor).order_by(models.Reading.timestamp.desc()).limit(limit).all()
    out = []
    for reading, sensor in q:
        out.append(ReadingOut(
            sensor_id=sensor.sensor_id,
            timestamp=reading.timestamp,
            soil_moisture=reading.soil_moisture,
            temperature=reading.temperature,
            humidity=reading.humidity,
            ph=reading.ph,
            crop=reading.crop
        ))
    return out

@app.get("/api/timeseries")
def timeseries(sensor_id: str, since_minutes: int = 1440, db: Session = Depends(db.get_db)):
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(minutes=since_minutes)
    sensor = db.query(models.Sensor).filter(models.Sensor.sensor_id==sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    rows = db.query(models.Reading).filter(models.Reading.sensor_id==sensor.id, models.Reading.timestamp>=since).order_by(models.Reading.timestamp).all()
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "soil_moisture": r.soil_moisture,
            "temperature": r.temperature,
            "humidity": r.humidity,
            "ph": r.ph,
            "crop": r.crop
        } for r in rows
    ]
