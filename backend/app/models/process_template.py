from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from app.database import Base


class ProcessTemplate(Base):
    __tablename__ = "process_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    commodity_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    sequence_order = Column(Integer, nullable=False, default=0)
    default_machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    default_cycle_time_min = Column(Float, nullable=True)
    default_setup_time_min = Column(Float, nullable=True)
    default_batch_size = Column(Integer, nullable=True, default=100)
    default_operators = Column(Integer, nullable=True, default=1)
    default_labor_rate_per_hr = Column(Float, nullable=True)
    default_tooling_cost_per_unit = Column(Float, nullable=True, default=0)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
