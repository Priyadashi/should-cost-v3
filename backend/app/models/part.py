from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    part_no = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    commodity_type = Column(String(100), nullable=False, default="Forging")
    annual_volume = Column(Integer, nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bom_lines = relationship("BomLine", back_populates="part", cascade="all, delete-orphan")
    routing_steps = relationship("RoutingStep", back_populates="part", cascade="all, delete-orphan", order_by="RoutingStep.sequence")


class BomLine(Base):
    __tablename__ = "bom_lines"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    gross_weight_kg = Column(Float, nullable=False)
    net_weight_kg = Column(Float, nullable=False)
    scrap_rate_per_kg = Column(Float, nullable=True, default=0)
    notes = Column(String(500), nullable=True)

    part = relationship("Part", back_populates="bom_lines")
    material = relationship("Material")


class RoutingStep(Base):
    __tablename__ = "routing_steps"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False)
    sequence = Column(Integer, nullable=False)
    operation_name = Column(String(200), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    cycle_time_min = Column(Float, nullable=False, default=0)
    setup_time_min = Column(Float, nullable=False, default=0)
    batch_size = Column(Integer, nullable=False, default=100)
    operators = Column(Integer, nullable=False, default=1)
    labor_rate_per_hr = Column(Float, nullable=False, default=0)
    tooling_cost_per_unit = Column(Float, nullable=False, default=0)
    notes = Column(String(500), nullable=True)

    part = relationship("Part", back_populates="routing_steps")
    machine = relationship("Machine")
