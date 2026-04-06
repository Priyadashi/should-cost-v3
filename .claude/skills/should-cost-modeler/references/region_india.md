# Regional Reference: India

## Table of Contents
1. [Currency & Exchange](#currency--exchange)
2. [GST (Goods & Services Tax)](#gst-goods--services-tax) — rates by category, how to apply
3. [Labor Rates (India-Specific)](#labor-rates-india-specific-detail) — city-tier rates, statutory benefits, productivity
4. [Machine Rate Adjustments](#machine-rate-adjustments) — cost drivers, multipliers by supplier profile
5. [Overhead Benchmarks (India)](#overhead-benchmarks-india) — factory type rates, India-specific components
6. [Common Indian Aluminum Suppliers & Pricing](#common-indian-aluminum-suppliers--pricing) — Hindalco, Vedanta, import pricing
7. [Surface Treatment Costs (India)](#surface-treatment-costs-india)
8. [Logistics (Domestic India)](#logistics-domestic-india)
9. [Financial Benchmarks (Listed Manufacturers)](#financial-benchmarks-publicly-listed-indian-manufacturers) — Bharat Forge, Sansera, Endurance, etc.

## Purpose
India-specific adjustments for should-cost models. Load this file when the supplier is located in India or when comparing Indian sourcing scenarios.

## Currency & Exchange
- Currency: Indian Rupee (INR)
- When modeling in INR, convert all USD reference rates using the prevailing exchange rate. As of Q1 2026, approximately 1 USD = 83-87 INR. Always state the rate used.
- For contract pricing, recommend specifying whether prices are INR or USD, and include forex re-opener triggers if cross-currency.

## GST (Goods & Services Tax)

GST is a critical factor in Indian manufacturing cost structures. Ensure the model is clear on pre-GST vs. post-GST pricing.

| Category | GST Rate | Notes |
|---|---|---|
| Raw materials (aluminum, steel, etc.) | 18% | Input tax credit (ITC) available to manufacturer |
| Job work / machining services | 12% (if registered) or 18% | 12% for job work on goods; 18% for manufacturing services |
| Finished manufactured goods (general) | 18% | Most engineering components |
| Surface treatment (anodizing, plating) | 18% | Outsourced process — ITC claimable |
| Packaging materials | 12-18% | Depends on material type |
| Freight (road transport by GTA) | 5% (no ITC) or 12% (with ITC) | Goods Transport Agency rates |

### How to Apply GST
- **If modeling ex-works cost for domestic sale**: Add GST at 18% on top of the ex-works price. Note that the buyer can claim ITC if registered.
- **If modeling for export**: Exports are zero-rated (0% GST). The supplier claims refund of input GST. However, working capital cost of GST float (refund delays of 3-6 months) should be considered — typically add 0.5-1.0% to cost.
- **If modeling for cost comparison**: Compare pre-GST (ex-works) costs across suppliers. GST is a pass-through for registered businesses.
- **Default**: Model all costs **exclusive of GST** and note this in the report. Add a separate line for GST if the buyer needs landed cost inclusive of tax.

## Labor Rates (India-Specific Detail)

Supplement the main `labor_rates.md` with tier-city granularity.

### By City Tier

| City tier | Examples | Unskilled (INR/hr) | Semi-skilled | Skilled (CNC) | Technician | Engineer |
|---|---|---|---|---|---|---|
| Tier 1 (metro) | Mumbai, Bangalore, Chennai, Pune, Delhi NCR | 200-350 | 320-510 | 470-750 | 700-1200 | 900-1700 |
| Tier 2 (industrial) | Coimbatore, Rajkot, Ahmedabad, Ludhiana, Jamshedpur | 150-250 | 250-420 | 380-600 | 550-950 | 700-1350 |
| Tier 3 (emerging) | Hubli, Kolhapur, Hosur, Haridwar, Pithampur | 120-200 | 200-340 | 300-500 | 450-750 | 550-1050 |

### Key India Labor Factors
- **Statutory benefits load**: ESI (Employee State Insurance) + PF (Provident Fund) + bonus + gratuity add 30-45% on top of base wages for organized sector. All rates above are **fully loaded**.
- **Contract labor**: Many Indian shops use contract workers for unskilled/semi-skilled roles at 20-30% lower fully-loaded cost than permanent employees, but with higher turnover and training cost.
- **Shift premiums**: Night shift typically adds 10-15% to base wage. Many Indian CNC shops run 2 shifts; 3 shifts less common except in automotive tier-1 suppliers.
- **Productivity factor**: Use 0.65-0.80 from the main labor reference. Within India:
  - Automotive tier-1 suppliers (Bharat Forge, Sansera, Endurance): 0.80-0.90
  - Established job shops (ISO-certified, Pune/Bangalore belt): 0.72-0.82
  - Small/medium unorganized shops: 0.60-0.72

## Machine Rate Adjustments

Indian machine rates are typically 50-70% of US equivalents. Key drivers:

| Factor | Impact on rate | Notes |
|---|---|---|
| Equipment acquisition cost | -15 to -30% | Indian/Taiwanese machines cost less; Japanese/German imports are similar to US |
| Facility cost | -40 to -60% | Rent/depreciation significantly lower |
| Energy cost | -10 to -25% | INR 8-12/kWh industrial vs. $0.08-0.15/kWh in US; but reliability issues add generator cost |
| Maintenance labor | -40 to -60% | Technicians are much cheaper |
| Tooling consumables | -5 to -15% | Similar global pricing, slight local sourcing advantage |

### Machine Rate Multipliers (vs. US mid-rate)

| Supplier profile | Multiplier | When to use |
|---|---|---|
| Large Indian tier-1 (Bharat Forge, Godrej, L&T) with imported machines | 0.65-0.75× | High-quality, export-grade work |
| Mid-size established shop (ISO 9001, Pune/Coimbatore belt) | 0.55-0.65× | Standard precision work |
| Small job shop with Indian/Taiwanese equipment | 0.40-0.55× | Lower precision, higher variability |
| Specialty/aerospace-certified (AS9100, NADCAP) | 0.70-0.85× | Premium for certification overhead |

## Overhead Benchmarks (India)

Indian factory overhead is lower than US due to facilities, energy, and indirect labor costs, but regulatory compliance (pollution control, factory inspectorate) adds some burden.

| Factory type | Overhead % (of conversion + labor) | Notes |
|---|---|---|
| Precision machining, large organized | 45-70% | Well-absorbed fixed costs, multiple shifts |
| Precision machining, mid-size | 55-85% | Moderate absorption |
| Precision machining, small job shop | 70-120% | Low volume, poor absorption |
| Automotive supplier (high automation) | 50-80% | High utilization drives down % |

### India-Specific Overhead Components
- **Power backup**: Generator + UPS adds 5-10% to energy cost (power reliability varies by state — Gujarat/Maharashtra better, UP/Bihar worse)
- **Compliance**: Pollution control board (PCB) fees, factory license, labor inspector compliance — typically 1-3% of overhead
- **Quality certification**: ISO 9001 / IATF 16949 / AS9100 maintenance — INR 3-8 lakh/year depending on scope

## Common Indian Aluminum Suppliers & Pricing

| Supplier | Material | Typical Price Range (INR/kg) | Notes |
|---|---|---|---|
| Hindalco (Aditya Birla Group) | 6061-T6, 6063, 2024 | 380-480 | Largest domestic producer; contract pricing available for >1 ton/month |
| Vedanta (BALCO) | Primary aluminum, some alloys | 350-430 | More commodity grades; limited alloy range |
| Imported (South Korea, China, UAE) | 6061-T6 plate | 420-550 | Higher quality consistency; import duty 7.5% + 18% GST |
| Indian distributors (Bharat Aluminium, Metline) | 6061-T6 cut-to-size | 450-600 | Premium for small quantities and cut-to-size service |

### Material Pricing Notes for India
- **Import duty on aluminum**: 7.5% basic customs duty + social welfare surcharge. Total effective duty ~10-12% on landed cost.
- **Indian vs. imported quality**: Hindalco 6061-T6 is generally acceptable for commercial applications. For aerospace or tight-tolerance work, imported material (Alcoa, Kaiser, Constellium) is often specified — at 20-40% premium.
- **Scrap market**: India has a well-developed aluminum scrap market. Machining chip recovery through local scrap dealers typically yields 30-45% of input material cost. Large shops negotiate better rates.

## Surface Treatment Costs (India)

| Treatment | Cost range (INR/part) | Notes | Typical location |
|---|---|---|---|
| Anodize Type II (clear) | 120-400 | Depends on part size and batch; MOQ often applies | Bangalore, Pune, Chennai clusters |
| Anodize Type III (hard) | 250-800 | Limited qualified suppliers in India | Bangalore, Pune |
| Zinc plating | 40-250 | Widely available | Most industrial clusters |
| Nickel plating | 150-650 | Quality varies significantly by supplier | Pune, Chennai, Delhi NCR |
| Powder coating | 80-400 | Very competitive in India | Everywhere |
| Passivation | 40-150 | Common for stainless parts | Most clusters |

## Logistics (Domestic India)

| Item | Cost range (INR/unit) | Notes |
|---|---|---|
| Basic packaging (corrugated box + foam) | 30-80 | Small-medium parts |
| Custom packaging (molded tray, VCI) | 80-200 | Precision parts requiring protection |
| Domestic road freight (per kg, within state) | INR 2-5/kg | LTL rates; FTL significantly cheaper |
| Domestic road freight (per kg, inter-state) | INR 4-10/kg | Distance-dependent; GST e-way bill required >INR 50,000 |
| Air freight (domestic, urgent) | INR 15-35/kg | For expedited shipments |

## Financial Benchmarks (Publicly Listed Indian Manufacturers)

Use these to cross-check overhead, SGA, and profit assumptions against real Indian companies.

| Company | Revenue (INR Cr) | Gross Margin | EBITDA Margin | Net Margin | Overhead implied | SGA implied |
|---|---|---|---|---|---|---|
| Bharat Forge | ~15,000 | 42-48% | 25-30% | 12-16% | High (forging, capital-intensive) | 8-10% |
| Sansera Engineering | ~2,800 | 38-42% | 18-22% | 10-13% | Moderate (precision machining) | 7-9% |
| Endurance Technologies | ~10,000 | 32-36% | 14-18% | 8-11% | Moderate (casting + machining) | 6-8% |
| Minda Industries | ~12,000 | 30-35% | 12-15% | 6-9% | Moderate (mixed manufacturing) | 7-10% |
| Craftsman Automation | ~3,500 | 40-45% | 20-25% | 10-14% | Moderate-high (precision machining) | 6-8% |

### How to Use These Benchmarks
- **Gross margin 35-45%**: Typical for Indian precision machining companies. Implies material is 55-65% of revenue (but includes all direct costs).
- **EBITDA margin 18-25%**: Healthy Indian manufacturer. If a supplier's implied margin from your model is far above this, there's room to negotiate. If below, the price may not be sustainable.
- **SGA 6-10%**: Cross-reference with the 8% default in overhead benchmarks. Indian companies on the lower end due to lower corporate costs.
- **Caution**: These are listed company averages. Small/medium unlisted suppliers may have higher overhead and SGA (10-15%) due to scale disadvantage.

## Sources
- IMTMA (Indian Machine Tool Manufacturers Association) — machine cost surveys
- CII (Confederation of Indian Industry) — manufacturing cost benchmarks
- ACMA (Automotive Component Manufacturers Association) — sector data
- Annual reports: Bharat Forge, Sansera, Endurance, Craftsman Automation (FY2024-25)
- GST rates from cbic.gov.in (Central Board of Indirect Taxes and Customs)
- Hindalco/Vedanta published price lists and investor presentations
