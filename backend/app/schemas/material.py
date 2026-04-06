from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MaterialBase(BaseModel):
    grade: str
    material_type: str = "Steel"
    density_kg_m3: Optional[float] = None
    rate_per_kg: float
    currency: str = "INR"
    region: Optional[str] = None
    scrap_recovery_pct: float = 0.35
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    grade: Optional[str] = None
    material_type: Optional[str] = None
    density_kg_m3: Optional[float] = None
    rate_per_kg: Optional[float] = None
    currency: Optional[str] = None
    region: Optional[str] = None
    scrap_recovery_pct: Optional[float] = None
    description: Optional[str] = None


class MaterialRead(MaterialBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
