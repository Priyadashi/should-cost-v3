"""
Should-Cost Calculation Engine v2
Refactored from scripts/should_cost_engine.py into a pure function with Pydantic I/O.
Preserves all math: material with scrap credit, conversion with setup amortization,
learning curve, tooling/NRE, overhead stacking, SGA, profit, logistics, sensitivity, volume-price.
"""
from app.engine.schemas import (
    CostSheetInput, CostSheetResult, LineItem, ResultSummary,
    SensitivityItem, VolumeAnalysisItem, ConfidenceSummary,
)


def calculate_should_cost(inp: CostSheetInput) -> CostSheetResult:
    """Pure function: takes validated input, returns complete cost sheet result."""
    currency = inp.currency
    line_items: list[LineItem] = []

    # ── 1. Material cost (with scrap credit) ──
    total_material_cost = 0.0
    total_scrap_credit = 0.0

    for mat in inp.materials:
        buy_weight = mat.finished_mass_kg / mat.utilization_rate if mat.utilization_rate > 0 else 0
        gross_mat_cost = buy_weight * mat.price_per_kg
        scrap_weight = buy_weight - mat.finished_mass_kg
        scrap_credit = scrap_weight * mat.price_per_kg * mat.scrap_recovery_pct
        net_mat_cost = gross_mat_cost - scrap_credit

        total_material_cost += net_mat_cost
        total_scrap_credit += scrap_credit

        line_items.append(LineItem(
            category="Material",
            item=f"{mat.name} ({mat.grade})",
            value=round(net_mat_cost, 2),
            detail=(
                f"{mat.finished_mass_kg}kg finished / {mat.utilization_rate:.0%} util = {buy_weight:.2f}kg buy "
                f"x {currency} {mat.price_per_kg:.2f}/kg = {currency} {gross_mat_cost:.2f} gross "
                f"- {currency} {scrap_credit:.2f} scrap credit "
                f"({scrap_weight:.2f}kg x {mat.scrap_recovery_pct:.0%} recovery)"
            ),
            source=mat.price_source,
            confidence=mat.confidence,
        ))

    # ── 2. Conversion cost (machine + labor per process step) ──
    total_conversion_cost = 0.0
    total_labor_cost = 0.0
    batch_size = inp.batch_size

    for step in inp.process_steps:
        machine_cost = (step.cycle_time_min / 60) * step.machine_rate_per_hr
        setup_cost_per_part = (
            (step.setup_time_min / 60) * step.machine_rate_per_hr / batch_size
            if batch_size > 0 else 0
        )
        labor_time_min = step.cycle_time_min + (step.setup_time_min / batch_size if batch_size > 0 else 0)
        labor_cost = (labor_time_min / 60) * step.labor_rate_per_hr * step.operators
        step_total = machine_cost + setup_cost_per_part + labor_cost

        total_conversion_cost += machine_cost + setup_cost_per_part
        total_labor_cost += labor_cost

        line_items.append(LineItem(
            category="Conversion",
            item=f"{step.step_name} ({step.machine_type})",
            value=round(step_total, 2),
            detail=(
                f"Machine: {step.cycle_time_min:.1f}min x {currency} {step.machine_rate_per_hr}/hr "
                f"= {currency} {machine_cost:.2f} + Setup: {currency} {setup_cost_per_part:.2f}/part "
                f"+ Labor: {currency} {labor_cost:.2f}"
            ),
            source=step.rate_source,
            confidence=step.confidence,
        ))

    # ── 2b. Learning curve ──
    if inp.learning_curve_factor < 1.0:
        lr_reduction_conv = total_conversion_cost * (1 - inp.learning_curve_factor)
        lr_reduction_labor = total_labor_cost * (1 - inp.learning_curve_factor)
        total_conversion_cost -= lr_reduction_conv
        total_labor_cost -= lr_reduction_labor
        line_items.append(LineItem(
            category="Learning Curve",
            item=f"Learning curve adjustment ({(1 - inp.learning_curve_factor):.0%} reduction)",
            value=round(-(lr_reduction_conv + lr_reduction_labor), 2),
            detail=f"Conversion: -{currency} {lr_reduction_conv:.2f}, Labor: -{currency} {lr_reduction_labor:.2f}",
            source=inp.learning_curve_source,
            confidence="medium",
        ))

    # ── 2c. Tooling / NRE amortization ──
    total_tooling_per_unit = 0.0
    for tool in inp.tooling_nre:
        per_unit = tool.cost / tool.life_units if tool.life_units > 0 else 0
        total_tooling_per_unit += per_unit
        line_items.append(LineItem(
            category="Tooling/NRE",
            item=tool.item,
            value=round(per_unit, 2),
            detail=f"{currency} {tool.cost:.0f} total / {tool.life_units} units = {currency} {per_unit:.2f}/unit",
            source=tool.source,
            confidence=tool.confidence,
        ))

    # ── 3. Overhead stacking ──
    oh = inp.overhead
    overhead_base = total_conversion_cost + total_labor_cost

    # Factory overhead (% of conversion + labor)
    factory_oh = overhead_base * oh.factory_overhead_pct
    # Admin overhead
    admin_oh = overhead_base * oh.admin_overhead_pct
    # Depreciation
    depreciation = overhead_base * oh.depreciation_pct
    # Quality cost
    quality = overhead_base * oh.quality_cost_pct

    total_overhead = factory_oh + admin_oh + depreciation + quality

    line_items.append(LineItem(
        category="Overhead",
        item=f"Factory overhead ({oh.factory_overhead_pct:.0%} of conversion + labor)",
        value=round(factory_oh, 2),
        detail=f"{currency} {overhead_base:.2f} x {oh.factory_overhead_pct:.0%}",
        source=oh.source,
        confidence=oh.confidence,
    ))
    if admin_oh > 0:
        line_items.append(LineItem(
            category="Overhead",
            item=f"Admin overhead ({oh.admin_overhead_pct:.0%})",
            value=round(admin_oh, 2),
            detail=f"{currency} {overhead_base:.2f} x {oh.admin_overhead_pct:.0%}",
            source=oh.source,
            confidence=oh.confidence,
        ))
    if depreciation > 0:
        line_items.append(LineItem(
            category="Overhead",
            item=f"Depreciation ({oh.depreciation_pct:.0%})",
            value=round(depreciation, 2),
            detail=f"{currency} {overhead_base:.2f} x {oh.depreciation_pct:.0%}",
            source=oh.source,
            confidence=oh.confidence,
        ))
    if quality > 0:
        line_items.append(LineItem(
            category="Overhead",
            item=f"Quality cost ({oh.quality_cost_pct:.0%})",
            value=round(quality, 2),
            detail=f"{currency} {overhead_base:.2f} x {oh.quality_cost_pct:.0%}",
            source=oh.source,
            confidence=oh.confidence,
        ))

    # ── 4. Total factory cost ──
    total_factory_cost = (
        total_material_cost + total_conversion_cost + total_labor_cost
        + total_overhead + total_tooling_per_unit
    )

    # ── 5. SGA ──
    sga_cost = total_factory_cost * oh.sga_pct
    line_items.append(LineItem(
        category="SGA",
        item=f"Selling, general & admin ({oh.sga_pct:.0%} of factory cost)",
        value=round(sga_cost, 2),
        detail=f"{currency} {total_factory_cost:.2f} x {oh.sga_pct:.0%}",
        source=oh.source,
        confidence=oh.confidence,
    ))

    # ── 6. Profit ──
    profit_base = total_factory_cost + sga_cost
    profit_cost = profit_base * oh.profit_margin_pct
    line_items.append(LineItem(
        category="Profit",
        item=f"Supplier profit ({oh.profit_margin_pct:.0%})",
        value=round(profit_cost, 2),
        detail=f"{currency} {profit_base:.2f} x {oh.profit_margin_pct:.0%}",
        source=oh.source,
        confidence=oh.confidence,
    ))

    # ── 6b. Taxes & duties ──
    taxes = 0.0
    if oh.taxes_duties_pct > 0:
        taxes = profit_base * oh.taxes_duties_pct
        line_items.append(LineItem(
            category="Taxes",
            item=f"Taxes & duties ({oh.taxes_duties_pct:.0%})",
            value=round(taxes, 2),
            detail=f"{currency} {profit_base:.2f} x {oh.taxes_duties_pct:.0%}",
            source=oh.source,
            confidence=oh.confidence,
        ))

    # ── 7. Logistics ──
    log = inp.logistics
    total_logistics = log.packaging_per_unit + log.freight_per_unit + log.other_per_unit
    if total_logistics > 0:
        line_items.append(LineItem(
            category="Logistics",
            item="Packaging + freight + outsourced processes",
            value=round(total_logistics, 2),
            detail=(
                f"Pkg: {currency} {log.packaging_per_unit:.2f} + "
                f"Freight: {currency} {log.freight_per_unit:.2f} + "
                f"Other: {currency} {log.other_per_unit:.2f}"
            ),
            source=log.source,
            confidence="medium",
        ))

    # ── 8. Total should-cost ──
    should_cost = (
        total_material_cost + total_conversion_cost + total_labor_cost
        + total_overhead + total_tooling_per_unit + sga_cost + profit_cost
        + taxes + total_logistics
    )
    gap = inp.current_quoted_price - should_cost
    gap_pct = (gap / inp.current_quoted_price * 100) if inp.current_quoted_price > 0 else 0
    annual_opportunity = gap * inp.annual_volume

    summary = ResultSummary(
        total_material_gross=round(total_material_cost + total_scrap_credit, 2),
        total_scrap_credit=round(-total_scrap_credit, 2),
        total_material_net=round(total_material_cost, 2),
        total_conversion=round(total_conversion_cost, 2),
        total_labor=round(total_labor_cost, 2),
        total_tooling_nre=round(total_tooling_per_unit, 2),
        total_overhead=round(total_overhead, 2),
        total_sga=round(sga_cost, 2),
        total_profit=round(profit_cost, 2),
        total_logistics=round(total_logistics, 2),
        should_cost=round(should_cost, 2),
        current_price=inp.current_quoted_price,
        gap=round(gap, 2),
        gap_pct=round(gap_pct, 1),
        annual_volume=inp.annual_volume,
        annual_opportunity=round(annual_opportunity, 2),
    )

    # ── Confidence summary ──
    conf = {"high": 0, "medium": 0, "low": 0}
    for item in line_items:
        c = item.confidence.lower()
        if c in conf:
            conf[c] += 1
    confidence_summary = ConfidenceSummary(**conf)

    confidence_warning = None
    total_items = sum(conf.values())
    if total_items > 0 and conf["medium"] > 0.7 * total_items:
        confidence_warning = (
            "WARNING: >70% of assumptions are tagged MEDIUM confidence. "
            "Review and re-tag inputs for better differentiation."
        )

    low_confidence_items = [
        item.item for item in line_items if item.confidence.lower() == "low"
    ]

    # ── Sensitivity analysis (±20%) ──
    sensitivity = _compute_sensitivity(
        inp, should_cost, total_material_cost, total_scrap_credit,
        total_conversion_cost, total_labor_cost, overhead_base, oh
    )

    # ── Volume-price analysis ──
    volume_analysis = _compute_volume_analysis(inp, should_cost, total_material_cost, total_logistics, oh)

    return CostSheetResult(
        product=inp.product_name,
        currency=currency,
        line_items=line_items,
        summary=summary,
        confidence_summary=confidence_summary,
        confidence_warning=confidence_warning,
        low_confidence_items=low_confidence_items,
        sensitivity=sensitivity,
        volume_analysis=volume_analysis,
    )


def _compute_sensitivity(
    inp: CostSheetInput, base_cost: float,
    total_material_cost: float, total_scrap_credit: float,
    total_conversion_cost: float, total_labor_cost: float,
    overhead_base: float, oh,
) -> list[SensitivityItem]:
    """±20% sensitivity on key cost drivers."""
    sensitivity = []
    # Combined overhead/margin multiplier for ripple effect
    margin_mult = (1 + oh.sga_pct) * (1 + oh.profit_margin_pct)

    # Material price sensitivity
    for mat in inp.materials:
        buy_weight = mat.finished_mass_kg / mat.utilization_rate if mat.utilization_rate > 0 else 0
        base_mat = buy_weight * mat.price_per_kg
        for label, factor in [("-20%", 0.8), ("+20%", 1.2)]:
            adjusted = base_mat * factor
            delta = (adjusted - base_mat)
            # Material delta ripples through overhead stack
            new_total = base_cost + delta * (1 + oh.factory_overhead_pct) * margin_mult
            sensitivity.append(SensitivityItem(
                driver=f"{mat.name} price {label}",
                new_should_cost=round(new_total, 2),
                impact=round(new_total - base_cost, 2),
                impact_pct=round((new_total - base_cost) / base_cost * 100, 1) if base_cost > 0 else 0,
            ))

    # Cycle time sensitivity
    total_cycle_conv = sum(
        (s.cycle_time_min / 60) * s.machine_rate_per_hr for s in inp.process_steps
    )
    for label, factor in [("-20%", 0.8), ("+20%", 1.2)]:
        delta = total_cycle_conv * (factor - 1)
        new_total = base_cost + delta * (1 + oh.factory_overhead_pct) * margin_mult
        sensitivity.append(SensitivityItem(
            driver=f"Cycle time {label}",
            new_should_cost=round(new_total, 2),
            impact=round(new_total - base_cost, 2),
            impact_pct=round((new_total - base_cost) / base_cost * 100, 1) if base_cost > 0 else 0,
        ))

    # Labor rate sensitivity
    total_labor = total_labor_cost
    for label, factor in [("-20%", 0.8), ("+20%", 1.2)]:
        delta = total_labor * (factor - 1)
        new_total = base_cost + delta * (1 + oh.factory_overhead_pct) * margin_mult
        sensitivity.append(SensitivityItem(
            driver=f"Labor rate {label}",
            new_should_cost=round(new_total, 2),
            impact=round(new_total - base_cost, 2),
            impact_pct=round((new_total - base_cost) / base_cost * 100, 1) if base_cost > 0 else 0,
        ))

    # Overhead sensitivity
    for label, factor in [("-20%", 0.8), ("+20%", 1.2)]:
        new_oh = overhead_base * oh.factory_overhead_pct * factor
        delta = new_oh - (overhead_base * oh.factory_overhead_pct)
        new_total = base_cost + delta * margin_mult
        sensitivity.append(SensitivityItem(
            driver=f"Factory overhead {label}",
            new_should_cost=round(new_total, 2),
            impact=round(new_total - base_cost, 2),
            impact_pct=round((new_total - base_cost) / base_cost * 100, 1) if base_cost > 0 else 0,
        ))

    return sensitivity


def _compute_volume_analysis(
    inp: CostSheetInput, base_should_cost: float,
    total_material_cost: float, total_logistics: float, oh,
) -> list[VolumeAnalysisItem]:
    """Volume-price analysis at 0.5x, 1x, 2x, 5x annual volume."""
    volume_multipliers = [0.5, 1.0, 2.0, 5.0]
    results = []

    for mult in volume_multipliers:
        vol = int(inp.annual_volume * mult)
        adj_batch = max(50, min(1000, int(inp.batch_size * mult)))

        adj_conversion = 0.0
        adj_labor = 0.0
        for step in inp.process_steps:
            mc = (step.cycle_time_min / 60) * step.machine_rate_per_hr
            sc = (step.setup_time_min / 60) * step.machine_rate_per_hr / adj_batch if adj_batch > 0 else 0
            lt = step.cycle_time_min + (step.setup_time_min / adj_batch if adj_batch > 0 else 0)
            lc = (lt / 60) * step.labor_rate_per_hr * step.operators
            adj_conversion += mc + sc
            adj_labor += lc

        if inp.learning_curve_factor < 1.0:
            adj_conversion *= inp.learning_curve_factor
            adj_labor *= inp.learning_curve_factor

        # Tooling amortization scales with volume
        adj_tooling = 0.0
        if inp.tooling_nre:
            for t in inp.tooling_nre:
                life = max(1, vol * max(1, t.life_units // inp.annual_volume)) if inp.annual_volume > 0 else t.life_units
                adj_tooling += t.cost / max(1, life)

        adj_oh_base = adj_conversion + adj_labor
        adj_oh = adj_oh_base * (oh.factory_overhead_pct + oh.admin_overhead_pct + oh.depreciation_pct + oh.quality_cost_pct)
        adj_factory = total_material_cost + adj_conversion + adj_labor + adj_oh + adj_tooling
        adj_sga = adj_factory * oh.sga_pct
        adj_profit = (adj_factory + adj_sga) * oh.profit_margin_pct
        adj_taxes = (adj_factory + adj_sga) * oh.taxes_duties_pct
        adj_total = adj_factory + adj_sga + adj_profit + adj_taxes + total_logistics

        results.append(VolumeAnalysisItem(
            annual_volume=vol,
            batch_size=adj_batch,
            should_cost_per_unit=round(adj_total, 2),
            delta_vs_base=round(adj_total - base_should_cost, 2),
            delta_pct=round((adj_total - base_should_cost) / base_should_cost * 100, 1) if base_should_cost > 0 else 0,
        ))

    return results
