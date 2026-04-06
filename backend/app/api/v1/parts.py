from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Part, BomLine, RoutingStep, Material, Machine
from app.schemas import (
    PartCreate, PartUpdate, PartRead, PartDetail,
    BomLineCreate, BomLineRead, RoutingStepCreate, RoutingStepRead,
)

router = APIRouter()


@router.get("/", response_model=list[PartRead])
def list_parts(
    skip: int = 0,
    limit: int = 50,
    commodity_type: str = None,
    db: Session = Depends(get_db),
):
    q = db.query(Part)
    if commodity_type:
        q = q.filter(Part.commodity_type == commodity_type)
    return q.offset(skip).limit(limit).all()


@router.get("/{id}", response_model=PartDetail)
def get_part(id: int, db: Session = Depends(get_db)):
    p = db.query(Part).filter(Part.id == id).first()
    if not p:
        raise HTTPException(404, "Part not found")
    # Build response with enriched BOM and routing
    bom = []
    for bl in p.bom_lines:
        mat = db.query(Material).filter(Material.id == bl.material_id).first()
        bom.append(BomLineRead(
            id=bl.id, part_id=bl.part_id, material_id=bl.material_id,
            gross_weight_kg=bl.gross_weight_kg, net_weight_kg=bl.net_weight_kg,
            scrap_rate_per_kg=bl.scrap_rate_per_kg, notes=bl.notes,
            material_grade=mat.grade if mat else None,
            material_rate=mat.rate_per_kg if mat else None,
        ))
    routing = []
    for rs in p.routing_steps:
        mach = db.query(Machine).filter(Machine.id == rs.machine_id).first() if rs.machine_id else None
        routing.append(RoutingStepRead(
            id=rs.id, part_id=rs.part_id, sequence=rs.sequence,
            operation_name=rs.operation_name, machine_id=rs.machine_id,
            cycle_time_min=rs.cycle_time_min, setup_time_min=rs.setup_time_min,
            batch_size=rs.batch_size, operators=rs.operators,
            labor_rate_per_hr=rs.labor_rate_per_hr,
            tooling_cost_per_unit=rs.tooling_cost_per_unit, notes=rs.notes,
            machine_name=mach.name if mach else None,
            machine_rate=mach.hourly_rate if mach else None,
        ))
    return PartDetail(
        id=p.id, part_no=p.part_no, name=p.name, commodity_type=p.commodity_type,
        annual_volume=p.annual_volume, description=p.description,
        created_at=p.created_at, updated_at=p.updated_at,
        bom_lines=bom, routing_steps=routing,
    )


@router.post("/", response_model=PartRead, status_code=201)
def create_part(data: PartCreate, db: Session = Depends(get_db)):
    p = Part(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{id}", response_model=PartRead)
def update_part(id: int, data: PartUpdate, db: Session = Depends(get_db)):
    p = db.query(Part).filter(Part.id == id).first()
    if not p:
        raise HTTPException(404, "Part not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{id}", status_code=204)
def delete_part(id: int, db: Session = Depends(get_db)):
    p = db.query(Part).filter(Part.id == id).first()
    if not p:
        raise HTTPException(404, "Part not found")
    db.delete(p)
    db.commit()


# BOM endpoints - replace-all pattern
@router.get("/{id}/bom", response_model=list[BomLineRead])
def get_bom(id: int, db: Session = Depends(get_db)):
    p = db.query(Part).filter(Part.id == id).first()
    if not p:
        raise HTTPException(404, "Part not found")
    result = []
    for bl in p.bom_lines:
        mat = db.query(Material).filter(Material.id == bl.material_id).first()
        result.append(BomLineRead(
            id=bl.id, part_id=bl.part_id, material_id=bl.material_id,
            gross_weight_kg=bl.gross_weight_kg, net_weight_kg=bl.net_weight_kg,
            scrap_rate_per_kg=bl.scrap_rate_per_kg, notes=bl.notes,
            material_grade=mat.grade if mat else None,
            material_rate=mat.rate_per_kg if mat else None,
        ))
    return result


@router.put("/{id}/bom", response_model=list[BomLineRead])
def replace_bom(id: int, lines: list[BomLineCreate], db: Session = Depends(get_db)):
    p = db.query(Part).filter(Part.id == id).first()
    if not p:
        raise HTTPException(404, "Part not found")
    # Delete existing
    db.query(BomLine).filter(BomLine.part_id == id).delete()
    # Create new
    new_lines = []
    for line in lines:
        bl = BomLine(part_id=id, **line.model_dump())
        db.add(bl)
        new_lines.append(bl)
    db.commit()
    result = []
    for bl in new_lines:
        db.refresh(bl)
        mat = db.query(Material).filter(Material.id == bl.material_id).first()
        result.append(BomLineRead(
            id=bl.id, part_id=bl.part_id, material_id=bl.material_id,
            gross_weight_kg=bl.gross_weight_kg, net_weight_kg=bl.net_weight_kg,
            scrap_rate_per_kg=bl.scrap_rate_per_kg, notes=bl.notes,
            material_grade=mat.grade if mat else None,
            material_rate=mat.rate_per_kg if mat else None,
        ))
    return result


# Routing endpoints - replace-all pattern
@router.get("/{id}/routing", response_model=list[RoutingStepRead])
def get_routing(id: int, db: Session = Depends(get_db)):
    p = db.query(Part).filter(Part.id == id).first()
    if not p:
        raise HTTPException(404, "Part not found")
    result = []
    for rs in p.routing_steps:
        mach = db.query(Machine).filter(Machine.id == rs.machine_id).first() if rs.machine_id else None
        result.append(RoutingStepRead(
            id=rs.id, part_id=rs.part_id, sequence=rs.sequence,
            operation_name=rs.operation_name, machine_id=rs.machine_id,
            cycle_time_min=rs.cycle_time_min, setup_time_min=rs.setup_time_min,
            batch_size=rs.batch_size, operators=rs.operators,
            labor_rate_per_hr=rs.labor_rate_per_hr,
            tooling_cost_per_unit=rs.tooling_cost_per_unit, notes=rs.notes,
            machine_name=mach.name if mach else None,
            machine_rate=mach.hourly_rate if mach else None,
        ))
    return result


@router.put("/{id}/routing", response_model=list[RoutingStepRead])
def replace_routing(id: int, steps: list[RoutingStepCreate], db: Session = Depends(get_db)):
    p = db.query(Part).filter(Part.id == id).first()
    if not p:
        raise HTTPException(404, "Part not found")
    db.query(RoutingStep).filter(RoutingStep.part_id == id).delete()
    new_steps = []
    for step in steps:
        rs = RoutingStep(part_id=id, **step.model_dump())
        db.add(rs)
        new_steps.append(rs)
    db.commit()
    result = []
    for rs in new_steps:
        db.refresh(rs)
        mach = db.query(Machine).filter(Machine.id == rs.machine_id).first() if rs.machine_id else None
        result.append(RoutingStepRead(
            id=rs.id, part_id=rs.part_id, sequence=rs.sequence,
            operation_name=rs.operation_name, machine_id=rs.machine_id,
            cycle_time_min=rs.cycle_time_min, setup_time_min=rs.setup_time_min,
            batch_size=rs.batch_size, operators=rs.operators,
            labor_rate_per_hr=rs.labor_rate_per_hr,
            tooling_cost_per_unit=rs.tooling_cost_per_unit, notes=rs.notes,
            machine_name=mach.name if mach else None,
            machine_rate=mach.hourly_rate if mach else None,
        ))
    return result
