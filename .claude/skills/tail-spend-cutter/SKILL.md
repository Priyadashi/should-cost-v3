---
name: tail-spend-cutter
description: |
  Analyze enterprise tail spend data to identify supplier consolidation opportunities, score suppliers, and generate a professional 6-tab Excel report with savings estimates and an action plan.

  Use when: (1) User provides spend, procurement, AP, or P-Card data (CSV/Excel) and wants to reduce supplier count or costs, (2) User asks about tail spend analysis, supplier rationalization, vendor consolidation, or spend optimization, (3) User wants Pareto analysis or segmentation of their supplier base, (4) User needs a supplier scoring model, consolidation roadmap, or savings estimate, (5) User asks "how many suppliers do I have", "where can I save on procurement", "analyze my spend data", or similar procurement analytics questions.

  Outputs: Auto-detects columns in messy data, fuzzy-matches duplicate suppliers, classifies Head/Core/Tail via Pareto, scores suppliers across 20 factors, clusters consolidation opportunities, and produces an Excel workbook with executive summary, scores, clusters, action plan, and savings waterfall.
---

# Tail Spend Cutter

## Overview

Autonomous tail spend analysis that matches consulting-grade capabilities. Ingests raw spend data, scores suppliers across 20 factors, clusters consolidation opportunities, and generates a professional Excel deliverable with actionable recommendations.

Typical enterprise results: 5-15% savings on tail spend, 25-40% supplier count reduction.

## Workflow

### Step 1: Gather Input Data

Ask the user for their spend data file (CSV or Excel). Minimum required columns:
- **Supplier name** (vendor, payee, merchant)
- **Spend amount** (amount, total, cost, value)

Optional columns that improve analysis quality:
- Category/commodity code
- Transaction date
- Department/business unit
- PO number
- Payment terms
- Quality/performance scores
- Country/location

If the user doesn't have a file ready, offer to work with a sample or help them identify where to export data from (ERP, AP system, P-Card program).

### Step 2: Analyze & Cleanse Data

Install dependencies if needed:
```bash
pip install -r {{SKILL_DIR}}/requirements.txt
```

Run the analysis script:
```bash
python {{SKILL_DIR}}/scripts/analyze_spend.py "<input_file>" --output-dir "<output_dir>" --tail-threshold 80
```

The script will:
1. Auto-detect column mappings via keyword matching
2. Clean data (drop nulls, normalize amounts, remove credits)
3. Fuzzy-match supplier names (rapidfuzz, threshold 85)
4. Aggregate transactions to supplier level
5. Perform Pareto classification (Head/Core/Tail)

**Present to user:**
- Data quality summary (rows processed, duplicates merged, issues found)
- Pareto breakdown (Head: X suppliers = Y% spend, Core: ..., Tail: ...)
- Ask user to confirm tail threshold (default 80%) or adjust

Review `data_quality_report.json` for ambiguous supplier matches — present any flagged pairs to the user for confirmation.

### Step 3: Score & Cluster Suppliers

Run the scoring script:
```bash
python {{SKILL_DIR}}/scripts/score_suppliers.py "<output_dir>/cleaned_spend.csv" --output-dir "<output_dir>" --feasibility 0.5
```

The script computes:
- **20 factor scores** (1-5 scale) across 5 dimensions
- **Consolidation Priority Score (CPS)** — 1-5, higher = more consolidation potential
- **Savings Potential Score (SPS)** — 0-1
- **Risk Score (RS)** — 0-1
- **Recommendation** — Eliminate / Consolidate / Renegotiate / Retain

Decision matrix: CPS × RS determines the action. See `references/scoring-framework.md` for full details.

**Present to user:**
- Recommendation breakdown (X to eliminate, Y to consolidate, etc.)
- Top 5 consolidation clusters with estimated savings
- Offer to customize dimension weights if user has industry-specific preferences

For weight customization, create a JSON file:
```json
{
  "financial": 0.30,
  "relationship": 0.15,
  "geographic": 0.10,
  "performance": 0.25,
  "market": 0.20
}
```
Pass with `--weights <weights.json>`.

Feasibility factor options:
- `0.3` Conservative (first-time analysis, poor data)
- `0.5` Moderate (default — established procurement, decent data)
- `0.7` Aggressive (strong procurement team, clean data, exec support)

### Step 4: Generate Report

```bash
python {{SKILL_DIR}}/scripts/generate_report.py \
  --scores "<output_dir>/supplier_scores.csv" \
  --pareto "<output_dir>/pareto_analysis.json" \
  --clusters "<output_dir>/consolidation_clusters.json" \
  --savings "<output_dir>/savings_estimates.json" \
  --cleaned "<output_dir>/cleaned_spend.csv" \
  --output "<output_dir>/Tail_Spend_Report.xlsx"
```

**6-tab workbook:**
1. **Executive Summary** — Key metrics, segment breakdown, top opportunities
2. **Pareto Analysis** — Full supplier ranking with cumulative spend curve
3. **Supplier Scores** — 20-factor detail + CPS/SPS/RS composites (conditional formatting)
4. **Consolidation** — Cluster details, strategies, supplier lists
5. **Action Plan** — 4-phase implementation roadmap with owners/status columns
6. **Savings Waterfall** — Phase-by-phase savings realization projection

### Step 5: Present Findings

Summarize for the user:
1. **Scale of opportunity** — Total tail spend, supplier count, addressable spend
2. **Top 3-5 quick wins** — Specific clusters, strategies, estimated savings
3. **Total savings projection** — Conservative to aggressive range
4. **Recommended next steps** — Who to involve, what to do first, timeline

## Reference Files

Detailed reference material is in the `references/` directory:
- `scoring-framework.md` — Full 20-factor model, weights, composite score formulas, decision matrix
- `strategies.md` — 8 consolidation strategies, quick-win criteria, savings estimation
- `benchmarks.md` — Industry savings rates, supplier count benchmarks, category mappings

Load these when:
- User asks about scoring methodology or wants to customize weights
- You need category-specific savings rates
- User asks about implementation strategies or benchmarks
