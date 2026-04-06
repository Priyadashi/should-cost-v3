from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Material
from app.schemas import MaterialCreate, MaterialUpdate, MaterialRead

router = APIRouter()


@router.get("/", response_model=list[MaterialRead])
def list_materials(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Material).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=MaterialRead)
def get_material(id: int, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.id == id).first()
    if not m:
        raise HTTPException(404, "Material not found")
    return m


@router.post("/", response_model=MaterialRead, status_code=201)
def create_material(data: MaterialCreate, db: Session = Depends(get_db)):
    m = Material(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/{id}", response_model=MaterialRead)
def update_material(id: int, data: MaterialUpdate, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.id == id).first()
    if not m:
        raise HTTPException(404, "Material not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/{id}", status_code=204)
def delete_material(id: int, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.id == id).first()
    if not m:
        raise HTTPException(404, "Material not found")
    db.delete(m)
    db.commit()
