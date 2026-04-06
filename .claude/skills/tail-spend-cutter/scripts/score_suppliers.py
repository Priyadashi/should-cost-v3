#!/usr/bin/env python3
"""
Supplier Scoring & Consolidation Clustering

Usage:
    python score_suppliers.py <cleaned_spend.csv> [--pareto <pareto.json>]
        [--category-summary <cat.json>] [--output-dir <dir>] [--weights <weights.json>]

Reads cleaned supplier-level spend data and produces:
    - supplier_scores.csv           20-factor scores + composite CPS/SPS/RS
    - consolidation_clusters.json   Grouped opportunities with recommended actions
    - savings_estimates.json        Per-cluster and total savings projections
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Default dimension and factor weights
# ---------------------------------------------------------------------------
DEFAULT_DIMENSION_WEIGHTS = {
    "financial": 0.30,
    "relationship": 0.15,
    "geographic": 0.10,
    "performance": 0.25,
    "market": 0.20,
}

# Factors per dimension with equal sub-weights (computed at runtime)
DIMENSION_FACTORS = {
    "financial": [
        "share_of_category_spend", "absolute_spend", "order_frequency",
        "avg_order_size", "payment_terms", "spend_trend",
    ],
    "relationship": [
        "supplier_duration", "contract_status", "usage_breadth",
    ],
    "geographic": [
        "domestic_international", "distance_to_facility",
    ],
    "performance": [
        "quality_score", "delivery_performance", "financial_stability",
        "switching_cost",
    ],
    "market": [
        "num_alternatives", "category_criticality", "market_concentration",
        "price_transparency", "substitutability",
    ],
}

NEUTRAL_SCORE = 3.0  # assigned when data is missing

# Category savings benchmarks (midpoint of typical range from benchmarks.md)
CATEGORY_SAVINGS = {
    "Office Supplies": 0.20,
    "IT Hardware": 0.115,
    "IT Software": 0.15,
    "Facilities": 0.16,
    "Marketing": 0.14,
    "Travel & Entertainment": 0.115,
    "Professional Services": 0.085,
    "Temporary Staffing": 0.115,
    "MRO": 0.17,
    "Telecom": 0.14,
    "Printing/Shipping": 0.225,
    "Catering/Food": 0.14,
    "Training": 0.15,
    "Uniforms/Safety": 0.20,
    "General": 0.115,
}

DEFAULT_FEASIBILITY = 0.5


def _score_1_5(value, low, mid, high):
    """Map a numeric value to 1-5 scale using 3 breakpoints."""
    if pd.isna(value):
        return NEUTRAL_SCORE
    if value <= low:
        return 1.0
    elif value <= mid:
        return 1.0 + (value - low) / (mid - low) * 2.0
    elif value <= high:
        return 3.0 + (value - mid) / (high - mid) * 2.0
    else:
        return 5.0


def _score_inverted_1_5(value, low, mid, high):
    """Inverted scale: high value = low score."""
    return 6.0 - _score_1_5(value, low, mid, high)


def compute_factor_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all 20 factor scores (1-5) from available data.
    Missing factors get NEUTRAL_SCORE.
    """
    scores = pd.DataFrame(index=df.index)
    scores["supplier"] = df["supplier"]

    # --- Financial/Volume ---
    if "total_spend" in df.columns and "primary_category" in df.columns:
        cat_totals = df.groupby("primary_category")["total_spend"].transform("sum")
        scores["share_of_category_spend"] = (df["total_spend"] / cat_totals * 100).apply(
            lambda x: _score_1_5(x, 1, 5, 15))
    elif "total_spend" in df.columns:
        total = df["total_spend"].sum()
        scores["share_of_category_spend"] = (df["total_spend"] / total * 100).apply(
            lambda x: _score_1_5(x, 0.1, 1, 5))
    else:
        scores["share_of_category_spend"] = NEUTRAL_SCORE

    if "total_spend" in df.columns:
        scores["absolute_spend"] = df["total_spend"].apply(
            lambda x: _score_1_5(x, 10000, 50000, 200000))
    else:
        scores["absolute_spend"] = NEUTRAL_SCORE

    if "transaction_count" in df.columns:
        scores["order_frequency"] = df["transaction_count"].apply(
            lambda x: _score_1_5(x, 2, 6, 15))
    else:
        scores["order_frequency"] = NEUTRAL_SCORE

    if "avg_transaction" in df.columns:
        scores["avg_order_size"] = df["avg_transaction"].apply(
            lambda x: _score_1_5(x, 500, 2500, 10000))
    else:
        scores["avg_order_size"] = NEUTRAL_SCORE

    # Payment terms and spend trend usually require extra data columns
    scores["payment_terms"] = df.get("payment_terms_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["spend_trend"] = df.get("spend_trend_score", pd.Series(NEUTRAL_SCORE, index=df.index))

    # --- Relationship ---
    scores["supplier_duration"] = df.get("duration_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["contract_status"] = df.get("contract_score", pd.Series(NEUTRAL_SCORE, index=df.index))

    if "categories" in df.columns:
        scores["usage_breadth"] = df["categories"].apply(
            lambda x: _score_1_5(x, 1, 2, 4) if pd.notna(x) else NEUTRAL_SCORE)
    else:
        scores["usage_breadth"] = NEUTRAL_SCORE

    # --- Geographic ---
    scores["domestic_international"] = df.get("geo_domestic_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["distance_to_facility"] = df.get("geo_distance_score", pd.Series(NEUTRAL_SCORE, index=df.index))

    # --- Performance & Risk ---
    scores["quality_score"] = df.get("quality_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["delivery_performance"] = df.get("delivery_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["financial_stability"] = df.get("fin_stability_score", pd.Series(NEUTRAL_SCORE, index=df.index))

    # Switching cost: inversely related to number of alternatives and spend concentration
    if "total_spend" in df.columns:
        spend_pct = df["total_spend"] / df["total_spend"].sum() * 100
        scores["switching_cost"] = spend_pct.apply(
            lambda x: _score_inverted_1_5(x, 0.5, 2, 10))
    else:
        scores["switching_cost"] = NEUTRAL_SCORE

    # --- Market ---
    if "primary_category" in df.columns:
        cat_supplier_counts = df.groupby("primary_category")["supplier"].transform("count")
        scores["num_alternatives"] = cat_supplier_counts.apply(
            lambda x: _score_1_5(x, 1, 3, 8))
    else:
        scores["num_alternatives"] = NEUTRAL_SCORE

    scores["category_criticality"] = df.get("criticality_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["market_concentration"] = df.get("concentration_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["price_transparency"] = df.get("transparency_score", pd.Series(NEUTRAL_SCORE, index=df.index))
    scores["substitutability"] = df.get("substitutability_score", pd.Series(NEUTRAL_SCORE, index=df.index))

    return scores


def compute_composite_scores(scores: pd.DataFrame,
                             dim_weights: dict = None) -> pd.DataFrame:
    """Compute CPS, SPS, and RS composite scores."""
    if dim_weights is None:
        dim_weights = DEFAULT_DIMENSION_WEIGHTS.copy()

    result = scores[["supplier"]].copy()

    # CPS: weighted average of all dimensions
    dim_scores = {}
    for dim, factors in DIMENSION_FACTORS.items():
        available = [f for f in factors if f in scores.columns]
        if available:
            # Exclude factors that are all neutral (no real data)
            real_factors = [f for f in available
                           if not (scores[f] == NEUTRAL_SCORE).all()]
            if real_factors:
                dim_scores[dim] = scores[real_factors].mean(axis=1)
            else:
                dim_scores[dim] = pd.Series(NEUTRAL_SCORE, index=scores.index)
        else:
            dim_scores[dim] = pd.Series(NEUTRAL_SCORE, index=scores.index)

    # Renormalize weights if any dimension is entirely neutral
    active_dims = {d: w for d, w in dim_weights.items()
                   if not (dim_scores[d] == NEUTRAL_SCORE).all()}
    if active_dims:
        total_w = sum(active_dims.values())
        norm_weights = {d: w / total_w for d, w in active_dims.items()}
    else:
        norm_weights = dim_weights

    cps = pd.Series(0.0, index=scores.index)
    for dim, weight in norm_weights.items():
        cps += dim_scores.get(dim, NEUTRAL_SCORE) * weight
    result["CPS"] = cps.round(2)

    # SPS: savings potential (0-1)
    sps_factors = {
        "num_alternatives": 0.30,
        "absolute_spend": 0.25,
        "switching_cost": 0.25,  # inverted: low switching = high savings potential
        "price_transparency": 0.20,
    }
    sps = pd.Series(0.0, index=scores.index)
    for factor, weight in sps_factors.items():
        if factor in scores.columns:
            # Normalize 1-5 to 0-1
            if factor == "switching_cost":
                # Already inverted in factor scoring
                norm = (scores[factor] - 1) / 4
            else:
                norm = (scores[factor] - 1) / 4
            sps += norm * weight
    result["SPS"] = sps.clip(0, 1).round(3)

    # RS: risk score (0-1)
    rs_factors = {
        "category_criticality": 0.30,
        "switching_cost": 0.25,
        "quality_score": 0.20,
        "financial_stability": 0.15,
        "market_concentration": 0.10,
    }
    rs = pd.Series(0.0, index=scores.index)
    for factor, weight in rs_factors.items():
        if factor in scores.columns:
            if factor == "switching_cost":
                # High switching cost = high risk (invert the inversion)
                norm = 1 - (scores[factor] - 1) / 4
            elif factor in ("quality_score", "financial_stability"):
                # Low quality/stability = high risk
                norm = 1 - (scores[factor] - 1) / 4
            else:
                norm = (scores[factor] - 1) / 4
            rs += norm * weight
    result["RS"] = rs.clip(0, 1).round(3)

    # Decision matrix
    def decide(row):
        cps_val, rs_val = row["CPS"], row["RS"]
        if cps_val >= 4.0:
            if rs_val < 0.3:
                return "Eliminate"
            elif rs_val < 0.6:
                return "Consolidate"
            else:
                return "Renegotiate"
        elif cps_val >= 3.0:
            if rs_val > 0.6:
                return "Renegotiate"
            else:
                return "Consolidate"
        elif cps_val >= 2.0:
            if rs_val > 0.6:
                return "Retain"
            else:
                return "Renegotiate"
        else:
            return "Retain"

    result["recommendation"] = result.apply(decide, axis=1)

    return result


def build_clusters(scored_df: pd.DataFrame, spend_df: pd.DataFrame) -> list:
    """Group tail suppliers into consolidation clusters by category."""
    clusters = []

    if "primary_category" not in spend_df.columns:
        # Single cluster for all tail suppliers
        tail = scored_df[scored_df["recommendation"].isin(
            ["Eliminate", "Consolidate"])].copy()
        if len(tail) > 0:
            tail_spend = spend_df[spend_df["supplier"].isin(tail["supplier"])]
            clusters.append({
                "cluster_id": 1,
                "category": "All Categories",
                "supplier_count": len(tail),
                "total_spend": float(tail_spend["total_spend"].sum()) if "total_spend" in tail_spend.columns else 0,
                "suppliers": tail["supplier"].tolist(),
                "primary_action": tail["recommendation"].mode().iloc[0] if len(tail) > 0 else "Consolidate",
                "strategy": "Category Consolidation",
            })
        return clusters

    merged = scored_df.merge(
        spend_df[["supplier", "total_spend", "primary_category", "segment"]],
        on="supplier", how="left")

    # Only cluster tail & core suppliers (not head)
    tail_core = merged[merged["segment"].isin(["Tail", "Core"])].copy()

    for cat_id, (category, group) in enumerate(
            tail_core.groupby("primary_category"), 1):
        actionable = group[group["recommendation"].isin(
            ["Eliminate", "Consolidate", "Renegotiate"])]
        if len(actionable) < 2:
            continue

        # Determine best strategy based on cluster profile
        n_suppliers = len(actionable)
        avg_spend = actionable["total_spend"].mean() if "total_spend" in actionable.columns else 0
        eliminate_count = (actionable["recommendation"] == "Eliminate").sum()

        if n_suppliers > 5 and avg_spend < 10000:
            strategy = "Category Consolidation"
        elif n_suppliers <= 5 and avg_spend > 25000:
            strategy = "Volume Bundling"
        elif eliminate_count > n_suppliers * 0.5:
            strategy = "Supplier Elimination"
        else:
            strategy = "Contract Renegotiation"

        cluster = {
            "cluster_id": cat_id,
            "category": category,
            "supplier_count": len(actionable),
            "total_spend": float(actionable["total_spend"].sum()) if "total_spend" in actionable.columns else 0,
            "suppliers": actionable["supplier"].tolist(),
            "recommendations": actionable["recommendation"].value_counts().to_dict(),
            "avg_cps": float(actionable["CPS"].mean()),
            "avg_sps": float(actionable["SPS"].mean()),
            "avg_rs": float(actionable["RS"].mean()),
            "primary_action": actionable["recommendation"].mode().iloc[0],
            "strategy": strategy,
        }
        clusters.append(cluster)

    clusters.sort(key=lambda c: c["total_spend"], reverse=True)
    return clusters


def estimate_savings(clusters: list, feasibility: float = DEFAULT_FEASIBILITY) -> dict:
    """Estimate savings per cluster and total."""
    cluster_savings = []
    total_addressable = 0
    total_estimated = 0

    for cluster in clusters:
        cat = cluster["category"]
        # Find best matching category benchmark
        rate = CATEGORY_SAVINGS.get(cat, None)
        if rate is None:
            # Try partial match
            for bench_cat, bench_rate in CATEGORY_SAVINGS.items():
                if bench_cat.lower() in cat.lower() or cat.lower() in bench_cat.lower():
                    rate = bench_rate
                    break
        if rate is None:
            rate = CATEGORY_SAVINGS["General"]

        addressable = cluster["total_spend"]
        estimated = addressable * rate * feasibility
        total_addressable += addressable
        total_estimated += estimated

        cluster_savings.append({
            "cluster_id": cluster["cluster_id"],
            "category": cat,
            "addressable_spend": round(addressable, 2),
            "savings_rate": rate,
            "feasibility_factor": feasibility,
            "estimated_savings": round(estimated, 2),
            "strategy": cluster["strategy"],
        })

    # Quick wins (top clusters by savings density that are low risk)
    quick_wins = [c for c in cluster_savings
                  if c["estimated_savings"] > 0]
    quick_wins.sort(key=lambda x: x["estimated_savings"], reverse=True)

    return {
        "total_addressable_spend": round(total_addressable, 2),
        "total_estimated_savings": round(total_estimated, 2),
        "savings_pct_of_addressable": round(
            total_estimated / total_addressable * 100, 1) if total_addressable > 0 else 0,
        "feasibility_factor": feasibility,
        "cluster_savings": cluster_savings,
        "quick_wins": quick_wins[:5],
    }


def score_and_cluster(cleaned_spend_path: str,
                      pareto_path: str = None,
                      category_summary_path: str = None,
                      output_dir: str = "output",
                      weights_path: str = None,
                      feasibility: float = DEFAULT_FEASIBILITY):
    """Main scoring pipeline."""
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    print(f"Loading cleaned spend data from {cleaned_spend_path}...")
    df = pd.read_csv(cleaned_spend_path)
    print(f"  {len(df)} suppliers loaded")

    # Load custom weights if provided
    dim_weights = None
    if weights_path:
        with open(weights_path) as f:
            dim_weights = json.load(f)
        print(f"  Custom weights loaded from {weights_path}")

    # Compute factor scores
    print("  Computing 20-factor scores...")
    factor_scores = compute_factor_scores(df)

    # Compute composite scores
    print("  Computing composite scores (CPS, SPS, RS)...")
    composite = compute_composite_scores(factor_scores, dim_weights)

    # Merge all scores
    full_scores = factor_scores.merge(
        composite[["supplier", "CPS", "SPS", "RS", "recommendation"]],
        on="supplier")

    # Build clusters
    print("  Building consolidation clusters...")
    clusters = build_clusters(composite, df)

    # Estimate savings
    print("  Estimating savings...")
    savings = estimate_savings(clusters, feasibility)

    # Save outputs
    scores_path = os.path.join(output_dir, "supplier_scores.csv")
    full_scores.to_csv(scores_path, index=False)
    print(f"  Saved: {scores_path}")

    clusters_path = os.path.join(output_dir, "consolidation_clusters.json")
    with open(clusters_path, "w") as f:
        json.dump(clusters, f, indent=2, default=str)
    print(f"  Saved: {clusters_path}")

    savings_path = os.path.join(output_dir, "savings_estimates.json")
    with open(savings_path, "w") as f:
        json.dump(savings, f, indent=2)
    print(f"  Saved: {savings_path}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"SCORING & CLUSTERING SUMMARY")
    print(f"{'='*60}")
    rec_counts = composite["recommendation"].value_counts()
    for rec, count in rec_counts.items():
        print(f"  {rec:15s}: {count:4d} suppliers")
    print(f"\n  Clusters identified: {len(clusters)}")
    print(f"  Addressable spend: ${savings['total_addressable_spend']:,.0f}")
    print(f"  Estimated savings: ${savings['total_estimated_savings']:,.0f} "
          f"({savings['savings_pct_of_addressable']:.1f}%)")
    print(f"{'='*60}")

    return {
        "scores": full_scores,
        "clusters": clusters,
        "savings": savings,
    }


def main():
    parser = argparse.ArgumentParser(description="Supplier Scoring & Clustering")
    parser.add_argument("cleaned_spend", help="Path to cleaned_spend.csv")
    parser.add_argument("--pareto", help="Path to pareto_analysis.json")
    parser.add_argument("--category-summary", help="Path to category_summary.json")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--weights", help="Path to custom weights JSON")
    parser.add_argument("--feasibility", type=float, default=DEFAULT_FEASIBILITY,
                        help=f"Feasibility factor 0-1 (default: {DEFAULT_FEASIBILITY})")
    args = parser.parse_args()

    try:
        score_and_cluster(
            args.cleaned_spend,
            args.pareto,
            args.category_summary,
            args.output_dir,
            args.weights,
            args.feasibility,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
