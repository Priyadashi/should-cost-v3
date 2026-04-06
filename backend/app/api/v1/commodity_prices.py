from fastapi import APIRouter, HTTPException, Query
from app.services.commodity_price_service import get_prices_for_material, MATERIAL_TO_TICKERS

router = APIRouter()


@router.get("/")
async def fetch_commodity_prices(
    material_type: str = Query(..., description="Material type, e.g. Steel, Aluminum, Copper")
):
    """
    Fetch live commodity prices (INR/kg) for the given material type from
    MCX India and LME/COMEX sources via Yahoo Finance.
    """
    if material_type not in MATERIAL_TO_TICKERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown material type '{material_type}'. "
                   f"Valid values: {sorted(MATERIAL_TO_TICKERS.keys())}",
        )

    prices = await get_prices_for_material(material_type)
    return {
        "material_type": material_type,
        "currency": "INR",
        "unit": "INR/kg",
        "prices": prices,
    }


@router.get("/supported-types")
def supported_material_types():
    """List material types that have commodity price data available."""
    return {"material_types": sorted(MATERIAL_TO_TICKERS.keys())}
