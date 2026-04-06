from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class CostSheetBase(BaseModel):
    part_id: int
    scenario_name: str = "Base Scenario"
    scenario_group: Optional[str] = None
    quoted_price: Optional[float] = None
    overhead_profile_id: Optional[int] = None


class CostSheetCreate(CostSheetBase):
    pass


class CostSheetUpdate(BaseModel):
    scenario_name: Optional[str] = None
    scenario_group: Optional[str] = None
    status: Optional[str] = None
    quoted_price: Optional[float] = None
    overhead_profile_id: Optional[int] = None


class CostSheetRead(CostSheetBase):
    id: int
    status: str
    result_summary: Optional[dict] = None
    calculated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    part_name: Optional[str] = None
    part_no: Optional[str] = None

    model_config = {"from_attributes": True}


class CostSheetDetail(CostSheetRead):
    input_snapshot: Optional[dict] = None
    result_line_items: Optional[list[dict]] = None
    sensitivity: Optional[list[dict]] = None
    volume_analysis: Optional[list[dict]] = None
    recommendations: Optional[list[dict]] = None
    ai_analysis: Optional[dict] = None


class CostSheetCalculateRequest(BaseModel):
    """Optional overrides for calculation"""
    bom_overrides: Optional[list[dict]] = None
    routing_overrides: Optional[list[dict]] = None
    overhead_overrides: Optional[dict] = None
    learning_curve_factor: float = 1.0
    batch_size: int = 100


class CompareRequest(BaseModel):
    sheet_ids: list[int]


class CompareResponse(BaseModel):
    sheets: list[dict]
    deltas: list[dict]
