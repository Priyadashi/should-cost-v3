from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Machine
from app.schemas import MachineCreate, MachineUpdate, MachineRead

router = APIRouter()


@router.get("/", response_model=list[MachineRead])
def list_machines(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Machine).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=MachineRead)
def get_machine(id: int, db: Session = Depends(get_db)):
    m = db.query(Machine).filter(Machine.id == id).first()
    if not m:
        raise HTTPException(404, "Machine not found")
    return m


@router.post("/", response_model=MachineRead, status_code=201)
def create_machine(data: MachineCreate, db: Session = Depends(get_db)):
    m = Machine(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/{id}", response_model=MachineRead)
def update_machine(id: int, data: MachineUpdate, db: Session = Depends(get_db)):
    m = db.query(Machine).filter(Machine.id == id).first()
    if not m:
        raise HTTPException(404, "Machine not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/{id}", status_code=204)
def delete_machine(id: int, db: Session = Depends(get_db)):
    m = db.query(Machine).filter(Machine.id == id).first()
    if not m:
        raise HTTPException(404, "Machine not found")
    db.delete(m)
    db.commit()
