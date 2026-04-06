from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ExcelUpload, CostSheet, Part
from app.services.excel_service import generate_cost_sheet_excel, generate_template_excel, ForgingExcelParser

router = APIRouter()


@router.post("/upload")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Only Excel files (.xlsx, .xls) are accepted")
    contents = await file.read()

    upload = ExcelUpload(filename=file.filename, upload_status="processing")
    db.add(upload)
    db.commit()
    db.refresh(upload)

    try:
        parsed = ForgingExcelParser.parse(contents)
        upload.raw_data = parsed
        upload.upload_status = "completed"
        if parsed.get("errors"):
            upload.error_log = parsed["errors"]
    except Exception as e:
        upload.upload_status = "failed"
        upload.error_log = [str(e)]

    db.commit()
    return {"id": upload.id, "filename": upload.filename, "status": upload.upload_status, "data": upload.raw_data}


@router.get("/upload/{id}/status")
def upload_status(id: int, db: Session = Depends(get_db)):
    upload = db.query(ExcelUpload).filter(ExcelUpload.id == id).first()
    if not upload:
        raise HTTPException(404, "Upload not found")
    return {
        "id": upload.id,
        "filename": upload.filename,
        "status": upload.upload_status,
        "errors": upload.error_log,
        "data": upload.raw_data,
    }


@router.get("/download/template")
def download_template():
    content = generate_template_excel()
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=should_cost_template.xlsx"},
    )


@router.get("/download/cost-sheet/{id}")
def download_cost_sheet(id: int, db: Session = Depends(get_db)):
    sheet = db.query(CostSheet).filter(CostSheet.id == id).first()
    if not sheet:
        raise HTTPException(404, "Cost sheet not found")
    if not sheet.result_summary:
        raise HTTPException(400, "Cost sheet has not been calculated")

    part = db.query(Part).filter(Part.id == sheet.part_id).first()
    content = generate_cost_sheet_excel(
        summary=sheet.result_summary,
        line_items=sheet.result_line_items or [],
        sensitivity=sheet.sensitivity or [],
        volume_analysis=sheet.volume_analysis or [],
        part_name=part.name if part else "Unknown",
        scenario_name=sheet.scenario_name,
    )
    filename = f"should_cost_{part.part_no if part else 'unknown'}_{sheet.scenario_name}.xlsx".replace(" ", "_")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
