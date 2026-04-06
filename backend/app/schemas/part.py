from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BomLineBase(BaseModel):
    material_id: int
    gross_weight_kg: float
    net_weight_kg: float
    scrap_rate_per_kg: float = 0
    notes: Optional[str] = None


class BomLineCreate(BomLineBase):
    pass


class BomLineRead(BomLineBase):
    id: int
    part_id: int
    material_grade: Optional[str] = None
    material_rate: Optional[float] = None

    model_config = {"from_attributes": True}


class RoutingStepBase(BaseModel):
    sequence: int
    operation_name: str
    machine_id: Optional[int] = None
    cycle_time_min: float = 0
    setup_time_min: float = 0
    batch_size: int = 100
    operators: int = 1
    labor_rate_per_hr: float = 0
    tooling_cost_per_unit: float = 0
    notes: Optional[str] = None


class RoutingStepCreate(RoutingStepBase):
    pass


class RoutingStepRead(RoutingStepBase):
    id: int
    part_id: int
    machine_name: Optional[str] = None
    machine_rate: Optional[float] = None

    model_config = {"from_attributes": True}


class PartBase(BaseModel):
    part_no: str
    name: str
    commodity_type: str = "Forging"
    annual_volume: Optional[int] = None
    description: Optional[str] = None


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    part_no: Optional[str] = None
    name: Optional[str] = None
    commodity_type: Optional[str] = None
    annual_volume: Optional[int] = None
    description: Optional[str] = None


class PartRead(PartBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PartDetail(PartRead):
    bom_lines: list[BomLineRead] = []
    routing_steps: list[RoutingStepRead] = []
