from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/s4hana/sync-materials")
def sync_materials():
    raise HTTPException(501, "S/4HANA integration not yet implemented")


@router.post("/s4hana/sync-bom")
def sync_bom():
    raise HTTPException(501, "S/4HANA integration not yet implemented")


@router.get("/s4hana/status")
def s4hana_status():
    raise HTTPException(501, "S/4HANA integration not yet implemented")
