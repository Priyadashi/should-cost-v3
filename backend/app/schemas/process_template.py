from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProcessTemplateBase(BaseModel):
    name: str
    commodity_type: str
    category: Optional[str] = None
    sequence_order: int = 0
    default_machine_id: Optional[int] = None
    default_cycle_time_min: Optional[float] = None
    default_setup_time_min: Optional[float] = None
    default_labor_rate_per_hr: Optional[float] = None
    description: Optional[str] = None


class ProcessTemplateCreate(ProcessTemplateBase):
    pass


class ProcessTemplateUpdate(BaseModel):
    name: Optional[str] = None
    commodity_type: Optional[str] = None
    category: Optional[str] = None
    sequence_order: Optional[int] = None
    default_machine_id: Optional[int] = None
    default_cycle_time_min: Optional[float] = None
    default_setup_time_min: Optional[float] = None
    default_labor_rate_per_hr: Optional[float] = None
    description: Optional[str] = None


class ProcessTemplateRead(ProcessTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
