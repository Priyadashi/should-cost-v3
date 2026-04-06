from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OverheadProfileBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False
    factory_overhead_pct: float = 0.12
    admin_overhead_pct: float = 0.08
    depreciation_pct: float = 0.05
    quality_cost_pct: float = 0.03
    profit_margin_pct: float = 0.10
    taxes_duties_pct: float = 0.05
    sga_pct: float = 0.08
    packaging_per_unit: float = 0
    freight_per_unit: float = 0
    other_logistics_per_unit: float = 0


class OverheadProfileCreate(OverheadProfileBase):
    pass


class OverheadProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    factory_overhead_pct: Optional[float] = None
    admin_overhead_pct: Optional[float] = None
    depreciation_pct: Optional[float] = None
    quality_cost_pct: Optional[float] = None
    profit_margin_pct: Optional[float] = None
    taxes_duties_pct: Optional[float] = None
    sga_pct: Optional[float] = None
    packaging_per_unit: Optional[float] = None
    freight_per_unit: Optional[float] = None
    other_logistics_per_unit: Optional[float] = None


class OverheadProfileRead(OverheadProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
