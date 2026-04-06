"""Pydantic models for the calculation engine input/output."""
from pydantic import BaseModel
from typing import Optional


class MaterialInput(BaseModel):
    name: str
    grade: str
    finished_mass_kg: float
    utilization_rate: float  # 0-1 (e.g., 0.65 = 65%)
    price_per_kg: float
    scrap_recovery_pct: float = 0.35  # 0-1
    price_source: str = "database"
    confidence: str = "medium"


class ProcessStepInput(BaseModel):
    step_name: str
    machine_type: str
    machine_rate_per_hr: float
    cycle_time_min: float
    setup_time_min: float = 0
    operators: int = 1
    labor_rate_per_hr: float = 0
    rate_source: str = "database"
    confidence: str = "medium"


class ToolingNreInput(BaseModel):
    item: str
    cost: float
    life_units: int
    source: str = "estimated"
    confidence: str = "medium"


class OverheadInput(BaseModel):
    factory_overhead_pct: float = 0.12
    admin_overhead_pct: float = 0.08
    depreciation_pct: float = 0.05
    quality_cost_pct: float = 0.03
    profit_margin_pct: float = 0.10
    taxes_duties_pct: float = 0.05
    sga_pct: float = 0.08
    source: str = "overhead_benchmarks"
    confidence: str = "medium"


class LogisticsInput(BaseModel):
    packaging_per_unit: float = 0
    freight_per_unit: float = 0
    other_per_unit: float = 0
    source: str = "estimated"


class CostSheetInput(BaseModel):
    product_name: str
    currency: str = "INR"
    current_quoted_price: float = 0
    annual_volume: int = 1000
    batch_size: int = 100
    materials: list[MaterialInput]
    process_steps: list[ProcessStepInput]
    tooling_nre: list[ToolingNreInput] = []
    learning_curve_factor: float = 1.0
    learning_curve_source: str = ""
    overhead: OverheadInput = OverheadInput()
    logistics: LogisticsInput = LogisticsInput()


class LineItem(BaseModel):
    category: str
    item: str
    value: float
    detail: str = ""
    source: str = ""
    confidence: str = "medium"


class ResultSummary(BaseModel):
    total_material_gross: float
    total_scrap_credit: float
    total_material_net: float
    total_conversion: float
    total_labor: float
    total_tooling_nre: float
    total_overhead: float
    total_sga: float
    total_profit: float
    total_logistics: float
    should_cost: float
    current_price: float
    gap: float
    gap_pct: float
    annual_volume: int
    annual_opportunity: float


class SensitivityItem(BaseModel):
    driver: str
    new_should_cost: float
    impact: float
    impact_pct: float


class VolumeAnalysisItem(BaseModel):
    annual_volume: int
    batch_size: int
    should_cost_per_unit: float
    delta_vs_base: float
    delta_pct: float


class ConfidenceSummary(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0


class CostSheetResult(BaseModel):
    product: str
    currency: str
    line_items: list[LineItem]
    summary: ResultSummary
    confidence_summary: ConfidenceSummary
    confidence_warning: Optional[str] = None
    low_confidence_items: list[str] = []
    sensitivity: list[SensitivityItem]
    volume_analysis: list[VolumeAnalysisItem]
