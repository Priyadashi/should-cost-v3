from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models import CostSheet, Part, BomLine, RoutingStep, Material, Machine, OverheadProfile
from app.schemas import (
    CostSheetCreate, CostSheetUpdate, CostSheetRead, CostSheetDetail,
    CostSheetCalculateRequest, CompareRequest, CompareResponse,
)
from app.engine.calculator import calculate_should_cost
from app.engine.schemas import (
    CostSheetInput, MaterialInput, ProcessStepInput, OverheadInput, LogisticsInput,
)
from app.engine.recommendations import get_recommendations

router = APIRouter()


@router.get("/", response_model=list[CostSheetRead])
def list_cost_sheets(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db),
):
    q = db.query(CostSheet)
    if status:
        q = q.filter(CostSheet.status == status)
    sheets = q.order_by(CostSheet.updated_at.desc()).offset(skip).limit(limit).all()
    result = []
    for s in sheets:
        part = db.query(Part).filter(Part.id == s.part_id).first()
        r = CostSheetRead(
            id=s.id, part_id=s.part_id, scenario_name=s.scenario_name,
            scenario_group=s.scenario_group, status=s.status,
            quoted_price=s.quoted_price, overhead_profile_id=s.overhead_profile_id,
            result_summary=s.result_summary, calculated_at=s.calculated_at,
            created_at=s.created_at, updated_at=s.updated_at,
            part_name=part.name if part else None,
            part_no=part.part_no if part else None,
        )
        result.append(r)
    return result


@router.get("/{id}", response_model=CostSheetDetail)
def get_cost_sheet(id: int, db: Session = Depends(get_db)):
    s = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not s:
        raise HTTPException(404, "Cost sheet not found")
    part = db.query(Part).filter(Part.id == s.part_id).first()
    return CostSheetDetail(
        id=s.id, part_id=s.part_id, scenario_name=s.scenario_name,
        scenario_group=s.scenario_group, status=s.status,
        quoted_price=s.quoted_price, overhead_profile_id=s.overhead_profile_id,
        result_summary=s.result_summary, calculated_at=s.calculated_at,
        created_at=s.created_at, updated_at=s.updated_at,
        part_name=part.name if part else None, part_no=part.part_no if part else None,
        input_snapshot=s.input_snapshot, result_line_items=s.result_line_items,
        sensitivity=s.sensitivity, volume_analysis=s.volume_analysis,
        recommendations=s.recommendations, ai_analysis=s.ai_analysis,
    )


@router.post("/", response_model=CostSheetRead, status_code=201)
def create_cost_sheet(data: CostSheetCreate, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.id == data.part_id).first()
    if not part:
        raise HTTPException(404, "Part not found")
    s = CostSheet(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return CostSheetRead(
        id=s.id, part_id=s.part_id, scenario_name=s.scenario_name,
        scenario_group=s.scenario_group, status=s.status,
        quoted_price=s.quoted_price, overhead_profile_id=s.overhead_profile_id,
        result_summary=s.result_summary, calculated_at=s.calculated_at,
        created_at=s.created_at, updated_at=s.updated_at,
        part_name=part.name, part_no=part.part_no,
    )


@router.put("/{id}", response_model=CostSheetRead)
def update_cost_sheet(id: int, data: CostSheetUpdate, db: Session = Depends(get_db)):
    s = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not s:
        raise HTTPException(404, "Cost sheet not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    part = db.query(Part).filter(Part.id == s.part_id).first()
    return CostSheetRead(
        id=s.id, part_id=s.part_id, scenario_name=s.scenario_name,
        scenario_group=s.scenario_group, status=s.status,
        quoted_price=s.quoted_price, overhead_profile_id=s.overhead_profile_id,
        result_summary=s.result_summary, calculated_at=s.calculated_at,
        created_at=s.created_at, updated_at=s.updated_at,
        part_name=part.name if part else None, part_no=part.part_no if part else None,
    )


@router.delete("/{id}", status_code=204)
def delete_cost_sheet(id: int, db: Session = Depends(get_db)):
    s = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not s:
        raise HTTPException(404, "Cost sheet not found")
    db.delete(s)
    db.commit()


@router.post("/{id}/calculate", response_model=CostSheetDetail)
def calculate_cost_sheet(
    id: int,
    req: CostSheetCalculateRequest = None,
    db: Session = Depends(get_db),
):
    """Run the calculation engine on a cost sheet."""
    s = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not s:
        raise HTTPException(404, "Cost sheet not found")
    part = db.query(Part).filter(Part.id == s.part_id).first()
    if not part:
        raise HTTPException(404, "Associated part not found")

    # Build engine input from part data
    bom_lines = db.query(BomLine).filter(BomLine.part_id == part.id).all()
    routing_steps = (
        db.query(RoutingStep)
        .filter(RoutingStep.part_id == part.id)
        .order_by(RoutingStep.sequence)
        .all()
    )

    if not bom_lines:
        raise HTTPException(400, "Part has no BOM lines. Add materials before calculating.")
    if not routing_steps:
        raise HTTPException(400, "Part has no routing steps. Add process steps before calculating.")

    # Build material inputs
    materials = []
    for bl in bom_lines:
        mat = db.query(Material).filter(Material.id == bl.material_id).first()
        if not mat:
            continue
        util_rate = bl.net_weight_kg / bl.gross_weight_kg if bl.gross_weight_kg > 0 else 0.75
        materials.append(MaterialInput(
            name=mat.grade.split("(")[0].strip() if "(" in mat.grade else mat.grade,
            grade=mat.grade,
            finished_mass_kg=bl.net_weight_kg,
            utilization_rate=util_rate,
            price_per_kg=mat.rate_per_kg,
            scrap_recovery_pct=mat.scrap_recovery_pct,
            price_source="material_database",
            confidence="medium",
        ))

    # Build process step inputs
    process_steps = []
    for rs in routing_steps:
        mach = (
            db.query(Machine).filter(Machine.id == rs.machine_id).first()
            if rs.machine_id
            else None
        )
        process_steps.append(ProcessStepInput(
            step_name=rs.operation_name,
            machine_type=mach.machine_type if mach else "Unknown",
            machine_rate_per_hr=mach.hourly_rate if mach else 0,
            cycle_time_min=rs.cycle_time_min,
            setup_time_min=rs.setup_time_min,
            operators=rs.operators,
            labor_rate_per_hr=rs.labor_rate_per_hr,
            rate_source="machine_database",
            confidence="medium",
        ))

    # Build overhead input
    oh = OverheadInput()
    logistics = LogisticsInput()
    if s.overhead_profile_id:
        profile = db.query(OverheadProfile).filter(
            OverheadProfile.id == s.overhead_profile_id
        ).first()
        if profile:
            oh = OverheadInput(
                factory_overhead_pct=profile.factory_overhead_pct,
                admin_overhead_pct=profile.admin_overhead_pct,
                depreciation_pct=profile.depreciation_pct,
                quality_cost_pct=profile.quality_cost_pct,
                profit_margin_pct=profile.profit_margin_pct,
                taxes_duties_pct=profile.taxes_duties_pct,
                sga_pct=profile.sga_pct,
            )
            logistics = LogisticsInput(
                packaging_per_unit=profile.packaging_per_unit,
                freight_per_unit=profile.freight_per_unit,
                other_per_unit=profile.other_logistics_per_unit,
            )

    batch_size = req.batch_size if req else 100
    learning = req.learning_curve_factor if req else 1.0

    engine_input = CostSheetInput(
        product_name=part.name,
        currency="INR",
        current_quoted_price=s.quoted_price or 0,
        annual_volume=part.annual_volume or 1000,
        batch_size=batch_size,
        materials=materials,
        process_steps=process_steps,
        learning_curve_factor=learning,
        overhead=oh,
        logistics=logistics,
    )

    # Run calculation
    result = calculate_should_cost(engine_input)

    # Run recommendations
    recs = get_recommendations(result, commodity_type=part.commodity_type)
    recs_dicts = [
        {
            "rule_id": r.rule_id,
            "severity": r.severity,
            "title": r.title,
            "description": r.description,
            "category": r.category,
            "potential_savings_pct": r.potential_savings_pct,
        }
        for r in recs
    ]

    # Store results
    s.input_snapshot = engine_input.model_dump()
    s.result_summary = result.summary.model_dump()
    s.result_line_items = [li.model_dump() for li in result.line_items]
    s.sensitivity = [si.model_dump() for si in result.sensitivity]
    s.volume_analysis = [va.model_dump() for va in result.volume_analysis]
    s.recommendations = recs_dicts
    s.status = "calculated"
    s.calculated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(s)

    return CostSheetDetail(
        id=s.id, part_id=s.part_id, scenario_name=s.scenario_name,
        scenario_group=s.scenario_group, status=s.status,
        quoted_price=s.quoted_price, overhead_profile_id=s.overhead_profile_id,
        result_summary=s.result_summary, calculated_at=s.calculated_at,
        created_at=s.created_at, updated_at=s.updated_at,
        part_name=part.name, part_no=part.part_no,
        input_snapshot=s.input_snapshot, result_line_items=s.result_line_items,
        sensitivity=s.sensitivity, volume_analysis=s.volume_analysis,
        recommendations=s.recommendations, ai_analysis=s.ai_analysis,
    )


@router.post("/{id}/recalculate", response_model=CostSheetDetail)
def recalculate(
    id: int,
    req: CostSheetCalculateRequest = None,
    db: Session = Depends(get_db),
):
    """Alias for calculate - recalculates with latest data."""
    return calculate_cost_sheet(id, req, db)


@router.get("/{id}/results")
def get_results(id: int, db: Session = Depends(get_db)):
    s = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not s:
        raise HTTPException(404, "Cost sheet not found")
    if not s.result_summary:
        raise HTTPException(400, "Cost sheet has not been calculated yet")
    return {
        "summary": s.result_summary,
        "line_items": s.result_line_items,
        "sensitivity": s.sensitivity,
        "volume_analysis": s.volume_analysis,
        "recommendations": s.recommendations,
    }


@router.get("/{id}/recommendations")
def get_recommendations_endpoint(id: int, db: Session = Depends(get_db)):
    s = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not s:
        raise HTTPException(404, "Cost sheet not found")
    return s.recommendations or []


@router.post("/compare")
def compare_sheets(req: CompareRequest, db: Session = Depends(get_db)):
    sheets = []
    for sid in req.sheet_ids:
        s = db.query(CostSheet).filter(CostSheet.id == sid).first()
        if not s:
            raise HTTPException(404, f"Cost sheet {sid} not found")
        if not s.result_summary:
            raise HTTPException(400, f"Cost sheet {sid} has not been calculated")
        part = db.query(Part).filter(Part.id == s.part_id).first()
        sheets.append({
            "id": s.id,
            "scenario_name": s.scenario_name,
            "part_name": part.name if part else None,
            "summary": s.result_summary,
            "line_items": s.result_line_items,
        })

    # Compute deltas between consecutive sheets
    deltas = []
    if len(sheets) >= 2:
        base = sheets[0]["summary"]
        for comp in sheets[1:]:
            comp_sum = comp["summary"]
            delta = {}
            for key in base:
                if isinstance(base[key], (int, float)) and isinstance(
                    comp_sum.get(key), (int, float)
                ):
                    delta[key] = round(comp_sum[key] - base[key], 2)
            deltas.append({
                "base_id": sheets[0]["id"],
                "compare_id": comp["id"],
                "deltas": delta,
            })

    return {"sheets": sheets, "deltas": deltas}


@router.post("/{id}/ai-analysis")
def generate_ai_analysis(id: int, db: Session = Depends(get_db)):
    """On-demand AI analysis using OpenAI."""
    s = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not s:
        raise HTTPException(404, "Cost sheet not found")
    if not s.result_summary:
        raise HTTPException(400, "Cost sheet has not been calculated yet")

    from app.services.ai_analysis_service import get_ai_analysis
    part = db.query(Part).filter(Part.id == s.part_id).first()

    analysis = get_ai_analysis(
        result_summary=s.result_summary,
        line_items=s.result_line_items or [],
        recommendations=s.recommendations or [],
        product_name=part.name if part else "Unknown",
        currency="INR",
    )

    if analysis is None:
        raise HTTPException(400, "OpenAI API key not configured. Set OPENAI_API_KEY in .env")

    s.ai_analysis = analysis
    db.commit()
    return analysis
