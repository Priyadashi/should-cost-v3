from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base, SessionLocal
from app.models import *  # noqa: register all models
from app.api.v1 import materials, machines, vendors, process_templates, overhead_profiles, parts, cost_sheets, excel, dashboard, integrations, commodity_prices

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    # Seed data
    db = SessionLocal()
    try:
        from app.seed.seed_data import seed_database
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Should-Cost Modeling Platform",
    version="1.0.0",
    description="Manufacturing should-cost analysis platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Master data
app.include_router(materials.router, prefix="/api/v1/materials", tags=["Materials"])
app.include_router(machines.router, prefix="/api/v1/machines", tags=["Machines"])
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["Vendors"])
app.include_router(process_templates.router, prefix="/api/v1/process-templates", tags=["Process Templates"])
app.include_router(overhead_profiles.router, prefix="/api/v1/overhead-profiles", tags=["Overhead Profiles"])

# Parts + BOM + Routing
app.include_router(parts.router, prefix="/api/v1/parts", tags=["Parts"])

# Cost Sheets
app.include_router(cost_sheets.router, prefix="/api/v1/cost-sheets", tags=["Cost Sheets"])

# Excel
app.include_router(excel.router, prefix="/api/v1/excel", tags=["Excel"])

# Dashboard
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

# Integrations
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])

# Commodity prices (live market data)
app.include_router(commodity_prices.router, prefix="/api/v1/commodity-prices", tags=["Commodity Prices"])


@app.get("/api/health")
def health():
    return {"status": "ok", "ping": "pong"}
