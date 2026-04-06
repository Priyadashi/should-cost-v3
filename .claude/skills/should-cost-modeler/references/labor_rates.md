# Labor Rate Reference Data

## Purpose
This file provides fully-loaded labor rates by country, region, and skill tier for use in should-cost calculations. Rates include base wage, benefits, social charges, and employer-side taxes. They do NOT include overtime premiums, shift differentials, or temporary labor markups — add those separately if applicable.

## How to Use
1. Identify the supplier's country/region
2. Select the appropriate skill tier for each process step
3. Use the "typical" rate as your base assumption (medium confidence)
4. Use the "best-in-class" rate for could-cost / best-case scenarios
5. If the supplier's country is not listed, use the closest regional proxy and note reduced confidence

## Skill Tier Definitions

| Tier | Description | Typical roles |
|---|---|---|
| Unskilled | No specialized training required | Material handling, packaging, simple assembly |
| Semi-skilled | Basic machine operation training (weeks) | Machine operators (attended), basic inspection, forklift |
| Skilled | Formal training or apprenticeship (months-years) | CNC operators, welders, tool setters, quality inspectors |
| Technician | Technical diploma or equivalent | CNC programmers, maintenance technicians, process engineers |
| Engineer | University degree | Design engineers, manufacturing engineers, project managers |

## Rates by Country (USD/hour, fully loaded, 2024-2025 benchmarks)

### North America

| Country | Unskilled | Semi-skilled | Skilled | Technician | Engineer |
|---|---|---|---|---|---|
| USA (national avg) | $18-24 | $24-32 | $32-45 | $45-65 | $55-85 |
| USA (Southeast — lower cost) | $15-20 | $20-28 | $28-40 | $40-55 | $50-75 |
| USA (Northeast/West Coast) | $22-30 | $28-38 | $38-52 | $52-75 | $65-100 |
| Canada | $17-23 | $23-30 | $30-42 | $42-60 | $52-80 |
| Mexico | $4-7 | $6-10 | $9-15 | $14-22 | $18-30 |

### Europe

| Country | Unskilled | Semi-skilled | Skilled | Technician | Engineer |
|---|---|---|---|---|---|
| Germany | $28-36 | $36-48 | $45-60 | $55-75 | $70-100 |
| France | $24-30 | $30-40 | $38-50 | $48-65 | $60-90 |
| Italy | $20-26 | $26-34 | $32-44 | $42-58 | $52-78 |
| Spain | $16-22 | $22-28 | $28-38 | $36-50 | $45-68 |
| Poland | $8-12 | $12-16 | $15-22 | $20-30 | $25-40 |
| Czech Republic | $9-13 | $13-18 | $17-24 | $22-32 | $28-44 |
| Romania | $6-9 | $9-13 | $12-18 | $16-24 | $20-34 |
| Turkey | $5-8 | $7-11 | $10-16 | $14-22 | $18-30 |
| UK | $22-28 | $28-36 | $35-48 | $46-64 | $58-88 |

### Asia

| Country | Unskilled | Semi-skilled | Skilled | Technician | Engineer |
|---|---|---|---|---|---|
| China (coastal/Tier 1) | $5-8 | $7-11 | $10-16 | $14-24 | $18-32 |
| China (inland/Tier 2-3) | $3-5 | $5-8 | $7-12 | $10-18 | $14-24 |
| India | $2-4 | $3-6 | $5-9 | $8-14 | $10-20 |
| Vietnam | $2-4 | $3-5 | $5-8 | $7-12 | $10-18 |
| Thailand | $3-5 | $5-8 | $7-12 | $10-18 | $14-24 |
| Japan | $22-30 | $30-40 | $38-52 | $48-68 | $60-95 |
| South Korea | $18-24 | $24-32 | $30-42 | $40-55 | $50-78 |
| Taiwan | $12-16 | $16-22 | $20-30 | $28-40 | $35-55 |

### Other Regions

| Country | Unskilled | Semi-skilled | Skilled | Technician | Engineer |
|---|---|---|---|---|---|
| Brazil | $5-8 | $8-12 | $11-18 | $16-26 | $20-35 |
| South Africa | $3-5 | $5-8 | $7-12 | $10-18 | $14-25 |
| Morocco | $3-5 | $4-7 | $6-10 | $9-15 | $12-22 |
| Indonesia | $2-3 | $3-5 | $4-7 | $6-11 | $8-16 |

## Productivity Adjustment Factors

Labor rates tell only half the story. Productivity varies significantly. Apply these multipliers to the labor time (not the rate) when comparing across regions.

| Region | Productivity factor (vs. Western Europe baseline of 1.0) |
|---|---|
| Germany, Japan, South Korea | 1.0 (baseline — highest productivity) |
| USA, Canada, UK, France | 0.95-1.0 |
| Eastern Europe (Poland, Czech) | 0.85-0.95 |
| China (coastal, established factories) | 0.80-0.90 |
| Mexico (mature maquiladora operations) | 0.80-0.90 |
| India, Vietnam, Indonesia | 0.65-0.80 |
| China (inland, newer operations) | 0.70-0.85 |

To use: if a task takes 10 minutes at productivity factor 1.0, it takes 10/0.80 = 12.5 minutes at factor 0.80. Apply the adjustment to the cycle time, then multiply by the local labor rate.

## Sources and Update Frequency
- US Bureau of Labor Statistics (BLS) International Labor Comparisons
- Eurostat Labour Cost Index
- ILO Global Wage Report
- Industry benchmarks from manufacturing trade associations
- Rates should be validated annually; material changes in exchange rates or inflation may require more frequent updates

## Confidence Guidance
- If supplier country is known and matches a row above: **high confidence**
- If using a regional proxy (e.g., "Southeast Asia" when exact country unknown): **medium confidence**
- If country is not listed and using a broad estimate: **low confidence** — flag for human review
