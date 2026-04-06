# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A manufacturing should-cost modeling platform. Users build cost sheets for physical parts by combining material costs, process routing (machine + labor), overhead stacking, tooling/NRE amortization, and logistics to compute a "should cost" price. The platform compares this against quoted supplier prices to identify negotiation opportunities.

## Commands

### Development (Docker)
```bash
docker-compose up          # Start all services (db, backend, frontend)
docker-compose up -d db    # Start just Postgres
```

### Backend (local, no Docker)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000    # Runs on :8000
python seed_db.py                             # Seed reference data
```

### Frontend (local, no Docker)
```bash
cd frontend
npm install
npm run dev      # Runs on :5173, proxies API to :8000
npm run build    # Production build
```

### Database
- Default: SQLite (`shouldcost.db`) when no `DATABASE_URL` env var is set
- Production/Docker: PostgreSQL 16 (`postgresql://shouldcost:shouldcost@db:5432/shouldcost`)
- Tables auto-created on backend startup via `Base.metadata.create_all`
- Alembic configured for migrations (`backend/alembic.ini`) pointing at Postgres

No test suite exists yet (`backend/tests/` is empty).

## Architecture

### Backend (FastAPI + SQLAlchemy)
- **Entry point**: `backend/app/main.py` — registers all routers, runs seed on startup
- **Config**: `backend/app/config.py` — `DATABASE_URL`, `OPENAI_API_KEY`, `CORS_ORIGINS` from env/.env
- **Models** (`backend/app/models/`): Material, Machine, Vendor, ProcessTemplate, OverheadProfile, Part (with BomLine + RoutingStep children), CostSheet, ExcelUpload, AuditLog
- **API** (`backend/app/api/v1/`): REST CRUD for each model, plus `cost_sheets.py` (calculate endpoint), `excel.py` (upload/download), `dashboard.py`, `integrations.py` (SAP S/4HANA stub)
- **Schemas** (`backend/app/schemas/`): Pydantic models for API request/response validation

### Calculation Engine (`backend/app/engine/`)
The core business logic, kept as pure functions separate from the API layer:
- `calculator.py` — `calculate_should_cost(CostSheetInput) -> CostSheetResult`. Computes: material with scrap credit, conversion with setup amortization, learning curve adjustment, tooling/NRE, overhead stacking (factory, admin, depreciation, quality), SGA, profit margin, taxes, logistics. Also produces sensitivity analysis (±20% on key drivers) and volume-price analysis.
- `schemas.py` — Pydantic I/O models for the engine (separate from API schemas)
- `recommendations.py` — Rule-based recommendation engine using a registry pattern (`@register_rule(commodity_type)` decorator). Rules in `engine/rules/`.

### Services
- `excel_service.py` — Parses commodity-specific Excel uploads (forging format) into Part + BOM + Routing; generates formatted Excel exports
- `ai_analysis_service.py` — Optional OpenAI-powered analysis of cost sheets (requires `OPENAI_API_KEY`)

### Frontend (React 18 + Vite + Tailwind)
- SPA with React Router, TanStack Query for data fetching, Recharts for charts
- `src/api/client.js` — Axios instance hitting `/api/v1`, response interceptor extracts `.data`
- Pages: Dashboard, CostSheetBuilder (create/edit), CostSheetOutput (results view), ScenarioComparison, CRUD list pages for master data, ExcelUpload, Settings
- Shared components: DataTable, Modal, FormField, StatusBadge, Toast

### Key Data Flow
1. User creates master data (materials, machines, overhead profiles) or uploads Excel
2. User builds a Part with BOM lines (material refs) and routing steps (machine refs)
3. User creates a CostSheet referencing a Part → backend assembles `CostSheetInput` from Part/BOM/Routing/Overheads → `calculate_should_cost()` returns full breakdown
4. Frontend renders line items, waterfall chart, sensitivity tornado, volume curve, and AI analysis
