from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import CostSheet, Part, Material, Machine

router = APIRouter()


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    total_sheets = db.query(func.count(CostSheet.id)).scalar() or 0
    calculated = (
        db.query(func.count(CostSheet.id))
        .filter(CostSheet.status == "calculated")
        .scalar()
        or 0
    )
    draft = (
        db.query(func.count(CostSheet.id))
        .filter(CostSheet.status == "draft")
        .scalar()
        or 0
    )
    total_parts = db.query(func.count(Part.id)).scalar() or 0
    total_materials = db.query(func.count(Material.id)).scalar() or 0
    total_machines = db.query(func.count(Machine.id)).scalar() or 0

    # Calculate total opportunity from calculated sheets
    sheets = db.query(CostSheet).filter(CostSheet.result_summary.isnot(None)).all()
    total_opportunity = sum(
        (s.result_summary or {}).get("annual_opportunity", 0) for s in sheets
    )

    return {
        "total_cost_sheets": total_sheets,
        "calculated_sheets": calculated,
        "draft_sheets": draft,
        "total_parts": total_parts,
        "total_materials": total_materials,
        "total_machines": total_machines,
        "total_annual_opportunity": round(total_opportunity, 2),
    }


@router.get("/recent-activity")
def recent_activity(limit: int = 10, db: Session = Depends(get_db)):
    sheets = (
        db.query(CostSheet).order_by(CostSheet.updated_at.desc()).limit(limit).all()
    )
    result = []
    for s in sheets:
        part = db.query(Part).filter(Part.id == s.part_id).first()
        result.append({
            "id": s.id,
            "type": "cost_sheet",
            "scenario_name": s.scenario_name,
            "part_name": part.name if part else "Unknown",
            "part_no": part.part_no if part else "",
            "status": s.status,
            "should_cost": (s.result_summary or {}).get("should_cost"),
            "gap_pct": (s.result_summary or {}).get("gap_pct"),
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        })
    return result
