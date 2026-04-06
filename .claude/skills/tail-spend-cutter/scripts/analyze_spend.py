#!/usr/bin/env python3
"""
Tail Spend Analyzer - Data ingestion, cleansing, and Pareto analysis

Usage:
    python analyze_spend.py <input_file> [--output-dir <dir>] [--tail-threshold <0-100>]

Reads CSV or Excel spend data, auto-detects columns, fuzzy-matches supplier names,
aggregates to supplier level, and performs Pareto classification.

Outputs (to output_dir):
    - cleaned_spend.csv          Deduplicated, normalized supplier-level spend
    - pareto_analysis.json       Head/core/tail classification with breakpoints
    - category_summary.json      Per-category supplier counts and spend totals
    - data_quality_report.json   Missing data, duplicates found, issues flagged
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

# ---------------------------------------------------------------------------
# Column detection keywords (priority-ordered)
# ---------------------------------------------------------------------------
COLUMN_KEYWORDS = {
    "supplier": ["supplier", "vendor", "payee", "merchant", "provider", "company_name",
                  "supplier_name", "vendor_name", "remit_to", "sold_by"],
    "amount": ["amount", "spend", "total", "value", "cost", "price", "payment",
               "invoice_amount", "line_amount", "extended_price", "net_amount"],
    "category": ["category", "commodity", "class", "group", "segment", "type",
                  "spend_category", "commodity_code", "unspsc", "gl_account"],
    "date": ["date", "period", "month", "year", "invoice_date", "po_date",
             "transaction_date", "payment_date", "posting_date"],
    "po_number": ["po", "purchase_order", "order_number", "po_number", "requisition"],
    "department": ["department", "division", "business_unit", "cost_center", "bu",
                   "org", "location", "site", "plant"],
    "description": ["description", "item", "line_description", "product", "service",
                     "material", "sku"],
    "payment_terms": ["terms", "payment_terms", "net_days"],
    "country": ["country", "nation", "region", "geography"],
    "quality_score": ["quality", "rating", "score", "performance"],
}


def detect_columns(df: pd.DataFrame) -> dict:
    """Auto-detect column mapping by matching header keywords."""
    mapping = {}
    used_cols = set()
    col_lower = {c: c.lower().replace(" ", "_").replace("-", "_") for c in df.columns}

    for field, keywords in COLUMN_KEYWORDS.items():
        best_col, best_score = None, 0
        for orig, norm in col_lower.items():
            if orig in used_cols:
                continue
            for kw in keywords:
                if kw == norm:
                    best_col, best_score = orig, 100
                    break
                sc = fuzz.partial_ratio(kw, norm)
                if sc > best_score and sc >= 70:
                    best_col, best_score = orig, sc
            if best_score == 100:
                break
        if best_col:
            mapping[field] = best_col
            used_cols.add(best_col)

    return mapping


def load_data(file_path: str) -> pd.DataFrame:
    """Load CSV or Excel file into a DataFrame."""
    p = Path(file_path)
    ext = p.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(p)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(p)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .csv or .xlsx")


def fuzzy_deduplicate(names: pd.Series, threshold: int = 85,
                      ambiguous_low: int = 85, ambiguous_high: int = 92):
    """
    Fuzzy-match supplier names. Returns (canonical_map, ambiguous_pairs).
    canonical_map: {original_name: canonical_name}
    ambiguous_pairs: [(name_a, name_b, score)]
    """
    unique_names = names.dropna().unique().tolist()
    canonical_map = {}
    ambiguous_pairs = []
    canonical_groups = []  # list of (canonical, [members])

    for name in sorted(unique_names):
        matched = False
        for canon, members in canonical_groups:
            score = fuzz.token_sort_ratio(name, canon)
            if score >= threshold:
                if score < ambiguous_high:
                    ambiguous_pairs.append((name, canon, score))
                canonical_map[name] = canon
                members.append(name)
                matched = True
                break
        if not matched:
            canonical_map[name] = name
            canonical_groups.append((name, [name]))

    return canonical_map, ambiguous_pairs


def pareto_classify(df: pd.DataFrame, spend_col: str,
                    supplier_col: str, tail_threshold: float = 80.0):
    """
    Classify suppliers into Head/Core/Tail by cumulative spend.
    tail_threshold: the cumulative % above which suppliers are 'tail'.
    Head = top suppliers making up 50% of spend.
    Core = 50% to tail_threshold.
    Tail = remaining.
    """
    agg = (df.groupby(supplier_col)[spend_col]
           .sum()
           .sort_values(ascending=False)
           .reset_index())
    agg.columns = ["supplier", "total_spend"]
    total = agg["total_spend"].sum()
    agg["spend_pct"] = agg["total_spend"] / total * 100
    agg["cumulative_pct"] = agg["spend_pct"].cumsum()

    def classify(cum_pct):
        if cum_pct <= 50:
            return "Head"
        elif cum_pct <= tail_threshold:
            return "Core"
        else:
            return "Tail"

    agg["segment"] = agg["cumulative_pct"].apply(classify)
    return agg, total


def build_category_summary(df: pd.DataFrame, supplier_col: str,
                           amount_col: str, category_col: str = None):
    """Build per-category summary of supplier counts and spend."""
    if category_col and category_col in df.columns:
        summary = (df.groupby(category_col)
                   .agg(
                       supplier_count=(supplier_col, "nunique"),
                       total_spend=(amount_col, "sum"),
                       transaction_count=(amount_col, "count"),
                       avg_transaction=(amount_col, "mean"),
                   )
                   .sort_values("total_spend", ascending=False)
                   .reset_index())
        summary.columns = ["category", "supplier_count", "total_spend",
                           "transaction_count", "avg_transaction"]
        return summary.to_dict(orient="records")
    return []


def analyze(input_file: str, output_dir: str = "output",
            tail_threshold: float = 80.0):
    """Main analysis pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    quality_report = {"issues": [], "stats": {}}

    # 1. Load data
    print(f"Loading {input_file}...")
    df = load_data(input_file)
    quality_report["stats"]["raw_rows"] = len(df)
    quality_report["stats"]["raw_columns"] = len(df.columns)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

    # 2. Detect columns
    col_map = detect_columns(df)
    print(f"  Detected columns: {json.dumps(col_map, indent=2)}")

    if "supplier" not in col_map:
        raise ValueError("Could not detect a supplier/vendor name column. "
                         "Please ensure a column contains supplier names.")
    if "amount" not in col_map:
        raise ValueError("Could not detect a spend/amount column. "
                         "Please ensure a column contains monetary amounts.")

    supplier_col = col_map["supplier"]
    amount_col = col_map["amount"]
    category_col = col_map.get("category")
    date_col = col_map.get("date")

    # 3. Data cleansing
    initial_rows = len(df)

    # Drop rows with missing supplier or amount
    df = df.dropna(subset=[supplier_col, amount_col])
    dropped = initial_rows - len(df)
    if dropped:
        quality_report["issues"].append(
            f"Dropped {dropped} rows with missing supplier or amount")

    # Ensure amount is numeric
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
    non_numeric = df[amount_col].isna().sum()
    if non_numeric:
        quality_report["issues"].append(
            f"Dropped {non_numeric} rows with non-numeric amounts")
        df = df.dropna(subset=[amount_col])

    # Remove negative/zero amounts (credits, reversals)
    neg_count = (df[amount_col] <= 0).sum()
    if neg_count:
        quality_report["issues"].append(
            f"Removed {neg_count} rows with zero or negative amounts (likely credits/reversals)")
        df = df[df[amount_col] > 0]

    # Normalize supplier names (strip, title case)
    df[supplier_col] = (df[supplier_col]
                        .astype(str)
                        .str.strip()
                        .str.title())

    # 4. Fuzzy deduplication
    print("  Running fuzzy supplier name matching...")
    canonical_map, ambiguous_pairs = fuzzy_deduplicate(df[supplier_col])
    df["supplier_canonical"] = df[supplier_col].map(canonical_map)

    dedup_count = len(set(canonical_map.keys())) - len(set(canonical_map.values()))
    if dedup_count > 0:
        quality_report["issues"].append(
            f"Merged {dedup_count} likely duplicate supplier names via fuzzy matching")
    if ambiguous_pairs:
        quality_report["issues"].append(
            f"Flagged {len(ambiguous_pairs)} ambiguous supplier name pairs for review")
        quality_report["ambiguous_pairs"] = [
            {"name_a": a, "name_b": b, "similarity": s}
            for a, b, s in ambiguous_pairs
        ]

    quality_report["stats"]["clean_rows"] = len(df)
    quality_report["stats"]["unique_suppliers_raw"] = df[supplier_col].nunique()
    quality_report["stats"]["unique_suppliers_deduped"] = df["supplier_canonical"].nunique()

    # 5. Parse dates if available
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # 6. Aggregate to supplier level
    agg_cols = {amount_col: ["sum", "count", "mean"]}
    if category_col and category_col in df.columns:
        supplier_agg = (df.groupby("supplier_canonical")
                        .agg(
                            total_spend=(amount_col, "sum"),
                            transaction_count=(amount_col, "count"),
                            avg_transaction=(amount_col, "mean"),
                            categories=(category_col, "nunique"),
                            primary_category=(category_col, lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else "Unknown"),
                        )
                        .sort_values("total_spend", ascending=False)
                        .reset_index())
    else:
        supplier_agg = (df.groupby("supplier_canonical")
                        .agg(
                            total_spend=(amount_col, "sum"),
                            transaction_count=(amount_col, "count"),
                            avg_transaction=(amount_col, "mean"),
                        )
                        .sort_values("total_spend", ascending=False)
                        .reset_index())

    supplier_agg.rename(columns={"supplier_canonical": "supplier"}, inplace=True)

    # 7. Pareto classification
    print(f"  Running Pareto analysis (tail threshold: {tail_threshold}%)...")
    pareto_df, total_spend = pareto_classify(
        df, amount_col, "supplier_canonical", tail_threshold)

    # Merge segment back into supplier_agg
    supplier_agg = supplier_agg.merge(
        pareto_df[["supplier", "spend_pct", "cumulative_pct", "segment"]],
        on="supplier", how="left")

    # 8. Build summaries
    segment_summary = {}
    for seg in ["Head", "Core", "Tail"]:
        seg_data = supplier_agg[supplier_agg["segment"] == seg]
        segment_summary[seg] = {
            "supplier_count": len(seg_data),
            "total_spend": float(seg_data["total_spend"].sum()),
            "spend_pct": float(seg_data["spend_pct"].sum()),
            "avg_spend_per_supplier": float(seg_data["total_spend"].mean()) if len(seg_data) > 0 else 0,
        }

    pareto_result = {
        "total_spend": float(total_spend),
        "tail_threshold_pct": tail_threshold,
        "segments": segment_summary,
        "supplier_count": len(supplier_agg),
    }

    category_summary = build_category_summary(
        df, "supplier_canonical", amount_col, category_col)

    # 9. Save outputs
    cleaned_path = os.path.join(output_dir, "cleaned_spend.csv")
    supplier_agg.to_csv(cleaned_path, index=False)
    print(f"  Saved: {cleaned_path}")

    pareto_path = os.path.join(output_dir, "pareto_analysis.json")
    with open(pareto_path, "w") as f:
        json.dump(pareto_result, f, indent=2)
    print(f"  Saved: {pareto_path}")

    cat_path = os.path.join(output_dir, "category_summary.json")
    with open(cat_path, "w") as f:
        json.dump(category_summary, f, indent=2, default=str)
    print(f"  Saved: {cat_path}")

    quality_path = os.path.join(output_dir, "data_quality_report.json")
    with open(quality_path, "w") as f:
        json.dump(quality_report, f, indent=2)
    print(f"  Saved: {quality_path}")

    # 10. Print summary
    print(f"\n{'='*60}")
    print(f"TAIL SPEND ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Total Spend: ${total_spend:,.0f}")
    print(f"Total Suppliers (after dedup): {len(supplier_agg)}")
    print(f"")
    for seg in ["Head", "Core", "Tail"]:
        s = segment_summary[seg]
        print(f"  {seg:6s}: {s['supplier_count']:5d} suppliers "
              f"({s['supplier_count']/len(supplier_agg)*100:5.1f}%)  |  "
              f"${s['total_spend']:>12,.0f}  ({s['spend_pct']:5.1f}%)")
    print(f"{'='*60}")

    return {
        "cleaned_spend": cleaned_path,
        "pareto_analysis": pareto_result,
        "category_summary": category_summary,
        "quality_report": quality_report,
        "supplier_agg": supplier_agg,
    }


def main():
    parser = argparse.ArgumentParser(description="Tail Spend Analyzer")
    parser.add_argument("input_file", help="Path to CSV or Excel spend data")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory (default: output)")
    parser.add_argument("--tail-threshold", type=float, default=80.0,
                        help="Cumulative spend %% above which suppliers are 'tail' (default: 80)")
    args = parser.parse_args()

    try:
        analyze(args.input_file, args.output_dir, args.tail_threshold)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
