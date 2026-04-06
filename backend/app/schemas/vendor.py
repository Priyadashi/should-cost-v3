from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VendorBase(BaseModel):
    name: str
    code: Optional[str] = None
    location: Optional[str] = None
    capabilities: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    capabilities: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class VendorRead(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
