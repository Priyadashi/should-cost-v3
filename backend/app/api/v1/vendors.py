from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Vendor
from app.schemas import VendorCreate, VendorUpdate, VendorRead

router = APIRouter()


@router.get("/", response_model=list[VendorRead])
def list_vendors(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Vendor).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=VendorRead)
def get_vendor(id: int, db: Session = Depends(get_db)):
    v = db.query(Vendor).filter(Vendor.id == id).first()
    if not v:
        raise HTTPException(404, "Vendor not found")
    return v


@router.post("/", response_model=VendorRead, status_code=201)
def create_vendor(data: VendorCreate, db: Session = Depends(get_db)):
    v = Vendor(**data.model_dump())
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


@router.put("/{id}", response_model=VendorRead)
def update_vendor(id: int, data: VendorUpdate, db: Session = Depends(get_db)):
    v = db.query(Vendor).filter(Vendor.id == id).first()
    if not v:
        raise HTTPException(404, "Vendor not found")
    for k, v_val in data.model_dump(exclude_unset=True).items():
        setattr(v, k, v_val)
    db.commit()
    db.refresh(v)
    return v


@router.delete("/{id}", status_code=204)
def delete_vendor(id: int, db: Session = Depends(get_db)):
    v = db.query(Vendor).filter(Vendor.id == id).first()
    if not v:
        raise HTTPException(404, "Vendor not found")
    db.delete(v)
    db.commit()
