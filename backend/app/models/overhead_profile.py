from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func
from app.database import Base


class OverheadProfile(Base):
    __tablename__ = "overhead_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    is_default = Column(Boolean, default=False)
    factory_overhead_pct = Column(Float, nullable=False, default=0.12)
    admin_overhead_pct = Column(Float, nullable=False, default=0.08)
    depreciation_pct = Column(Float, nullable=False, default=0.05)
    quality_cost_pct = Column(Float, nullable=False, default=0.03)
    profit_margin_pct = Column(Float, nullable=False, default=0.10)
    taxes_duties_pct = Column(Float, nullable=False, default=0.05)
    sga_pct = Column(Float, nullable=False, default=0.08)
    packaging_per_unit = Column(Float, nullable=False, default=0)
    freight_per_unit = Column(Float, nullable=False, default=0)
    other_logistics_per_unit = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
