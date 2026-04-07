"""
API integration tests using SQLite in-memory DB (no Docker needed).
Run: cd backend && pytest tests/test_api.py -v
"""
import pytest
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.migrations import run_migrations
import app.models  # noqa: ensure all models are registered with Base

# ── In-memory SQLite for tests (StaticPool shares one connection) ─────────────
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True, scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Build a minimal test app (no lifespan seed, no real DB engine)
from app.api.v1 import (
    materials, machines, vendors, process_templates,
    overhead_profiles, parts, cost_sheets, dashboard,
)

test_app = FastAPI()
test_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
                        allow_methods=["*"], allow_headers=["*"])
test_app.include_router(materials.router,         prefix="/api/v1/materials")
test_app.include_router(machines.router,          prefix="/api/v1/machines")
test_app.include_router(vendors.router,           prefix="/api/v1/vendors")
test_app.include_router(process_templates.router, prefix="/api/v1/process-templates")
test_app.include_router(overhead_profiles.router, prefix="/api/v1/overhead-profiles")
test_app.include_router(parts.router,             prefix="/api/v1/parts")
test_app.include_router(cost_sheets.router,       prefix="/api/v1/cost-sheets")

@test_app.get("/api/health")
def health():
    return {"status": "ok", "ping": "pong"}


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c
    test_app.dependency_overrides.clear()


# ── Materials ─────────────────────────────────────────────────────────────────

def test_create_and_list_material(client):
    r = client.post("/api/v1/materials/", json={
        "grade": "EN8 (Medium Carbon Steel)",
        "material_type": "Steel",
        "rate_per_kg": 68.0,
        "scrap_recovery_pct": 0.35,
        "currency": "INR",
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["grade"] == "EN8 (Medium Carbon Steel)"
    assert data["rate_per_kg"] == 68.0

    r2 = client.get("/api/v1/materials/")
    assert r2.status_code == 200
    assert any(m["grade"] == "EN8 (Medium Carbon Steel)" for m in r2.json())


def test_update_material(client):
    r = client.post("/api/v1/materials/", json={
        "grade": "SS304 (Stainless Steel)", "material_type": "Steel",
        "rate_per_kg": 200.0, "scrap_recovery_pct": 0.40, "currency": "INR",
    })
    mid = r.json()["id"]
    r2 = client.put(f"/api/v1/materials/{mid}", json={"rate_per_kg": 215.0})
    assert r2.status_code == 200
    assert r2.json()["rate_per_kg"] == 215.0


def test_delete_material(client):
    r = client.post("/api/v1/materials/", json={
        "grade": "TO_DELETE", "material_type": "Steel",
        "rate_per_kg": 50.0, "scrap_recovery_pct": 0.30, "currency": "INR",
    })
    mid = r.json()["id"]
    assert client.delete(f"/api/v1/materials/{mid}").status_code == 204
    assert client.get(f"/api/v1/materials/{mid}").status_code == 404


# ── Machines ──────────────────────────────────────────────────────────────────

def test_create_and_list_machine(client):
    r = client.post("/api/v1/machines/", json={
        "name": "CNC Machining Center", "machine_type": "CNC",
        "hourly_rate": 1800.0, "currency": "INR",
        "commodity_types": ["Forging", "Casting"],
    })
    assert r.status_code == 201, r.text
    assert r.json()["hourly_rate"] == 1800.0

    r2 = client.get("/api/v1/machines/")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


# ── Vendors ───────────────────────────────────────────────────────────────────

def test_create_and_list_vendor(client):
    r = client.post("/api/v1/vendors/", json={
        "name": "Bharat Forge Ltd", "code": "BFL",
        "location": "Pune, India",
        "capabilities": ["Forging", "CNC Machining"],
        "certifications": ["ISO 9001", "IATF 16949"],
    })
    assert r.status_code == 201, r.text
    assert r.json()["name"] == "Bharat Forge Ltd"

    r2 = client.get("/api/v1/vendors/")
    assert r2.status_code == 200
    assert any(v["code"] == "BFL" for v in r2.json())


# ── Process Templates ─────────────────────────────────────────────────────────

def test_create_process_template(client):
    r = client.post("/api/v1/process-templates/", json={
        "name": "Billet Cutting",
        "commodity_type": "Forging",
        "category": "Preparation",
        "sequence_order": 10,
        "default_cycle_time_min": 3.0,
        "default_setup_time_min": 15.0,
        "default_batch_size": 200,
        "default_operators": 1,
        "default_labor_rate_per_hr": 350.0,
        "default_tooling_cost_per_unit": 2.0,
    })
    assert r.status_code == 201, r.text
    d = r.json()
    assert d["name"] == "Billet Cutting"
    assert d["default_batch_size"] == 200
    assert d["default_operators"] == 1


def test_list_process_templates_by_commodity(client):
    # Create forging template
    client.post("/api/v1/process-templates/", json={
        "name": "Forging Press", "commodity_type": "Forging",
        "sequence_order": 30, "default_cycle_time_min": 2.0,
        "default_batch_size": 100, "default_operators": 2,
    })
    # Create casting template
    client.post("/api/v1/process-templates/", json={
        "name": "Sand Moulding", "commodity_type": "Casting",
        "sequence_order": 10, "default_cycle_time_min": 20.0,
        "default_batch_size": 10, "default_operators": 2,
    })
    r = client.get("/api/v1/process-templates/?commodity_type=Casting")
    assert r.status_code == 200
    assert all(t["commodity_type"] == "Casting" for t in r.json())


# ── Overhead Profiles ─────────────────────────────────────────────────────────

def test_create_overhead_profile(client):
    r = client.post("/api/v1/overhead-profiles/", json={
        "name": "India - Standard Forging",
        "factory_overhead_pct": 0.12,
        "admin_overhead_pct": 0.08,
        "depreciation_pct": 0.05,
        "quality_cost_pct": 0.03,
        "profit_margin_pct": 0.10,
        "taxes_duties_pct": 0.05,
        "sga_pct": 0.08,
        "packaging_per_unit": 50.0,
        "freight_per_unit": 80.0,
    })
    assert r.status_code == 201, r.text
    assert r.json()["profit_margin_pct"] == 0.10


# ── Parts + BOM + Routing ─────────────────────────────────────────────────────

def test_create_part_with_bom_and_routing(client):
    # Material
    mat = client.post("/api/v1/materials/", json={
        "grade": "EN8 Test", "material_type": "Steel",
        "rate_per_kg": 68.0, "scrap_recovery_pct": 0.35, "currency": "INR",
    }).json()

    # Machine
    mach = client.post("/api/v1/machines/", json={
        "name": "Test CNC", "machine_type": "CNC",
        "hourly_rate": 1800.0, "commodity_types": ["Forging"],
    }).json()

    # Part
    part = client.post("/api/v1/parts/", json={
        "part_no": "TEST-001", "name": "Test Part",
        "commodity_type": "Forging", "annual_volume": 1000,
    })
    assert part.status_code == 201, part.text
    pid = part.json()["id"]

    # BOM
    bom = client.put(f"/api/v1/parts/{pid}/bom", json=[{
        "material_id": mat["id"], "gross_weight_kg": 2.0,
        "net_weight_kg": 1.5, "scrap_rate_per_kg": 15.0,
    }])
    assert bom.status_code == 200

    # Routing
    routing = client.put(f"/api/v1/parts/{pid}/routing", json=[{
        "sequence": 1, "operation_name": "CNC Machining",
        "machine_id": mach["id"], "cycle_time_min": 8.0,
        "setup_time_min": 25.0, "operators": 1,
        "labor_rate_per_hr": 450.0,
    }])
    assert routing.status_code == 200


# ── Cost Sheet + Calculation ──────────────────────────────────────────────────

def test_cost_sheet_calculate(client):
    mat = client.post("/api/v1/materials/", json={
        "grade": "EN19 Calc Test", "material_type": "Steel",
        "rate_per_kg": 95.0, "scrap_recovery_pct": 0.35, "currency": "INR",
    }).json()
    mach = client.post("/api/v1/machines/", json={
        "name": "Calc CNC", "machine_type": "CNC",
        "hourly_rate": 1800.0, "commodity_types": ["Forging"],
    }).json()
    part = client.post("/api/v1/parts/", json={
        "part_no": "CALC-001", "name": "Calc Part",
        "commodity_type": "Forging", "annual_volume": 5000,
    }).json()
    pid = part["id"]
    client.put(f"/api/v1/parts/{pid}/bom", json=[{
        "material_id": mat["id"], "gross_weight_kg": 3.0,
        "net_weight_kg": 2.2, "scrap_rate_per_kg": 20.0,
    }])
    client.put(f"/api/v1/parts/{pid}/routing", json=[{
        "sequence": 1, "operation_name": "CNC Machining",
        "machine_id": mach["id"], "cycle_time_min": 8.0,
        "setup_time_min": 25.0, "operators": 1, "labor_rate_per_hr": 450.0,
    }])

    # Create cost sheet
    cs = client.post("/api/v1/cost-sheets/", json={
        "part_id": pid, "scenario_name": "Base Scenario",
        "quoted_price": 500.0, "supplier_name": "Bharat Forge",
    })
    assert cs.status_code == 201, cs.text
    csid = cs.json()["id"]

    # Calculate
    calc = client.post(f"/api/v1/cost-sheets/{csid}/calculate")
    assert calc.status_code == 200, calc.text
    result = calc.json()
    assert result["status"] == "calculated"
    assert result["result_summary"] is not None
    assert result["result_summary"]["total_material_net"] > 0
    assert result["result_summary"]["total_conversion"] >= 0
    assert result["result_line_items"] is not None


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
