# models.py - SQLAlchemy models for sensors and readings
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, unique=True, index=True)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    readings = relationship("Reading", back_populates="sensor", cascade="all, delete-orphan")

class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    soil_moisture = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    crop = Column(String, nullable=True)

    sensor = relationship("Sensor", back_populates="readings")
