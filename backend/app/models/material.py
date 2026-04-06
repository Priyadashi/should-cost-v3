from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(String(200), nullable=False)
    material_type = Column(String(100), nullable=False, default="Steel")
    density_kg_m3 = Column(Float, nullable=True)
    rate_per_kg = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="INR")
    region = Column(String(100), nullable=True)
    scrap_recovery_pct = Column(Float, nullable=False, default=0.35)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
