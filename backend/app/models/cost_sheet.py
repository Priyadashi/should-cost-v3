from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base


class CostSheet(Base):
    __tablename__ = "cost_sheets"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    scenario_name = Column(String(200), nullable=False, default="Base Scenario")
    scenario_group = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    quoted_price = Column(Float, nullable=True)
    supplier_name = Column(String(200), nullable=True)
    overhead_profile_id = Column(Integer, ForeignKey("overhead_profiles.id"), nullable=True)

    # JSON fields for flexible storage
    input_snapshot = Column(JSON, nullable=True)
    result_summary = Column(JSON, nullable=True)
    result_line_items = Column(JSON, nullable=True)
    sensitivity = Column(JSON, nullable=True)
    volume_analysis = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    ai_analysis = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    calculated_at = Column(DateTime(timezone=True), nullable=True)

    part = relationship("Part")
    overhead_profile = relationship("OverheadProfile")


class ExcelUpload(Base):
    __tablename__ = "excel_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    upload_status = Column(String(50), nullable=False, default="pending")
    error_log = Column(JSON, nullable=True)
    mapped_part_id = Column(Integer, ForeignKey("parts.id"), nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    changes = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
