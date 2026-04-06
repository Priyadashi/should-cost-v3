"""Seed the database with initial reference data for Indian forging should-cost models."""

from sqlalchemy.orm import Session
from app.models import (
    Material, Machine, ProcessTemplate, OverheadProfile,
    Vendor, Part, BomLine, RoutingStep,
)


def seed_database(db: Session) -> str:
    """Populate the database with initial seed data.

    Skips seeding if materials already exist.
    Returns a summary string describing what was created.
    """
    existing = db.query(Material).count()
    if existing > 0:
        return f"Seed skipped: database already contains {existing} material(s)."

    # ------------------------------------------------------------------
    # Materials (Indian forging grades, rates in INR/kg)
    # ------------------------------------------------------------------
    materials = [
        Material(grade="EN8 (Medium Carbon Steel)", material_type="Steel",
                 rate_per_kg=68, scrap_recovery_pct=0.35, currency="INR"),
        Material(grade="EN19 (Alloy Steel)", material_type="Steel",
                 rate_per_kg=95, scrap_recovery_pct=0.35, currency="INR"),
        Material(grade="SS304 (Stainless Steel)", material_type="Steel",
                 rate_per_kg=210, scrap_recovery_pct=0.40, currency="INR"),
        Material(grade="IS2062 E250 (Mild Steel)", material_type="Steel",
                 rate_per_kg=58, scrap_recovery_pct=0.30, currency="INR"),
        Material(grade="EN24 (High Tensile Steel)", material_type="Steel",
                 rate_per_kg=112, scrap_recovery_pct=0.35, currency="INR"),
        Material(grade="ADC12 (Aluminium Die Cast)", material_type="Aluminum",
                 rate_per_kg=185, scrap_recovery_pct=0.40, currency="INR"),
        Material(grade="GG25 (Grey Cast Iron)", material_type="Cast Iron",
                 rate_per_kg=52, scrap_recovery_pct=0.25, currency="INR"),
    ]
    db.add_all(materials)
    db.flush()

    # ------------------------------------------------------------------
    # Machines (rates in INR/hr)
    # ------------------------------------------------------------------
    machines = [
        Machine(name="CNC Machining Center", machine_type="CNC",
                hourly_rate=1800, power_kw=15,
                commodity_types=["Forging", "Casting", "Fabrication"]),
        Machine(name="Hydraulic Press 500T", machine_type="Press",
                hourly_rate=2200, power_kw=45,
                commodity_types=["Forging"]),
        Machine(name="MIG Welding Station", machine_type="Welding",
                hourly_rate=950, power_kw=8,
                commodity_types=["Fabrication"]),
        Machine(name="Lathe Machine", machine_type="Lathe",
                hourly_rate=1200, power_kw=10,
                commodity_types=["Forging", "Casting"]),
        Machine(name="Induction Heater", machine_type="Heater",
                hourly_rate=1600, power_kw=100,
                commodity_types=["Forging"]),
        Machine(name="Shot Blasting Machine", machine_type="Blasting",
                hourly_rate=800, power_kw=20,
                commodity_types=["Forging", "Casting"]),
        Machine(name="Heat Treatment Furnace", machine_type="Furnace",
                hourly_rate=1400, power_kw=80,
                commodity_types=["Forging", "Casting"]),
        Machine(name="Press Brake", machine_type="Press",
                hourly_rate=1100, power_kw=12,
                commodity_types=["Fabrication"]),
    ]
    db.add_all(machines)
    db.flush()

    # Build a lookup so we can reference machines by name
    m = {machine.name: machine for machine in machines}

    # ------------------------------------------------------------------
    # Forging Process Templates
    # ------------------------------------------------------------------
    process_templates = [
        ProcessTemplate(name="Billet Cutting", commodity_type="Forging",
                        sequence_order=1, default_machine_id=m["Lathe Machine"].id,
                        default_cycle_time_min=3, default_setup_time_min=15,
                        default_labor_rate_per_hr=350),
        ProcessTemplate(name="Heating", commodity_type="Forging",
                        sequence_order=2, default_machine_id=m["Induction Heater"].id,
                        default_cycle_time_min=5, default_setup_time_min=20,
                        default_labor_rate_per_hr=300),
        ProcessTemplate(name="Forging Press", commodity_type="Forging",
                        sequence_order=3, default_machine_id=m["Hydraulic Press 500T"].id,
                        default_cycle_time_min=2, default_setup_time_min=30,
                        default_labor_rate_per_hr=400),
        ProcessTemplate(name="Trimming", commodity_type="Forging",
                        sequence_order=4, default_machine_id=m["Hydraulic Press 500T"].id,
                        default_cycle_time_min=1.5, default_setup_time_min=15,
                        default_labor_rate_per_hr=350),
        ProcessTemplate(name="Heat Treatment", commodity_type="Forging",
                        sequence_order=5, default_machine_id=m["Heat Treatment Furnace"].id,
                        default_cycle_time_min=15, default_setup_time_min=30,
                        default_labor_rate_per_hr=300),
        ProcessTemplate(name="Shot Blasting", commodity_type="Forging",
                        sequence_order=6, default_machine_id=m["Shot Blasting Machine"].id,
                        default_cycle_time_min=5, default_setup_time_min=10,
                        default_labor_rate_per_hr=250),
        ProcessTemplate(name="CNC Machining", commodity_type="Forging",
                        sequence_order=7, default_machine_id=m["CNC Machining Center"].id,
                        default_cycle_time_min=8, default_setup_time_min=25,
                        default_labor_rate_per_hr=450),
    ]
    db.add_all(process_templates)
    db.flush()

    # Build a template lookup by name
    tpl = {t.name: t for t in process_templates}

    # ------------------------------------------------------------------
    # Overhead Profiles
    # ------------------------------------------------------------------
    overhead_profiles = [
        OverheadProfile(
            name="India - Standard Forging", is_default=True,
            factory_overhead_pct=0.12, admin_overhead_pct=0.08,
            depreciation_pct=0.05, quality_cost_pct=0.03,
            profit_margin_pct=0.10, taxes_duties_pct=0.05,
            sga_pct=0.08, packaging_per_unit=50, freight_per_unit=80,
        ),
        OverheadProfile(
            name="India - Premium / Automotive", is_default=False,
            factory_overhead_pct=0.15, admin_overhead_pct=0.10,
            depreciation_pct=0.07, quality_cost_pct=0.05,
            profit_margin_pct=0.08, taxes_duties_pct=0.05,
            sga_pct=0.07, packaging_per_unit=80, freight_per_unit=120,
        ),
    ]
    db.add_all(overhead_profiles)
    db.flush()

    # ------------------------------------------------------------------
    # Vendors
    # ------------------------------------------------------------------
    vendors = [
        Vendor(name="Bharat Forge Ltd", code="BFL", location="Pune, India",
               capabilities=["Forging", "Heat Treatment", "CNC Machining"],
               certifications=["ISO 9001", "IATF 16949", "AS9100"]),
        Vendor(name="Kalyani Steel", code="KSL", location="Pune, India",
               capabilities=["Forging", "Steel Making"],
               certifications=["ISO 9001", "ISO 14001"]),
    ]
    db.add_all(vendors)
    db.flush()

    # ------------------------------------------------------------------
    # Helper: build routing steps from a list of template names
    # ------------------------------------------------------------------
    def _make_routing(part: Part, template_names: list[str]) -> list[RoutingStep]:
        steps = []
        for seq, tname in enumerate(template_names, start=1):
            t = tpl[tname]
            steps.append(RoutingStep(
                part_id=part.id,
                sequence=seq,
                operation_name=t.name,
                machine_id=t.default_machine_id,
                cycle_time_min=t.default_cycle_time_min,
                setup_time_min=t.default_setup_time_min,
                labor_rate_per_hr=t.default_labor_rate_per_hr,
            ))
        return steps

    # Material lookup by partial grade prefix
    mat = {mat.grade.split(" ")[0]: mat for mat in materials}

    # ------------------------------------------------------------------
    # Part 1: Connecting Rod
    # ------------------------------------------------------------------
    part1 = Part(part_no="CR-2024-001", name="Connecting Rod",
                 commodity_type="Forging", annual_volume=5000)
    db.add(part1)
    db.flush()

    db.add(BomLine(part_id=part1.id, material_id=mat["EN8"].id,
                   gross_weight_kg=2.8, net_weight_kg=1.9, scrap_rate_per_kg=20))
    db.add_all(_make_routing(part1, [
        "Billet Cutting", "Heating", "Forging Press", "Trimming",
        "Heat Treatment", "Shot Blasting", "CNC Machining",
    ]))

    # ------------------------------------------------------------------
    # Part 2: Crankshaft Flange
    # ------------------------------------------------------------------
    part2 = Part(part_no="CF-2024-002", name="Crankshaft Flange",
                 commodity_type="Forging", annual_volume=3000)
    db.add(part2)
    db.flush()

    db.add(BomLine(part_id=part2.id, material_id=mat["EN19"].id,
                   gross_weight_kg=5.2, net_weight_kg=3.8, scrap_rate_per_kg=25))
    db.add_all(_make_routing(part2, [
        "Billet Cutting", "Heating", "Forging Press",
        "Heat Treatment", "CNC Machining",
    ]))

    # ------------------------------------------------------------------
    # Part 3: Suspension Knuckle
    # ------------------------------------------------------------------
    part3 = Part(part_no="SK-2024-003", name="Suspension Knuckle",
                 commodity_type="Forging", annual_volume=8000)
    db.add(part3)
    db.flush()

    db.add(BomLine(part_id=part3.id, material_id=mat["EN24"].id,
                   gross_weight_kg=3.5, net_weight_kg=2.5, scrap_rate_per_kg=22))
    db.add_all(_make_routing(part3, [
        "Billet Cutting", "Heating", "Forging Press",
        "Trimming", "Shot Blasting", "CNC Machining",
    ]))

    # ------------------------------------------------------------------
    # Commit everything
    # ------------------------------------------------------------------
    db.commit()

    summary_lines = [
        "Seed complete:",
        f"  {len(materials)} materials",
        f"  {len(machines)} machines",
        f"  {len(process_templates)} process templates",
        f"  {len(overhead_profiles)} overhead profiles",
        f"  {len(vendors)} vendors",
        f"  3 parts with BOM and routing",
    ]
    return "\n".join(summary_lines)
