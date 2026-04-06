from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import OverheadProfile
from app.schemas import OverheadProfileCreate, OverheadProfileUpdate, OverheadProfileRead

router = APIRouter()


@router.get("/", response_model=list[OverheadProfileRead])
def list_overhead_profiles(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(OverheadProfile).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=OverheadProfileRead)
def get_overhead_profile(id: int, db: Session = Depends(get_db)):
    op = db.query(OverheadProfile).filter(OverheadProfile.id == id).first()
    if not op:
        raise HTTPException(404, "Overhead profile not found")
    return op


@router.post("/", response_model=OverheadProfileRead, status_code=201)
def create_overhead_profile(data: OverheadProfileCreate, db: Session = Depends(get_db)):
    op = OverheadProfile(**data.model_dump())
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


@router.put("/{id}", response_model=OverheadProfileRead)
def update_overhead_profile(id: int, data: OverheadProfileUpdate, db: Session = Depends(get_db)):
    op = db.query(OverheadProfile).filter(OverheadProfile.id == id).first()
    if not op:
        raise HTTPException(404, "Overhead profile not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(op, k, v)
    db.commit()
    db.refresh(op)
    return op


@router.delete("/{id}", status_code=204)
def delete_overhead_profile(id: int, db: Session = Depends(get_db)):
    op = db.query(OverheadProfile).filter(OverheadProfile.id == id).first()
    if not op:
        raise HTTPException(404, "Overhead profile not found")
    db.delete(op)
    db.commit()
