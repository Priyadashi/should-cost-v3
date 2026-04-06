# Commodity Module: CNC Machined Parts

## Table of Contents
1. [Scope](#scope)
2. [Process Routing Template](#1-process-routing-template) — standard routing, selection logic
3. [Machine Rate Table](#2-machine-rate-table) — cutting machines, secondary ops, surface treatment
4. [Cycle Time Estimation Logic](#3-cycle-time-estimation-logic) — MRR-based milling, turning, setup times
5. [Material Utilization Norms](#4-material-utilization-norms) — utilization by part type, scrap recovery
6. [CNC-Specific Diagnostic Questions](#5-cnc-specific-diagnostic-questions-for-supplier-negotiation) — process, material, setup, quality

## Scope
This module covers parts manufactured primarily through CNC machining processes: milling (3-axis, 4-axis, 5-axis), turning (CNC lathe), grinding, and combinations thereof. It includes parts made from bar stock, plate, billet, or near-net-shape forgings/castings that require significant machining.

## 1. Process Routing Template

The standard process routing for a CNC machined part follows this sequence. Not every part requires every step — select the steps that apply based on the part description.

| Step | Operation | When required | Typical machine |
|---|---|---|---|
| 1 | Raw material procurement | Always | N/A (material cost only) |
| 2 | Saw cutting / shearing to blank | When starting from bar/plate stock | Bandsaw / plate shear |
| 3 | First machining operation (roughing) | Always | CNC mill or CNC lathe |
| 4 | Second machining operation (finishing) | When tight tolerances or multiple faces | CNC mill (potentially 5-axis) |
| 5 | Additional operations (holes, threads, slots) | When features require separate setup | CNC mill, drill press, or tap |
| 6 | Grinding | When surface finish or tolerance requires it | Surface or cylindrical grinder |
| 7 | Deburring / edge finishing | Almost always | Manual or tumble deburr |
| 8 | Surface treatment | When specified (anodize, plate, paint, passivate) | Outsourced process typically |
| 9 | Inspection | Always (level varies) | CMM, manual gauging, or visual |
| 10 | Cleaning and packing | Always | Manual or automated wash + pack |

### Routing Selection Logic

- **Simple prismatic part (bracket, plate, spacer)**: Steps 1 → 2 → 3 → 7 → 9 → 10. One machining operation, typically 3-axis VMC.
- **Moderate complexity (housing, manifold, fixture)**: Steps 1 → 2 → 3 → 4 → 5 → 7 → 9 → 10. Two or more machining operations, possibly requiring 4/5-axis.
- **Rotational part (shaft, bushing, pin)**: Steps 1 → 2 → 3 (lathe) → 5 (secondary milling if flats/features) → 6 (if ground diameter required) → 7 → 9 → 10.
- **High-precision part (aerospace, medical)**: Add step 6 (grinding) and extended step 9 (CMM inspection). Surface treatment (step 8) is common.

## 2. Machine Rate Table

All rates in USD per hour. Rates include machine depreciation, energy, maintenance, tooling amortization, and floor space allocation. They EXCLUDE operator labor (added separately using the labor rates reference file).

### Cutting / Shaping Machines

| Machine type | Size / capacity | Rate ($/hr) low | Rate ($/hr) mid | Rate ($/hr) high | Typical OEE |
|---|---|---|---|---|---|
| Bandsaw | Standard | $10 | $15 | $20 | 85-90% |
| Manual lathe | Standard | $20 | $30 | $40 | 75-85% |
| CNC lathe — small | <200mm swing | $35 | $50 | $65 | 82-90% |
| CNC lathe — medium | 200-400mm swing | $50 | $65 | $85 | 80-88% |
| CNC lathe — large | >400mm swing | $70 | $90 | $120 | 78-85% |
| CNC lathe — multi-axis (mill-turn) | Combined turning + milling | $90 | $120 | $160 | 75-85% |
| 3-axis VMC — small | <600mm X-travel | $40 | $55 | $70 | 82-90% |
| 3-axis VMC — medium | 600-1000mm X-travel | $55 | $72 | $90 | 80-88% |
| 3-axis VMC — large | >1000mm X-travel | $75 | $95 | $120 | 78-85% |
| 4-axis VMC | With rotary table | $70 | $90 | $115 | 78-86% |
| 5-axis VMC | Simultaneous 5-axis | $90 | $120 | $160 | 75-85% |
| Surface grinder | Standard | $40 | $55 | $75 | 78-85% |
| Cylindrical grinder | Standard | $50 | $65 | $85 | 78-85% |
| CNC cylindrical grinder | With CNC dressing | $65 | $85 | $110 | 76-84% |

### Secondary / Finishing Operations

| Operation | Method | Rate ($/hr) or cost per unit |
|---|---|---|
| Deburring — manual | Hand tools | Use labor rate only (no machine cost) |
| Deburring — tumble/vibratory | Batch process | $15-25/hr machine + labor; typically 0.5-2 min amortized per part |
| Cleaning — solvent/aqueous wash | Batch or inline | $0.20-1.00 per part |
| Inspection — manual gauging | Calipers, micrometers | Use labor rate only; 1-5 min per part depending on feature count |
| Inspection — CMM | Coordinate measuring machine | $50-80/hr; 3-15 min per part depending on complexity |
| Packing | Manual | Use labor rate; 0.5-2 min per part |

### Surface Treatment (typically outsourced)

| Treatment | Typical cost range per part | Notes |
|---|---|---|
| Anodize (Type II, clear) | $1.50-5.00 | Depends on part size and batch |
| Anodize (Type III, hard) | $3.00-10.00 | Thicker coating, more expensive |
| Zinc plating | $0.50-3.00 | Common for steel parts |
| Nickel plating | $2.00-8.00 | Higher quality/cost |
| Passivation (stainless) | $0.50-2.00 | Chemical treatment |
| Powder coating | $1.00-5.00 | Depends on part size |
| Black oxide | $0.30-1.50 | Low-cost finish for steel |

### Machine Rate Selection Logic

When choosing which rate (low/mid/high) to use:
- **Low rate**: high-volume production shop, newer equipment, high utilization, developing economy
- **Mid rate**: typical job shop or production shop in developed economy (use this as default)
- **High rate**: specialty/aerospace shop, older equipment, low utilization, high-cost region, or small lot requirements that limit machine allocation

Apply regional adjustments from the labor rates reference file for machine rates too — a CNC mill in India costs roughly 50-70% of the same machine in the US due to lower depreciation basis, energy, and facility costs.

## 3. Cycle Time Estimation Logic

Cycle time is the most judgment-intensive assumption. Use the following estimation approach.

### For Milling Operations

The primary driver of milling cycle time is **material removal volume (MRV)** — the difference between the billet/blank volume and the finished part volume.

**Step 1: Estimate material removal volume**
- If you know billet and finished dimensions: MRV = billet volume − finished volume (in cm³)
- If you only know finished dimensions: estimate billet as the smallest rectangular prism that contains the part, then MRV = billet volume − (estimated finished volume at ~60-80% of billet)

**Step 2: Apply material removal rate (MRR)**

| Material type | Roughing MRR (cm³/min) | Finishing MRR (cm³/min) |
|---|---|---|
| Aluminum alloys (6061, 7075) | 50-150 | 15-40 |
| Mild steel / carbon steel | 15-40 | 5-15 |
| Stainless steel (304, 316) | 8-25 | 3-10 |
| Tool steel / alloy steel | 5-15 | 2-8 |
| Titanium alloys | 3-10 | 1-4 |
| Brass / bronze | 40-100 | 12-30 |
| Plastics (Delrin, PEEK, nylon) | 80-200 | 25-60 |

**Step 3: Calculate base machining time**
```python
# Cycle time estimation for milling
def estimate_milling_time(material_removal_cm3, material_type_roughing_mrr, material_type_finishing_mrr, roughing_fraction=0.7):
    """
    Estimate milling cycle time from material removal volume.
    roughing_fraction: proportion of MRV removed in roughing (default 70%)
    """
    roughing_volume = material_removal_cm3 * roughing_fraction
    finishing_volume = material_removal_cm3 * (1 - roughing_fraction)

    roughing_time_min = roughing_volume / material_type_roughing_mrr
    finishing_time_min = finishing_volume / material_type_finishing_mrr

    base_time = roughing_time_min + finishing_time_min
    return base_time
```

**Step 4: Add time multipliers**

| Factor | Multiplier | When to apply |
|---|---|---|
| Tight tolerances (±0.025mm / ±0.001") | 1.15-1.30× | Precision features requiring slow feeds or spring passes |
| Complex geometry / 5-axis required | 1.20-1.40× | Undercuts, compound angles, sculptured surfaces |
| Multiple setups required | Add 5-15 min per additional setup | Each time the part is re-fixtured |
| Tool changes | Add 0.5-1 min per tool change | Typical 3-8 tools per operation |
| Many features (>10 holes, pockets, etc.) | 1.10-1.20× | Accumulated positioning and tool change time |
| Thin walls (<2mm) | 1.15-1.30× | Reduced feed to prevent deflection |

### For Turning Operations

| Operation | Estimation basis |
|---|---|
| External turning (roughing) | Length × depth of cut / feed rate. Typical: 0.5-3 min for small parts, 2-10 min for medium |
| External turning (finishing) | 30-50% of roughing time at reduced feed |
| Face machining | 0.5-2 min per face depending on diameter |
| Boring | Similar to external turning for the bore length |
| Threading | 0.5-2 min per thread depending on length |
| Parting off | 0.3-1 min |

### Setup Time Estimates

| Setup type | Time (minutes) | Notes |
|---|---|---|
| Simple vise setup (3-axis) | 10-20 | Part in vise, touch off, load program |
| Fixture setup (3-axis, dedicated fixture) | 15-30 | Fixture alignment, clamping, tool verification |
| 4/5-axis setup | 20-40 | More complex alignment and probing |
| CNC lathe (chuck work) | 10-20 | Chuck jaws, tool offsets |
| CNC lathe (between centers) | 15-25 | Center alignment, drive dog |
| First article / new program | Add 30-60 min | First time a program runs on a machine |

Setup time is amortized across the batch: setup cost per part = (setup time × machine rate) / batch size. This is where batch size has a dramatic cost impact — a 10-piece batch carries 10× the setup cost per part vs. a 100-piece batch.

## 4. Material Utilization Norms

Material utilization = finished part weight / raw material weight purchased. The remainder is scrap (chips, offcuts, remnants). Some scrap has recovery value.

| Process / part type | Typical utilization | Notes |
|---|---|---|
| Simple prismatic (bar stock) | 50-70% | Rectangular blanks close to finished size |
| Complex prismatic (plate stock) | 30-55% | Significant pocket milling, internal features |
| Rotational (bar stock on lathe) | 55-75% | Turning is relatively efficient for cylindrical parts |
| From near-net-shape forging | 70-85% | Forging gets close; machining is mostly finishing |
| From near-net-shape casting | 75-90% | Casting gets very close; machining just critical surfaces |
| Aerospace structural (from billet) | 10-30% | "Hog-out" parts — extremely low utilization, very high material cost impact |

### Scrap Recovery Value

| Material | Typical scrap recovery (% of purchased price) |
|---|---|
| Aluminum | 25-40% (machining chips have good value) |
| Steel (mild/carbon) | 10-20% |
| Stainless steel | 20-35% |
| Titanium | 30-50% (high scrap value) |
| Brass/copper | 35-55% (high scrap value) |
| Plastics | 0-5% (usually landfill cost, not recovery) |

To include scrap credit in the model: Net material cost = gross material cost − (scrap weight × scrap recovery price per kg). For most analyses, ignoring scrap recovery is a conservative assumption that slightly overstates should-cost — acceptable because it gives the supplier less room to argue.

## 5. CNC-Specific Diagnostic Questions for Supplier Negotiation

Use these in addition to the generic questions in `references/negotiation_templates.md`.

### Process Efficiency
- How many operations and setups does this part require? Have you explored combining operations (e.g., mill-turn instead of separate lathe + mill)?
- What CNC machine model are you running this part on? Is it the right-sized machine for the job, or is it running on an oversized machine?
- What are your programmed feed rates and spindle speeds? Are they at or near the tooling manufacturer's recommendations for this material?
- What is your tool life assumption? When was it last validated? Are you using the most current insert grades and coatings?
- Are you running this part attended or unattended? If attended, what is the operator doing during the machine cycle?
- What is your OEE on the machines running this part? What are the main sources of downtime?

### Material Efficiency
- What form and size of raw material are you starting from (bar, plate, billet)? Have you considered a near-net-shape blank (forging or casting) to reduce machining?
- What is your material utilization rate? Are you nesting parts on the raw material to reduce waste?
- Are you buying material at spot or contract pricing? When was the last time you renegotiated your material supply agreement?
- Is there a scrap recovery program? What scrap value are you receiving and is it reflected in the price?

### Setup and Batch Optimization
- What batch sizes are you running? Is the batch size driven by our order pattern or by your production scheduling?
- What is the setup time for this part? Has it been reduced since the part was first introduced?
- Have you invested in quick-change tooling or modular fixturing that could reduce setup time?
- Could order consolidation (combining multiple releases into fewer, larger batches) meaningfully reduce the per-unit cost?

### Quality and Rework
- What is your first-pass yield rate on this part? What are the primary defect modes?
- Are there tolerance specifications that are difficult to hold consistently? Could any tolerances be relaxed without affecting function?
- What percentage of parts require CMM inspection vs. process-controlled / SPC-monitored operations?
