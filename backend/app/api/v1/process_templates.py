from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ProcessTemplate
from app.schemas import ProcessTemplateCreate, ProcessTemplateUpdate, ProcessTemplateRead

router = APIRouter()


@router.get("/", response_model=list[ProcessTemplateRead])
def list_process_templates(
    skip: int = 0,
    limit: int = 50,
    commodity_type: str = None,
    db: Session = Depends(get_db),
):
    q = db.query(ProcessTemplate)
    if commodity_type:
        q = q.filter(ProcessTemplate.commodity_type == commodity_type)
    return q.offset(skip).limit(limit).all()


@router.get("/{id}", response_model=ProcessTemplateRead)
def get_process_template(id: int, db: Session = Depends(get_db)):
    pt = db.query(ProcessTemplate).filter(ProcessTemplate.id == id).first()
    if not pt:
        raise HTTPException(404, "Process template not found")
    return pt


@router.post("/", response_model=ProcessTemplateRead, status_code=201)
def create_process_template(data: ProcessTemplateCreate, db: Session = Depends(get_db)):
    pt = ProcessTemplate(**data.model_dump())
    db.add(pt)
    db.commit()
    db.refresh(pt)
    return pt


@router.put("/{id}", response_model=ProcessTemplateRead)
def update_process_template(id: int, data: ProcessTemplateUpdate, db: Session = Depends(get_db)):
    pt = db.query(ProcessTemplate).filter(ProcessTemplate.id == id).first()
    if not pt:
        raise HTTPException(404, "Process template not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(pt, k, v)
    db.commit()
    db.refresh(pt)
    return pt


@router.delete("/{id}", status_code=204)
def delete_process_template(id: int, db: Session = Depends(get_db)):
    pt = db.query(ProcessTemplate).filter(ProcessTemplate.id == id).first()
    if not pt:
        raise HTTPException(404, "Process template not found")
    db.delete(pt)
    db.commit()
