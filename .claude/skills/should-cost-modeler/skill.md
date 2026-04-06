---
name: should-cost-modeler
description: >
  Build should-cost models for MANUFACTURED physical components and parts — items with a bill of materials (BOM),
  raw materials (metals, plastics, composites), and manufacturing processes (CNC machining, stamping, injection molding,
  casting, welding, assembly). Use when the user asks about should-costing, cleansheet analysis, cost buildup,
  make-vs-buy analysis, or wants to estimate what a physical part should cost based on material weight, cycle times,
  machine rates, labor, overhead, and supplier profit margin. Also trigger on: "BOM cost", "material cost breakdown",
  "machining cost estimate", "supplier price challenge" for a manufactured part, "negotiation brief" for a component,
  "cost transparency" on a physical product, or comparing a supplier's quoted price against a fact-based cost model.

  DO NOT use this skill for: service spend (staffing, consulting, facilities management, cleaning, catering),
  IT hardware resale or software licenses, office supplies, travel and entertainment, marketing services,
  telecom, or any non-manufactured procurement category. For those categories, use the tail-spend-cutter skill
  for portfolio-level consolidation analysis, or build a custom bill-rate / markup analysis instead.
---

# Should-Cost Analysis Skill

## Purpose

Produce procurement-grade should-cost analyses for manufactured components. Output is a complete negotiation package: cost breakdown with traceable assumptions, gap analysis with diagnostic questions, sensitivity/scenario analysis, contract clause recommendations, and a supplier data request form.

Follows McKinsey Cleansheet, BCG technical lever, Kearney Purchasing Chessboard, and Total Cost of Ownership frameworks.

## Core Principle: Transparency Over Precision

85% accurate with visible assumptions beats 95% accurate but opaque. Every number must trace to its source. The buyer must be able to say: "Here is exactly where this number comes from. If you disagree, provide your data — we will update the model."

## Architecture

1. **Foundation** (this file): orchestration logic, decision tree, output specs
2. **Calculation engine** (`scripts/should_cost_engine.py`): Python template — read, fill in variables, execute
3. **Reference data** (`references/`): labor rates, overhead benchmarks, negotiation templates, regional overlays
4. **Commodity modules** (`references/`): plug-in files per commodity type (CNC, sheet metal, etc.)

---

## Input Contract

### Tier 1: Required (cannot proceed without these)
- **Product/component description**: what is it, key dimensions/weight if known
- **Current price or supplier quote**: per unit
- **Annual volume**: units per year
- **Primary material(s)**: type and grade (e.g., "6061-T6 aluminum", "AISI 304 stainless")

### Tier 2: Enrichment (agent looks up or infers)
- Material spot prices → web search for current commodity prices
- Regional labor rates → `references/labor_rates.md`
- Machine hourly rates → commodity module
- Overhead/SGA benchmarks → `references/overhead_benchmarks.md`
- Logistics costs → estimate from origin-destination if known

### Tier 3: Contextual (ask only if >10% impact on cost)
- Supplier cost breakdown (enables does-cost vs. should-cost gap)
- Supplier country/location (enables precise labor rate and TCO)
- Manufacturing process details (machines, tolerances, finish specs)
- Drawings or CAD data (enables weight and process inference)
- Number of qualified alternative suppliers (enables leverage assessment)

### How to gather inputs

Ask all missing Tier 1 items in a single question — do not ask one at a time. Look up Tier 2 autonomously. For Tier 3, use reasonable midpoint assumptions and tag with medium confidence if uncertain.

---

## The Eight-Step Pipeline

Every step below ends with a **GATE** — a checklist of conditions that must be true before moving to the next step. If a gate condition is not met, either fix it or document why in the output. Do not silently skip gate items.

### Step 0: Pre-flight — load reference files

Before any analysis, load the files you will need. This prevents the temptation to guess values that are in the reference data.

**Required reads:**
1. Read `scripts/should_cost_engine.py` — understand the template variables you need to fill
2. Read the appropriate commodity module (e.g., `references/commodity_cnc_machined.md`)
3. Read `references/labor_rates.md`
4. Read `references/overhead_benchmarks.md`
5. If supplier country has a regional overlay → read it (e.g., `references/region_india.md`)
6. Read `references/negotiation_templates.md` (needed for Step 6)

> **GATE:** All 5-6 files above are loaded. If a file does not exist, note it and proceed with reduced confidence on the affected inputs.

### Step 1: Parse and classify

Determine:
- **Commodity type**: which module to load (CNC, sheet metal, injection molding, etc.)
- **Analysis depth**: full cleansheet (detailed BOM) → parametric estimation (description + weight) → benchmarking mode ("we pay $X")
- **Single vs. portfolio**: one item → deep analysis; spreadsheet → portfolio screening (flag outliers, deep-dive top 10-20)

If uncovered by an existing commodity module, offer best-effort with closest module, noting reduced confidence.

> **GATE:** Commodity module identified and loaded in Step 0. Analysis depth determined.

### Step 2: Decompose the BOM and fetch live pricing

For each material, do these sub-steps **in order**:

**2a. Identify material parameters** from the commodity module:
- Type, grade, finished mass, utilization rate (from commodity module norms)
- Calculate buy weight = finished mass / utilization rate

**2b. Fetch live pricing — this is mandatory, not optional.**
- Perform a web search. Use specific queries like:
  - `"LME aluminum price today"` (for base metal)
  - `"6061-T6 plate price [country] per kg [year]"` (for alloy/form-specific pricing)
  - `"[supplier name] aluminum price"` (if supplier is known)
- If the web search returns usable pricing → use it and tag confidence **HIGH**.
- If the web search fails or returns nothing usable → fall back to reference files. **Tag confidence LOW** — not MEDIUM. A static reference price without live validation is LOW by definition.

**2c. Apply regional adjustments** from the regional overlay (import duties, local supplier premiums).

**2d. Calculate scrap recovery credit:**
- Scrap weight = buy weight − finished mass
- Scrap credit = scrap weight × price/kg × recovery % (from commodity module)

**2e. Flag utilization anomalies.** If the supplier's quoted material cost implies utilization below the commodity module's range for this part type, flag it — this is a common hidden margin source.

> **GATE:** For every material line item, verify:
> - [ ] A web search was attempted (record the query used in the `price_source` field)
> - [ ] Confidence is HIGH (live price used) or LOW (fallback to static reference). MEDIUM is not valid for material pricing unless the user provided the price directly.
> - [ ] Scrap recovery credit is calculated (not zero, unless the commodity module says recovery is negligible for this material)
> - [ ] `price_source` field contains the specific source, not a generic description

### Step 3: Infer manufacturing process and estimate cycle times

From the commodity module loaded in Step 0:
1. Determine process routing using the routing selection logic
2. For each operation, estimate cycle time using the module's estimation method (e.g., MRV-based for milling)
3. Select machine rates from the commodity module's rate table
4. Apply regional multiplier from `references/labor_rates.md` (the file you already loaded)
5. Select labor rates by skill tier from `references/labor_rates.md`, using the regional overlay for country-specific granularity

When selecting machine rates (low/mid/high):
- **Low**: high-volume, newer equipment, developing economy
- **Mid**: typical job shop or production shop in developed economy (default)
- **High**: specialty/aerospace, older equipment, low utilization

> **GATE:** For every process step, verify:
> - [ ] Machine rate source is cited (which table row, which regional multiplier)
> - [ ] Labor rate source is cited (which country, which skill tier, which file)
> - [ ] Cycle time estimation method is documented (e.g., "MRV = X cm³, roughing MRR = Y cm³/min")
> - [ ] Setup time is included and will be amortized over batch size

### Step 4: Stack up total cost using the calculation engine

1. Read `scripts/should_cost_engine.py` (already loaded in Step 0)
2. Read `references/overhead_benchmarks.md` (already loaded in Step 0) — select overhead %, SGA %, and profit % with documented reasoning
3. Copy the engine template into a new Python file
4. Fill in ALL variables from Steps 1-3
5. Execute the script

Do not compute cost figures through prose reasoning or mental math. The engine exists because manual arithmetic introduces errors and loses traceability. If you catch yourself doing math in text, stop and put it in the script instead.

> **GATE:**
> - [ ] The Python script was written to a file and executed (not computed in prose)
> - [ ] All engine template variables are filled in (no `___` placeholders remain)
> - [ ] Overhead, SGA, and profit percentages each cite their source from `references/overhead_benchmarks.md` or the regional overlay
> - [ ] The engine output JSON was captured and will be used for Steps 5-7

### Step 5: Score and prioritize

From the engine output:
- Extract should-cost, gap, gap %, and annual opportunity
- In portfolio mode, rank items by annual opportunity value

> **GATE:** Gap and annual opportunity values come from the engine JSON, not from separate calculation.

### Step 6: Generate the negotiation package

Produce all five deliverables below. For diagnostic questions, open `references/negotiation_templates.md` and the commodity module (both loaded in Step 0) and pull specific questions — do not generate generic questions from memory.

> **GATE:**
> - [ ] All 5 deliverables are present in the output
> - [ ] Diagnostic questions in Deliverable 2 cite their source file
> - [ ] Contract clause templates in Deliverable 4 are adapted from `references/negotiation_templates.md`
> - [ ] Supplier data request in Deliverable 5 follows `references/supplier_data_request_template.md`

### Step 7: Sensitivity, scenario, and volume-price analysis

The engine automatically produces sensitivity (±20% on top drivers) and volume-price curves. Present these in the report. Re-run with modified variables for user-requested scenarios.

### Step 8: Final confidence audit

Before presenting the output, review every line item's confidence tag against these rules:

| Confidence | Criteria | Common mistakes to catch |
|---|---|---|
| **HIGH** | User-provided, from supplier quote, or from **live** authoritative source (web search with date) | Do not tag HIGH if the price came from a static reference file |
| **MEDIUM** | From reference table with confirmed regional/industry match, or inferred from well-characterized geometry | Do not tag MEDIUM for material prices without live validation — that's LOW |
| **LOW** | Inferred from limited info, proxy region, no drawings, or static benchmark when live data unavailable | If you didn't attempt a web search, the price is LOW not MEDIUM |

The engine flags if >70% of items are MEDIUM — if this warning fires, re-examine your tags before presenting. At least one item should be HIGH (user-provided inputs like quoted price, volume, or material grade are HIGH by default). If zero items are HIGH, something is wrong with your tagging.

> **GATE:**
> - [ ] At least one HIGH-confidence item exists
> - [ ] No material price is tagged MEDIUM (must be HIGH if live-fetched, or LOW if static reference)
> - [ ] All LOW-confidence items are called out in the Confidence Summary section of Deliverable 1

---

## Output Specifications

### Deliverable 1: Cost Breakdown Report

Structured waterfall table: category, value, assumption detail, source, confidence tag (HIGH/MEDIUM/LOW). End with total should-cost, quoted price, gap, gap %, annual opportunity. Include the **Confidence Summary** — call out which LOW-confidence items need validation.

### Deliverable 2: Gap Analysis with Diagnostic Questions

For each significant gap: state your assumption vs. supplier's, hypothesize root cause, provide 3-5 diagnostic questions **pulled from** the commodity module and `references/negotiation_templates.md` (cite the source).

Segment into: **Recover now** (price/margin) → **Short-term 0-6mo** (process improvements) → **Medium-term 6-18mo** (capital/sourcing changes).

Include: "If you disagree with any assumptions, we welcome your data. Provide supporting evidence and we will update our model."

### Deliverable 3: Sensitivity, Scenario, and Volume-Price Analysis

Tornado-style ranking of sensitivity results. Volume-price table from engine output — highlight volume leverage for negotiation. Comparison table for any user-requested scenarios.

### Deliverable 4: Contract Clause Recommendations

Recommend: commodity index linkage (index, formula, thresholds), annual productivity target, milestone-based reductions, re-opener triggers. Adapt templates from `references/negotiation_templates.md`.

### Deliverable 5: Supplier Data Request Form

Generate using the template in `references/supplier_data_request_template.md`. Tailor the data points to the specific analysis. Pre-fill the "Our Assumption" column with model values so the supplier can respond to specific numbers.

---

## Commodity Module Routing

| Commodity type | Module file |
|---|---|
| CNC machined parts (milling, turning, grinding) | `references/commodity_cnc_machined.md` |
| Sheet metal (stamping, bending, laser cutting) | *Future: references/commodity_sheet_metal.md* |
| Plastic injection molding | *Future: references/commodity_injection_molding.md* |
| Casting (sand, die, investment) | *Future: references/commodity_casting.md* |
| Electronic PCB assembly | *Future: references/commodity_electronics.md* |

### Regional Overlay Files

| Country | Overlay file |
|---|---|
| India | `references/region_india.md` |
| *Other countries* | *Future: add as needed* |

---

## Important Guardrails

1. **Never send output directly to a supplier.** All output is a draft for human review.
2. **Use "reasonable best-in-class" assumptions**, not theoretical minimum. Do not cherry-pick structural costs from different regions.
3. **Flag all LOW-confidence assumptions prominently.**
4. **Arithmetic must go through the code.** Always use `scripts/should_cost_engine.py`.
5. **Cite sources.** Every rate, price, or benchmark must cite its origin file and the specific table/row used.
