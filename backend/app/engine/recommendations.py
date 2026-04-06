"""
Rule-based recommendation engine for should-cost analysis.
Registry pattern: rules are registered per commodity type for easy extension.
"""
from dataclasses import dataclass
from typing import Callable
from app.engine.schemas import CostSheetResult


@dataclass
class Recommendation:
    rule_id: str
    severity: str  # "high", "medium", "low"
    title: str
    description: str
    category: str  # "material", "process", "overhead", "pricing", "volume"
    potential_savings_pct: float = 0  # estimated % of total cost


# Rule registry: commodity_type -> list of rule functions
_rule_registry: dict[str, list[Callable]] = {}


def register_rule(commodity_type: str):
    """Decorator to register a recommendation rule for a commodity type."""
    def decorator(func: Callable):
        _rule_registry.setdefault(commodity_type, []).append(func)
        _rule_registry.setdefault("*", [])  # wildcard for all commodities
        return func
    return decorator


def register_global_rule(func: Callable):
    """Decorator to register a rule that applies to all commodity types."""
    _rule_registry.setdefault("*", []).append(func)
    return func


def get_recommendations(result: CostSheetResult, commodity_type: str = "Forging") -> list[Recommendation]:
    """Run all applicable rules and return recommendations."""
    recommendations = []
    rules = _rule_registry.get("*", []) + _rule_registry.get(commodity_type, [])
    for rule_fn in rules:
        rec = rule_fn(result)
        if rec:
            if isinstance(rec, list):
                recommendations.extend(rec)
            else:
                recommendations.append(rec)
    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda r: severity_order.get(r.severity, 3))
    return recommendations


# ── Global rules (apply to all commodities) ──

@register_global_rule
def rule_rm_high_share(result: CostSheetResult) -> Recommendation | None:
    """RM_HIGH_SHARE: Material > 60% of total."""
    s = result.summary
    if s.should_cost > 0 and s.total_material_net / s.should_cost > 0.60:
        pct = s.total_material_net / s.should_cost * 100
        return Recommendation(
            rule_id="RM_HIGH_SHARE",
            severity="high",
            title="Material cost dominates total cost",
            description=(
                f"Raw material accounts for {pct:.0f}% of total should-cost. "
                f"Focus negotiation on material pricing, explore alternative grades, "
                f"increase utilization rate, or negotiate commodity index-linked contracts."
            ),
            category="material",
            potential_savings_pct=5.0,
        )


@register_global_rule
def rule_low_utilization(result: CostSheetResult) -> Recommendation | None:
    """LOW_UTILIZATION: Utilization < 70% (high scrap)."""
    s = result.summary
    if s.total_material_gross > 0:
        util = s.total_material_net / s.total_material_gross if s.total_material_gross > 0 else 1
        # Approximate: if scrap credit is large relative to gross, utilization is low
        if s.total_material_gross > 0:
            effective_util = 1 - (abs(s.total_scrap_credit) / s.total_material_gross) if s.total_material_gross > 0 else 1
            if effective_util < 0.70:
                return Recommendation(
                    rule_id="LOW_UTILIZATION",
                    severity="medium",
                    title="Low material utilization detected",
                    description=(
                        f"Effective material utilization is approximately {effective_util:.0%}. "
                        f"Consider near-net-shape processes, die optimization, or material grade changes "
                        f"to improve buy-to-fly ratio."
                    ),
                    category="material",
                    potential_savings_pct=3.0,
                )


@register_global_rule
def rule_high_scrap_no_credit(result: CostSheetResult) -> Recommendation | None:
    """HIGH_SCRAP_NO_CREDIT: Scrap > 20% without meaningful recovery."""
    s = result.summary
    if s.total_material_gross > 0:
        scrap_pct = abs(s.total_scrap_credit) / s.total_material_gross
        if scrap_pct < 0.05 and s.total_material_gross > s.total_material_net * 1.2:
            return Recommendation(
                rule_id="HIGH_SCRAP_NO_CREDIT",
                severity="high",
                title="High scrap with minimal recovery credit",
                description=(
                    "Material scrap exceeds 20% of gross weight but scrap recovery credit is minimal. "
                    "Negotiate scrap return/credit terms, verify scrap recovery percentages, "
                    "or explore suppliers with better scrap management programs."
                ),
                category="material",
                potential_savings_pct=4.0,
            )


@register_global_rule
def rule_setup_dominant(result: CostSheetResult) -> Recommendation | None:
    """SETUP_DOMINANT: Setup > 15% of conversion cost."""
    conv_items = [i for i in result.line_items if i.category == "Conversion"]
    if not conv_items:
        return None
    total_conv = sum(i.value for i in conv_items)
    # Look for "Setup" mentions in detail
    setup_cost = 0
    for item in conv_items:
        if "Setup:" in item.detail:
            try:
                # Extract setup cost from detail string
                parts = item.detail.split("Setup:")
                if len(parts) > 1:
                    setup_str = parts[1].split("/part")[0].strip().replace(result.currency, "").strip()
                    setup_cost += float(setup_str)
            except (ValueError, IndexError):
                pass
    if total_conv > 0 and setup_cost / total_conv > 0.15:
        return Recommendation(
            rule_id="SETUP_DOMINANT",
            severity="medium",
            title="Setup costs are a significant portion of conversion",
            description=(
                f"Setup costs represent {setup_cost / total_conv:.0%} of total conversion cost. "
                f"Consider larger batch sizes, SMED (quick changeover) techniques, "
                f"or dedicated tooling to reduce setup time impact."
            ),
            category="process",
            potential_savings_pct=2.0,
        )


@register_global_rule
def rule_gap_significant(result: CostSheetResult) -> Recommendation | None:
    """GAP_SIGNIFICANT: Gap > 15% between quoted and should-cost."""
    s = result.summary
    if s.current_price > 0 and s.gap_pct > 15:
        return Recommendation(
            rule_id="GAP_SIGNIFICANT",
            severity="high",
            title=f"Significant price gap of {s.gap_pct:.1f}%",
            description=(
                f"The quoted price ({result.currency} {s.current_price:.2f}) is {s.gap_pct:.1f}% above "
                f"the should-cost ({result.currency} {s.should_cost:.2f}). "
                f"Annual savings opportunity: {result.currency} {s.annual_opportunity:,.0f}. "
                f"Recommend detailed should-cost discussion with supplier, competitive benchmarking, "
                f"and structured negotiation with this cost model as basis."
            ),
            category="pricing",
            potential_savings_pct=s.gap_pct * 0.5,  # Assume can capture ~50% of gap
        )


@register_global_rule
def rule_gap_negative(result: CostSheetResult) -> Recommendation | None:
    """GAP_NEGATIVE: Gap < -5% (vendor underpricing risk)."""
    s = result.summary
    if s.current_price > 0 and s.gap_pct < -5:
        return Recommendation(
            rule_id="GAP_NEGATIVE",
            severity="medium",
            title="Vendor may be underpricing — supply risk",
            description=(
                f"The quoted price is {abs(s.gap_pct):.1f}% BELOW the should-cost estimate. "
                f"This may indicate: (a) the supplier has structural cost advantages not in our model, "
                f"(b) the supplier is buying the business at unsustainable margins, or "
                f"(c) our model overestimates some costs. Validate assumptions and assess supply continuity risk."
            ),
            category="pricing",
            potential_savings_pct=0,
        )


@register_global_rule
def rule_overhead_high(result: CostSheetResult) -> Recommendation | None:
    """OVERHEAD_HIGH: Overhead > 25% of total."""
    s = result.summary
    if s.should_cost > 0 and s.total_overhead / s.should_cost > 0.25:
        pct = s.total_overhead / s.should_cost * 100
        return Recommendation(
            rule_id="OVERHEAD_HIGH",
            severity="medium",
            title=f"Overhead represents {pct:.0f}% of total cost",
            description=(
                "Factory overhead is a large share of total cost. "
                "Request supplier's overhead allocation methodology, compare against industry benchmarks, "
                "and evaluate if multi-shift operation or volume commitments could improve absorption."
            ),
            category="overhead",
            potential_savings_pct=2.0,
        )


@register_global_rule
def rule_single_process_dominant(result: CostSheetResult) -> Recommendation | None:
    """SINGLE_PROCESS_DOMINANT: One step > 40% of conversion."""
    conv_items = [i for i in result.line_items if i.category == "Conversion"]
    total_conv = sum(i.value for i in conv_items)
    if total_conv <= 0 or len(conv_items) < 2:
        return None
    for item in conv_items:
        if item.value / total_conv > 0.40:
            return Recommendation(
                rule_id="SINGLE_PROCESS_DOMINANT",
                severity="low",
                title=f"'{item.item}' dominates conversion cost",
                description=(
                    f"This single process step accounts for {item.value / total_conv:.0%} of total conversion. "
                    f"Focus cycle time reduction efforts here for maximum impact. "
                    f"Consider machine upgrades, tooling optimization, or alternative processes."
                ),
                category="process",
                potential_savings_pct=2.0,
            )
    return None


@register_global_rule
def rule_volume_leverage(result: CostSheetResult) -> Recommendation | None:
    """VOLUME_LEVERAGE: >10% reduction at 2x volume."""
    for va in result.volume_analysis:
        if va.annual_volume == result.summary.annual_volume * 2:
            if va.delta_pct < -10:
                return Recommendation(
                    rule_id="VOLUME_LEVERAGE",
                    severity="medium",
                    title=f"Strong volume leverage: {abs(va.delta_pct):.1f}% reduction at 2x volume",
                    description=(
                        f"Doubling annual volume to {va.annual_volume:,} units reduces per-unit cost by "
                        f"{abs(va.delta_pct):.1f}%. Consider volume commitments, multi-year agreements, "
                        f"or demand aggregation across similar parts to capture this leverage."
                    ),
                    category="volume",
                    potential_savings_pct=abs(va.delta_pct) * 0.3,
                )
    return None


@register_global_rule
def rule_confidence_low(result: CostSheetResult) -> Recommendation | None:
    """CONFIDENCE_LOW: >30% of items have LOW confidence."""
    cs = result.confidence_summary
    total = cs.high + cs.medium + cs.low
    if total > 0 and cs.low / total > 0.30:
        return Recommendation(
            rule_id="CONFIDENCE_LOW",
            severity="low",
            title="Many assumptions have low confidence",
            description=(
                f"{cs.low} of {total} line items are tagged LOW confidence. "
                f"Items: {', '.join(result.low_confidence_items[:5])}. "
                f"Prioritize validating these assumptions before using this model in negotiations. "
                f"Request supplier data or conduct market research for these items."
            ),
            category="pricing",
            potential_savings_pct=0,
        )
    return None


# ── Forging-specific rules ──

@register_rule("Forging")
def rule_forging_die_life(result: CostSheetResult) -> Recommendation | None:
    """Check for forging-specific die/tooling optimization opportunities."""
    tooling_items = [i for i in result.line_items if i.category == "Tooling/NRE"]
    if tooling_items:
        total_tooling = sum(i.value for i in tooling_items)
        if result.summary.should_cost > 0 and total_tooling / result.summary.should_cost > 0.08:
            return Recommendation(
                rule_id="FORGING_DIE_COST",
                severity="medium",
                title="Forging die/tooling cost is significant",
                description=(
                    "Tooling represents >8% of per-unit cost. For forging, consider: "
                    "multi-impression dies, die life extension through heat treatment, "
                    "or amortizing over longer production runs. Negotiate die ownership "
                    "and maintenance responsibilities."
                ),
                category="process",
                potential_savings_pct=2.0,
            )
    return None
