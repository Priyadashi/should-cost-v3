import json

# ============================================================
# SHOULD-COST CALCULATION ENGINE v2
# Fill in all variables below from your analysis, then execute.
# Features: scrap credit, tooling/NRE, learning curve,
#           confidence classification, volume-price analysis
# ============================================================

# --- PRODUCT IDENTIFICATION ---
product_name = "___"
currency = "___"  # e.g., "USD", "INR", "EUR"
current_quoted_price = ___  # per unit in the specified currency
annual_volume = ___  # units per year

# --- MATERIAL INPUTS ---
materials = [
    {
        "name": "___",
        "grade": "___",
        "finished_mass_kg": ___,
        "utilization_rate": ___,  # 0.0 to 1.0 (e.g., 0.65 = 65%)
        "price_per_kg": ___,
        "scrap_recovery_pct": ___,  # 0.0 to 1.0 — fraction of purchased price recovered from scrap (e.g., 0.35 = 35%)
        "price_source": "___",  # e.g., "LME spot 2026-03-17 via web search", "user provided"
        "confidence": "___"  # "high", "medium", "low" — apply classification rules from skill.md
    }
]

# --- PROCESS STEPS ---
process_steps = [
    {
        "step_name": "___",
        "machine_type": "___",
        "machine_rate_per_hr": ___,
        "cycle_time_min": ___,
        "setup_time_min": ___,
        "operators": ___,
        "labor_rate_per_hr": ___,
        "rate_source": "___",
        "confidence": "___"
    }
]

batch_size = ___  # parts per production batch

# --- TOOLING AND NRE ---
# One-time costs amortized over the expected production life
tooling_nre = [
    {
        "item": "___",  # e.g., "CNC fixture (2x)", "Programming NRE", "Inspection gauge"
        "cost": ___,  # total one-time cost
        "life_units": ___,  # number of units over which to amortize (e.g., annual_volume * contract_years)
        "source": "___",
        "confidence": "___"
    }
]

# --- LEARNING CURVE ---
# Applies a cost reduction to conversion + labor based on cumulative volume.
# Set to 1.0 to disable. Typical: 0.95 = 5% reduction from learning effects.
# Use only when annual volume > 2,000 and the part has been in production > 1 year.
learning_curve_factor = ___  # 0.0 to 1.0 (e.g., 0.95 = 5% learning-driven cost reduction)
learning_curve_source = "___"  # e.g., "Wright learning curve, 95% slope, cumulative 10K units"

# --- OVERHEAD AND MARGIN ---
factory_overhead_pct = ___
sga_pct = ___
profit_pct = ___
overhead_source = "___"
overhead_confidence = "___"

# --- LOGISTICS ---
packaging_per_unit = ___
freight_per_unit = ___
other_logistics_per_unit = ___  # tariffs, duties, outsourced surface treatment, etc.
logistics_source = "___"

# ============================================================
# CALCULATION
# ============================================================

results = {"product": product_name, "currency": currency, "line_items": [], "summary": {}}

# 1. Material cost (with scrap credit)
total_material_cost = 0
total_scrap_credit = 0
for mat in materials:
    buy_weight = mat["finished_mass_kg"] / mat["utilization_rate"]
    gross_mat_cost = buy_weight * mat["price_per_kg"]
    scrap_weight = buy_weight - mat["finished_mass_kg"]
    scrap_credit = scrap_weight * mat["price_per_kg"] * mat["scrap_recovery_pct"]
    net_mat_cost = gross_mat_cost - scrap_credit
    total_material_cost += net_mat_cost
    total_scrap_credit += scrap_credit
    results["line_items"].append({
        "category": "Material",
        "item": f"{mat['name']} ({mat['grade']})",
        "value": round(net_mat_cost, 2),
        "detail": (f"{mat['finished_mass_kg']}kg finished / {mat['utilization_rate']:.0%} util = {buy_weight:.2f}kg buy "
                   f"x {currency} {mat['price_per_kg']:.2f}/kg = {currency} {gross_mat_cost:.2f} gross "
                   f"- {currency} {scrap_credit:.2f} scrap credit ({scrap_weight:.2f}kg x {mat['scrap_recovery_pct']:.0%} recovery)"),
        "source": mat["price_source"],
        "confidence": mat["confidence"]
    })

# 2. Conversion cost (machine + labor per process step)
total_conversion_cost = 0
total_labor_cost = 0
for step in process_steps:
    machine_cost = (step["cycle_time_min"] / 60) * step["machine_rate_per_hr"]
    setup_cost_per_part = (step["setup_time_min"] / 60) * step["machine_rate_per_hr"] / batch_size
    labor_time_min = step["cycle_time_min"] + (step["setup_time_min"] / batch_size)
    labor_cost = (labor_time_min / 60) * step["labor_rate_per_hr"] * step["operators"]
    step_total = machine_cost + setup_cost_per_part + labor_cost
    total_conversion_cost += machine_cost + setup_cost_per_part
    total_labor_cost += labor_cost
    results["line_items"].append({
        "category": "Conversion",
        "item": f"{step['step_name']} ({step['machine_type']})",
        "value": round(step_total, 2),
        "detail": (f"Machine: {step['cycle_time_min']:.1f}min x {currency} {step['machine_rate_per_hr']}/hr "
                   f"= {currency} {machine_cost:.2f} + Setup: {currency} {setup_cost_per_part:.2f}/part "
                   f"+ Labor: {currency} {labor_cost:.2f}"),
        "source": step["rate_source"],
        "confidence": step["confidence"]
    })

# 2b. Apply learning curve to conversion + labor
if learning_curve_factor < 1.0:
    learning_reduction_conversion = total_conversion_cost * (1 - learning_curve_factor)
    learning_reduction_labor = total_labor_cost * (1 - learning_curve_factor)
    total_conversion_cost -= learning_reduction_conversion
    total_labor_cost -= learning_reduction_labor
    results["line_items"].append({
        "category": "Learning Curve",
        "item": f"Learning curve adjustment ({(1-learning_curve_factor):.0%} reduction)",
        "value": round(-(learning_reduction_conversion + learning_reduction_labor), 2),
        "detail": (f"Conversion: -{currency} {learning_reduction_conversion:.2f}, "
                   f"Labor: -{currency} {learning_reduction_labor:.2f}"),
        "source": learning_curve_source,
        "confidence": "medium"
    })

# 2c. Tooling / NRE amortization
total_tooling_per_unit = 0
for tool in tooling_nre:
    per_unit = tool["cost"] / tool["life_units"] if tool["life_units"] > 0 else 0
    total_tooling_per_unit += per_unit
    results["line_items"].append({
        "category": "Tooling/NRE",
        "item": tool["item"],
        "value": round(per_unit, 2),
        "detail": f"{currency} {tool['cost']:.0f} total / {tool['life_units']} units = {currency} {per_unit:.2f}/unit",
        "source": tool["source"],
        "confidence": tool["confidence"]
    })

# 3. Factory overhead
overhead_base = total_conversion_cost + total_labor_cost
overhead_cost = overhead_base * factory_overhead_pct
results["line_items"].append({
    "category": "Overhead",
    "item": f"Factory overhead ({factory_overhead_pct:.0%} of conversion + labor)",
    "value": round(overhead_cost, 2),
    "detail": f"{currency} {overhead_base:.2f} x {factory_overhead_pct:.0%}",
    "source": overhead_source,
    "confidence": overhead_confidence
})

# 4. Total factory cost
total_factory_cost = (total_material_cost + total_conversion_cost + total_labor_cost
                      + overhead_cost + total_tooling_per_unit)

# 5. SGA
sga_cost = total_factory_cost * sga_pct
results["line_items"].append({
    "category": "SGA",
    "item": f"Selling, general & admin ({sga_pct:.0%} of factory cost)",
    "value": round(sga_cost, 2),
    "detail": f"{currency} {total_factory_cost:.2f} x {sga_pct:.0%}",
    "source": overhead_source,
    "confidence": overhead_confidence
})

# 6. Profit
profit_base = total_factory_cost + sga_cost
profit_cost = profit_base * profit_pct
results["line_items"].append({
    "category": "Profit",
    "item": f"Supplier profit ({profit_pct:.0%})",
    "value": round(profit_cost, 2),
    "detail": f"{currency} {profit_base:.2f} x {profit_pct:.0%}",
    "source": overhead_source,
    "confidence": overhead_confidence
})

# 7. Logistics
total_logistics = packaging_per_unit + freight_per_unit + other_logistics_per_unit
if total_logistics > 0:
    results["line_items"].append({
        "category": "Logistics",
        "item": "Packaging + freight + outsourced processes",
        "value": round(total_logistics, 2),
        "detail": (f"Pkg: {currency} {packaging_per_unit:.2f} + Freight: {currency} {freight_per_unit:.2f} "
                   f"+ Other: {currency} {other_logistics_per_unit:.2f}"),
        "source": logistics_source,
        "confidence": "medium"
    })

# 8. Total should-cost
should_cost = (total_material_cost + total_conversion_cost + total_labor_cost
               + overhead_cost + total_tooling_per_unit + sga_cost + profit_cost + total_logistics)
gap = current_quoted_price - should_cost
gap_pct = (gap / current_quoted_price) * 100 if current_quoted_price > 0 else 0
annual_opportunity = gap * annual_volume

results["summary"] = {
    "total_material_gross": round(total_material_cost + total_scrap_credit, 2),
    "total_scrap_credit": round(-total_scrap_credit, 2),
    "total_material_net": round(total_material_cost, 2),
    "total_conversion": round(total_conversion_cost, 2),
    "total_labor": round(total_labor_cost, 2),
    "total_tooling_nre": round(total_tooling_per_unit, 2),
    "total_overhead": round(overhead_cost, 2),
    "total_sga": round(sga_cost, 2),
    "total_profit": round(profit_cost, 2),
    "total_logistics": round(total_logistics, 2),
    "should_cost": round(should_cost, 2),
    "current_price": current_quoted_price,
    "gap": round(gap, 2),
    "gap_pct": round(gap_pct, 1),
    "annual_volume": annual_volume,
    "annual_opportunity": round(annual_opportunity, 2)
}

# --- CONFIDENCE SUMMARY ---
conf_counts = {"high": 0, "medium": 0, "low": 0}
for item in results["line_items"]:
    c = item.get("confidence", "medium").lower()
    if c in conf_counts:
        conf_counts[c] += 1
results["confidence_summary"] = conf_counts

# Confidence validation warning
total_items = sum(conf_counts.values())
if total_items > 0 and conf_counts["medium"] > 0.7 * total_items:
    results["confidence_warning"] = (
        "WARNING: >70% of assumptions are tagged MEDIUM confidence. "
        "Review the classification rules in skill.md and re-tag inputs: "
        "user-provided or live-fetched data should be HIGH; "
        "geometry-inferred or proxy-region estimates should be LOW. "
        "Undifferentiated confidence reduces the reviewer's ability to prioritize validation."
    )
if conf_counts["low"] > 0:
    low_items = [item["item"] for item in results["line_items"] if item.get("confidence", "").lower() == "low"]
    results["low_confidence_items"] = low_items

# --- SENSITIVITY ANALYSIS ---
sensitivity = []
base_cost = should_cost

# Material price sensitivity
for mat in materials:
    for direction, factor in [("-20%", 0.8), ("+20%", 1.2)]:
        adjusted_mat_cost = (mat["finished_mass_kg"] / mat["utilization_rate"]) * mat["price_per_kg"] * factor
        delta = adjusted_mat_cost - (mat["finished_mass_kg"] / mat["utilization_rate"]) * mat["price_per_kg"]
        new_total = base_cost + delta * (1 + factory_overhead_pct) * (1 + sga_pct) * (1 + profit_pct)
        sensitivity.append({
            "driver": f"{mat['name']} price {direction}",
            "new_should_cost": round(new_total, 2),
            "impact": round(new_total - base_cost, 2),
            "impact_pct": round((new_total - base_cost) / base_cost * 100, 1)
        })

# Cycle time sensitivity
total_cycle_conversion = sum((s["cycle_time_min"]/60) * s["machine_rate_per_hr"] for s in process_steps)
for direction, factor in [("-20%", 0.8), ("+20%", 1.2)]:
    delta = total_cycle_conversion * (factor - 1)
    new_total = base_cost + delta * (1 + factory_overhead_pct) * (1 + sga_pct) * (1 + profit_pct)
    sensitivity.append({
        "driver": f"Cycle time {direction}",
        "new_should_cost": round(new_total, 2),
        "impact": round(new_total - base_cost, 2),
        "impact_pct": round((new_total - base_cost) / base_cost * 100, 1)
    })

# Labor rate sensitivity
for direction, factor in [("-20%", 0.8), ("+20%", 1.2)]:
    delta = total_labor_cost * (factor - 1)
    new_total = base_cost + delta * (1 + factory_overhead_pct) * (1 + sga_pct) * (1 + profit_pct)
    sensitivity.append({
        "driver": f"Labor rate {direction}",
        "new_should_cost": round(new_total, 2),
        "impact": round(new_total - base_cost, 2),
        "impact_pct": round((new_total - base_cost) / base_cost * 100, 1)
    })

# Overhead sensitivity
for direction, factor in [("-20%", 0.8), ("+20%", 1.2)]:
    new_oh = overhead_base * factory_overhead_pct * factor
    delta = new_oh - overhead_cost
    new_total = base_cost + delta * (1 + sga_pct) * (1 + profit_pct)
    sensitivity.append({
        "driver": f"Factory overhead {direction}",
        "new_should_cost": round(new_total, 2),
        "impact": round(new_total - base_cost, 2),
        "impact_pct": round((new_total - base_cost) / base_cost * 100, 1)
    })

results["sensitivity"] = sensitivity

# --- VOLUME-PRICE ANALYSIS ---
volume_multipliers = [0.5, 1.0, 2.0, 5.0]
volume_analysis = []
for mult in volume_multipliers:
    vol = int(annual_volume * mult)
    adj_batch = max(50, min(1000, int(batch_size * mult)))
    adj_conversion = 0
    adj_labor = 0
    for step in process_steps:
        mc = (step["cycle_time_min"] / 60) * step["machine_rate_per_hr"]
        sc = (step["setup_time_min"] / 60) * step["machine_rate_per_hr"] / adj_batch
        lt = step["cycle_time_min"] + (step["setup_time_min"] / adj_batch)
        lc = (lt / 60) * step["labor_rate_per_hr"] * step["operators"]
        adj_conversion += mc + sc
        adj_labor += lc
    if learning_curve_factor < 1.0:
        adj_conversion *= learning_curve_factor
        adj_labor *= learning_curve_factor
    adj_tooling = sum(t["cost"] / max(1, vol * max(1, t["life_units"] // annual_volume)) for t in tooling_nre) if tooling_nre else 0
    adj_oh_base = adj_conversion + adj_labor
    adj_oh = adj_oh_base * factory_overhead_pct
    adj_factory = total_material_cost + adj_conversion + adj_labor + adj_oh + adj_tooling
    adj_sga = adj_factory * sga_pct
    adj_profit = (adj_factory + adj_sga) * profit_pct
    adj_total = adj_factory + adj_sga + adj_profit + total_logistics
    volume_analysis.append({
        "annual_volume": vol,
        "batch_size": adj_batch,
        "should_cost_per_unit": round(adj_total, 2),
        "delta_vs_base": round(adj_total - should_cost, 2),
        "delta_pct": round((adj_total - should_cost) / should_cost * 100, 1) if should_cost > 0 else 0
    })

results["volume_analysis"] = volume_analysis

# --- OUTPUT ---
print(json.dumps(results, indent=2))
