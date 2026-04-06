from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MachineBase(BaseModel):
    name: str
    machine_type: str
    hourly_rate: float
    currency: str = "INR"
    power_kw: Optional[float] = None
    commodity_types: Optional[list[str]] = None
    description: Optional[str] = None


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    machine_type: Optional[str] = None
    hourly_rate: Optional[float] = None
    currency: Optional[str] = None
    power_kw: Optional[float] = None
    commodity_types: Optional[list[str]] = None
    description: Optional[str] = None


class MachineRead(MachineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
