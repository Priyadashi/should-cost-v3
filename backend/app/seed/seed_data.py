"""Seed the database with initial reference data for Indian should-cost models."""

from sqlalchemy.orm import Session
from app.models import (
    Material, Machine, ProcessTemplate, OverheadProfile,
    Vendor, Part, BomLine, RoutingStep,
)


def _get_or_create(db, model, lookup: dict, defaults: dict = None):
    """Fetch a record matching lookup fields, or create it with lookup + defaults."""
    obj = db.query(model).filter_by(**lookup).first()
    if obj is None:
        data = {**lookup, **(defaults or {})}
        obj = model(**data)
        db.add(obj)
        db.flush()
    return obj


def seed_database(db: Session) -> str:
    created = {"materials": 0, "machines": 0, "templates": 0,
                "profiles": 0, "vendors": 0, "parts": 0}

    # ------------------------------------------------------------------
    # Materials (Indian grades, rates in INR/kg)
    # ------------------------------------------------------------------
    material_data = [
        dict(grade="EN8 (Medium Carbon Steel)",   material_type="Steel",     rate_per_kg=68,  scrap_recovery_pct=0.35, currency="INR"),
        dict(grade="EN19 (Alloy Steel)",           material_type="Steel",     rate_per_kg=95,  scrap_recovery_pct=0.35, currency="INR"),
        dict(grade="EN24 (High Tensile Steel)",    material_type="Steel",     rate_per_kg=112, scrap_recovery_pct=0.35, currency="INR"),
        dict(grade="SS304 (Stainless Steel)",      material_type="Steel",     rate_per_kg=210, scrap_recovery_pct=0.40, currency="INR"),
        dict(grade="IS2062 E250 (Mild Steel)",     material_type="Steel",     rate_per_kg=58,  scrap_recovery_pct=0.30, currency="INR"),
        dict(grade="42CrMo4 (Chromoly Steel)",     material_type="Steel",     rate_per_kg=130, scrap_recovery_pct=0.35, currency="INR"),
        dict(grade="ADC12 (Aluminium Die Cast)",   material_type="Aluminum",  rate_per_kg=185, scrap_recovery_pct=0.40, currency="INR"),
        dict(grade="A356 (Aluminium Sand Cast)",   material_type="Aluminum",  rate_per_kg=175, scrap_recovery_pct=0.38, currency="INR"),
        dict(grade="GG25 (Grey Cast Iron)",        material_type="Cast Iron", rate_per_kg=52,  scrap_recovery_pct=0.25, currency="INR"),
        dict(grade="SG500 (Ductile Iron)",         material_type="Cast Iron", rate_per_kg=62,  scrap_recovery_pct=0.28, currency="INR"),
        dict(grade="IS 2062 E350 (Structural Steel)", material_type="Steel",  rate_per_kg=65,  scrap_recovery_pct=0.30, currency="INR"),
    ]
    mats = {}
    for md in material_data:
        obj = _get_or_create(db, Material, {"grade": md["grade"]}, md)
        mats[md["grade"].split(" ")[0]] = obj
        if db.new.__contains__(obj):
            created["materials"] += 1

    # ------------------------------------------------------------------
    # Machines (rates in INR/hr)
    # ------------------------------------------------------------------
    machine_data = [
        dict(name="CNC Machining Center",      machine_type="CNC",      hourly_rate=1800, power_kw=15,  commodity_types=["Forging","Casting","Fabrication"]),
        dict(name="VMC 850 (Vertical Machining Center)", machine_type="CNC", hourly_rate=2000, power_kw=18, commodity_types=["Forging","Casting"]),
        dict(name="Hydraulic Press 500T",      machine_type="Press",    hourly_rate=2200, power_kw=45,  commodity_types=["Forging"]),
        dict(name="Hydraulic Press 1000T",     machine_type="Press",    hourly_rate=3200, power_kw=90,  commodity_types=["Forging"]),
        dict(name="Induction Heater",          machine_type="Heater",   hourly_rate=1600, power_kw=100, commodity_types=["Forging"]),
        dict(name="Heat Treatment Furnace",    machine_type="Furnace",  hourly_rate=1400, power_kw=80,  commodity_types=["Forging","Casting"]),
        dict(name="Shot Blasting Machine",     machine_type="Blasting", hourly_rate=800,  power_kw=20,  commodity_types=["Forging","Casting"]),
        dict(name="Lathe Machine",             machine_type="Lathe",    hourly_rate=1200, power_kw=10,  commodity_types=["Forging","Casting"]),
        dict(name="MIG Welding Station",       machine_type="Welding",  hourly_rate=950,  power_kw=8,   commodity_types=["Fabrication"]),
        dict(name="TIG Welding Station",       machine_type="Welding",  hourly_rate=1200, power_kw=10,  commodity_types=["Fabrication"]),
        dict(name="Plasma Cutting Machine",    machine_type="Cutting",  hourly_rate=1100, power_kw=25,  commodity_types=["Fabrication"]),
        dict(name="Press Brake 200T",          machine_type="Press",    hourly_rate=1100, power_kw=12,  commodity_types=["Fabrication"]),
        dict(name="Sand Casting Setup",        machine_type="Casting",  hourly_rate=900,  power_kw=30,  commodity_types=["Casting"]),
        dict(name="Die Casting Machine 400T",  machine_type="Casting",  hourly_rate=2500, power_kw=55,  commodity_types=["Casting"]),
        dict(name="Fettling & Grinding",       machine_type="Grinding", hourly_rate=750,  power_kw=12,  commodity_types=["Casting","Forging"]),
    ]
    machs = {}
    for md in machine_data:
        obj = _get_or_create(db, Machine, {"name": md["name"]}, md)
        machs[md["name"]] = obj
        if db.new.__contains__(obj):
            created["machines"] += 1

    # ------------------------------------------------------------------
    # Process Templates — Forging
    # ------------------------------------------------------------------
    forging_templates = [
        dict(name="Billet Cutting",  commodity_type="Forging", category="Preparation", sequence_order=10,
             default_machine_id=machs["Lathe Machine"].id,           default_cycle_time_min=3,  default_setup_time_min=15, default_batch_size=200, default_operators=1, default_labor_rate_per_hr=350, default_tooling_cost_per_unit=2),
        dict(name="Induction Heating", commodity_type="Forging", category="Heating",   sequence_order=20,
             default_machine_id=machs["Induction Heater"].id,        default_cycle_time_min=5,  default_setup_time_min=20, default_batch_size=200, default_operators=1, default_labor_rate_per_hr=300, default_tooling_cost_per_unit=0),
        dict(name="Forging Press",   commodity_type="Forging", category="Forming",     sequence_order=30,
             default_machine_id=machs["Hydraulic Press 500T"].id,    default_cycle_time_min=2,  default_setup_time_min=30, default_batch_size=200, default_operators=2, default_labor_rate_per_hr=400, default_tooling_cost_per_unit=15),
        dict(name="Trimming",        commodity_type="Forging", category="Forming",     sequence_order=40,
             default_machine_id=machs["Hydraulic Press 500T"].id,    default_cycle_time_min=1.5,default_setup_time_min=15, default_batch_size=200, default_operators=1, default_labor_rate_per_hr=350, default_tooling_cost_per_unit=5),
        dict(name="Heat Treatment",  commodity_type="Forging", category="Thermal",     sequence_order=50,
             default_machine_id=machs["Heat Treatment Furnace"].id,  default_cycle_time_min=15, default_setup_time_min=30, default_batch_size=100, default_operators=1, default_labor_rate_per_hr=300, default_tooling_cost_per_unit=0),
        dict(name="Shot Blasting",   commodity_type="Forging", category="Finishing",   sequence_order=60,
             default_machine_id=machs["Shot Blasting Machine"].id,   default_cycle_time_min=5,  default_setup_time_min=10, default_batch_size=100, default_operators=1, default_labor_rate_per_hr=250, default_tooling_cost_per_unit=0),
        dict(name="CNC Machining",   commodity_type="Forging", category="Machining",   sequence_order=70,
             default_machine_id=machs["CNC Machining Center"].id,    default_cycle_time_min=8,  default_setup_time_min=25, default_batch_size=50,  default_operators=1, default_labor_rate_per_hr=450, default_tooling_cost_per_unit=25),
        dict(name="Turning & Boring",commodity_type="Forging", category="Machining",   sequence_order=75,
             default_machine_id=machs["Lathe Machine"].id,           default_cycle_time_min=6,  default_setup_time_min=20, default_batch_size=50,  default_operators=1, default_labor_rate_per_hr=400, default_tooling_cost_per_unit=18),
        dict(name="Inspection & Packing", commodity_type="Forging", category="Quality",sequence_order=90,
             default_machine_id=None,                                 default_cycle_time_min=3,  default_setup_time_min=10, default_batch_size=200, default_operators=1, default_labor_rate_per_hr=280, default_tooling_cost_per_unit=0),
    ]

    # Process Templates — Casting
    casting_templates = [
        dict(name="Pattern Making",   commodity_type="Casting", category="Preparation", sequence_order=10,
             default_machine_id=None,                                   default_cycle_time_min=60, default_setup_time_min=120,default_batch_size=1,   default_operators=2, default_labor_rate_per_hr=500, default_tooling_cost_per_unit=50),
        dict(name="Mould Preparation",commodity_type="Casting", category="Preparation", sequence_order=20,
             default_machine_id=machs["Sand Casting Setup"].id,         default_cycle_time_min=20, default_setup_time_min=30, default_batch_size=10,  default_operators=2, default_labor_rate_per_hr=350, default_tooling_cost_per_unit=10),
        dict(name="Melting & Pouring",commodity_type="Casting", category="Casting",     sequence_order=30,
             default_machine_id=machs["Sand Casting Setup"].id,         default_cycle_time_min=10, default_setup_time_min=30, default_batch_size=20,  default_operators=2, default_labor_rate_per_hr=400, default_tooling_cost_per_unit=5),
        dict(name="Shakeout & Cleaning", commodity_type="Casting", category="Finishing",sequence_order=40,
             default_machine_id=machs["Fettling & Grinding"].id,        default_cycle_time_min=15, default_setup_time_min=10, default_batch_size=20,  default_operators=1, default_labor_rate_per_hr=280, default_tooling_cost_per_unit=0),
        dict(name="Fettling & Grinding", commodity_type="Casting", category="Finishing",sequence_order=50,
             default_machine_id=machs["Fettling & Grinding"].id,        default_cycle_time_min=10, default_setup_time_min=10, default_batch_size=20,  default_operators=1, default_labor_rate_per_hr=280, default_tooling_cost_per_unit=8),
        dict(name="Heat Treatment (Casting)", commodity_type="Casting", category="Thermal",sequence_order=60,
             default_machine_id=machs["Heat Treatment Furnace"].id,     default_cycle_time_min=20, default_setup_time_min=30, default_batch_size=50,  default_operators=1, default_labor_rate_per_hr=300, default_tooling_cost_per_unit=0),
        dict(name="CNC Machining (Casting)", commodity_type="Casting", category="Machining",sequence_order=70,
             default_machine_id=machs["VMC 850 (Vertical Machining Center)"].id, default_cycle_time_min=10, default_setup_time_min=30, default_batch_size=25, default_operators=1, default_labor_rate_per_hr=450, default_tooling_cost_per_unit=30),
    ]

    # Process Templates — Fabrication
    fabrication_templates = [
        dict(name="Laser / Plasma Cutting", commodity_type="Fabrication", category="Cutting",   sequence_order=10,
             default_machine_id=machs["Plasma Cutting Machine"].id,   default_cycle_time_min=5,  default_setup_time_min=15, default_batch_size=50,  default_operators=1, default_labor_rate_per_hr=380, default_tooling_cost_per_unit=3),
        dict(name="Sheet Bending",           commodity_type="Fabrication", category="Forming",   sequence_order=20,
             default_machine_id=machs["Press Brake 200T"].id,         default_cycle_time_min=4,  default_setup_time_min=20, default_batch_size=50,  default_operators=1, default_labor_rate_per_hr=350, default_tooling_cost_per_unit=5),
        dict(name="MIG Welding",             commodity_type="Fabrication", category="Welding",   sequence_order=30,
             default_machine_id=machs["MIG Welding Station"].id,      default_cycle_time_min=12, default_setup_time_min=20, default_batch_size=20,  default_operators=2, default_labor_rate_per_hr=400, default_tooling_cost_per_unit=8),
        dict(name="TIG Welding",             commodity_type="Fabrication", category="Welding",   sequence_order=35,
             default_machine_id=machs["TIG Welding Station"].id,      default_cycle_time_min=20, default_setup_time_min=25, default_batch_size=10,  default_operators=1, default_labor_rate_per_hr=500, default_tooling_cost_per_unit=12),
        dict(name="Surface Treatment / Painting", commodity_type="Fabrication", category="Finishing", sequence_order=40,
             default_machine_id=None,                                  default_cycle_time_min=15, default_setup_time_min=20, default_batch_size=20,  default_operators=1, default_labor_rate_per_hr=300, default_tooling_cost_per_unit=20),
        dict(name="Assembly & Fastening",    commodity_type="Fabrication", category="Assembly",  sequence_order=50,
             default_machine_id=None,                                  default_cycle_time_min=10, default_setup_time_min=15, default_batch_size=20,  default_operators=2, default_labor_rate_per_hr=350, default_tooling_cost_per_unit=5),
        dict(name="Inspection & Dispatch",   commodity_type="Fabrication", category="Quality",   sequence_order=60,
             default_machine_id=None,                                  default_cycle_time_min=5,  default_setup_time_min=10, default_batch_size=50,  default_operators=1, default_labor_rate_per_hr=280, default_tooling_cost_per_unit=0),
    ]

    all_templates = forging_templates + casting_templates + fabrication_templates
    tpls = {}
    for td in all_templates:
        obj = _get_or_create(db, ProcessTemplate, {"name": td["name"], "commodity_type": td["commodity_type"]}, td)
        tpls[td["name"]] = obj
        if db.new.__contains__(obj):
            created["templates"] += 1

    # ------------------------------------------------------------------
    # Overhead Profiles
    # ------------------------------------------------------------------
    overhead_data = [
        dict(name="India - Standard Forging", is_default=True,
             factory_overhead_pct=0.12, admin_overhead_pct=0.08, depreciation_pct=0.05,
             quality_cost_pct=0.03, profit_margin_pct=0.10, taxes_duties_pct=0.05,
             sga_pct=0.08, packaging_per_unit=50, freight_per_unit=80, other_logistics_per_unit=20),
        dict(name="India - Automotive Tier 1", is_default=False,
             factory_overhead_pct=0.15, admin_overhead_pct=0.10, depreciation_pct=0.07,
             quality_cost_pct=0.05, profit_margin_pct=0.08, taxes_duties_pct=0.05,
             sga_pct=0.07, packaging_per_unit=80, freight_per_unit=120, other_logistics_per_unit=30),
        dict(name="India - Export / IATF", is_default=False,
             factory_overhead_pct=0.18, admin_overhead_pct=0.12, depreciation_pct=0.08,
             quality_cost_pct=0.06, profit_margin_pct=0.12, taxes_duties_pct=0.00,
             sga_pct=0.09, packaging_per_unit=120, freight_per_unit=350, other_logistics_per_unit=50),
        dict(name="India - Small Foundry", is_default=False,
             factory_overhead_pct=0.10, admin_overhead_pct=0.06, depreciation_pct=0.04,
             quality_cost_pct=0.02, profit_margin_pct=0.12, taxes_duties_pct=0.05,
             sga_pct=0.06, packaging_per_unit=30, freight_per_unit=60, other_logistics_per_unit=10),
    ]
    for od in overhead_data:
        obj = _get_or_create(db, OverheadProfile, {"name": od["name"]}, od)
        if db.new.__contains__(obj):
            created["profiles"] += 1

    # ------------------------------------------------------------------
    # Vendors
    # ------------------------------------------------------------------
    vendor_data = [
        dict(name="Bharat Forge Ltd", code="BFL", location="Pune, India",
             capabilities=["Forging","Heat Treatment","CNC Machining"],
             certifications=["ISO 9001","IATF 16949","AS9100"]),
        dict(name="Kalyani Steels Ltd", code="KSL", location="Pune, India",
             capabilities=["Forging","Steel Making"],
             certifications=["ISO 9001","ISO 14001"]),
        dict(name="Endurance Technologies", code="ETL", location="Aurangabad, India",
             capabilities=["Die Casting","CNC Machining","Assembly"],
             certifications=["ISO 9001","IATF 16949"]),
        dict(name="Minda Industries", code="MIL", location="Gurgaon, India",
             capabilities=["Casting","Fabrication","Electronics"],
             certifications=["ISO 9001","IATF 16949"]),
        dict(name="Ramkrishna Forgings", code="RKF", location="Kolkata, India",
             capabilities=["Forging","Machining","Heat Treatment"],
             certifications=["ISO 9001","IATF 16949","ISO 14001"]),
        dict(name="Sundram Fasteners", code="SFL", location="Chennai, India",
             capabilities=["Forging","Cold Forming","CNC Machining"],
             certifications=["ISO 9001","IATF 16949","ISO 45001"]),
        dict(name="Tata AutoComp Systems", code="TACS", location="Pune, India",
             capabilities=["Fabrication","Stamping","Assembly","Painting"],
             certifications=["ISO 9001","IATF 16949","ISO 14001"]),
    ]
    for vd in vendor_data:
        obj = _get_or_create(db, Vendor, {"code": vd["code"]}, vd)
        if db.new.__contains__(obj):
            created["vendors"] += 1

    # ------------------------------------------------------------------
    # Sample Parts (only if no parts exist)
    # ------------------------------------------------------------------
    if db.query(Part).count() == 0:
        mat = mats  # shorthand

        def _routing(part, steps):
            for seq, (op, mach_name, ct, st, lr) in enumerate(steps, 1):
                db.add(RoutingStep(
                    part_id=part.id, sequence=seq, operation_name=op,
                    machine_id=machs[mach_name].id if mach_name else None,
                    cycle_time_min=ct, setup_time_min=st, labor_rate_per_hr=lr,
                ))

        # Part 1: Connecting Rod
        p1 = Part(part_no="CR-2024-001", name="Connecting Rod", commodity_type="Forging", annual_volume=5000)
        db.add(p1); db.flush()
        db.add(BomLine(part_id=p1.id, material_id=mat["EN8"].id, gross_weight_kg=2.8, net_weight_kg=1.9, scrap_rate_per_kg=20))
        _routing(p1, [
            ("Billet Cutting",   "Lathe Machine",           3,  15, 350),
            ("Induction Heating","Induction Heater",         5,  20, 300),
            ("Forging Press",    "Hydraulic Press 500T",     2,  30, 400),
            ("Trimming",         "Hydraulic Press 500T",     1.5,15, 350),
            ("Heat Treatment",   "Heat Treatment Furnace",   15, 30, 300),
            ("Shot Blasting",    "Shot Blasting Machine",    5,  10, 250),
            ("CNC Machining",    "CNC Machining Center",     8,  25, 450),
        ])

        # Part 2: Crankshaft Flange
        p2 = Part(part_no="CF-2024-002", name="Crankshaft Flange", commodity_type="Forging", annual_volume=3000)
        db.add(p2); db.flush()
        db.add(BomLine(part_id=p2.id, material_id=mat["EN19"].id, gross_weight_kg=5.2, net_weight_kg=3.8, scrap_rate_per_kg=25))
        _routing(p2, [
            ("Billet Cutting",   "Lathe Machine",           3,  15, 350),
            ("Induction Heating","Induction Heater",         6,  20, 300),
            ("Forging Press",    "Hydraulic Press 1000T",    3,  45, 450),
            ("Heat Treatment",   "Heat Treatment Furnace",   20, 30, 300),
            ("Shot Blasting",    "Shot Blasting Machine",    5,  10, 250),
            ("CNC Machining",    "VMC 850 (Vertical Machining Center)", 12, 30, 480),
        ])

        # Part 3: Suspension Knuckle
        p3 = Part(part_no="SK-2024-003", name="Suspension Knuckle", commodity_type="Forging", annual_volume=8000)
        db.add(p3); db.flush()
        db.add(BomLine(part_id=p3.id, material_id=mat["EN24"].id, gross_weight_kg=3.5, net_weight_kg=2.5, scrap_rate_per_kg=22))
        _routing(p3, [
            ("Billet Cutting",   "Lathe Machine",           3,  15, 350),
            ("Induction Heating","Induction Heater",         5,  20, 300),
            ("Forging Press",    "Hydraulic Press 500T",     2,  30, 400),
            ("Trimming",         "Hydraulic Press 500T",     1.5,15, 350),
            ("Shot Blasting",    "Shot Blasting Machine",    5,  10, 250),
            ("CNC Machining",    "CNC Machining Center",     8,  25, 450),
        ])
        created["parts"] = 3

    db.commit()

    return (
        f"Seed complete — added: {created['materials']} materials, "
        f"{created['machines']} machines, {created['templates']} templates, "
        f"{created['profiles']} overhead profiles, {created['vendors']} vendors, "
        f"{created['parts']} parts."
    )
