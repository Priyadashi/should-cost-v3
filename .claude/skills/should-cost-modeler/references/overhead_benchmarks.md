# Overhead, SGA, and Profit Margin Benchmarks

## Purpose
This file provides industry-benchmarked rates for factory overhead, selling/general/administrative costs (SGA), and supplier profit margins. These are applied on top of direct costs (material + conversion + labor) to arrive at the full should-cost.

## How Overhead Stacks Up

The cost buildup follows this structure:

```
  Direct material cost
+ Direct conversion cost (machine time)
+ Direct labor cost
= Prime cost
+ Factory overhead (% of conversion + labor)
= Total factory cost
+ SGA (% of total factory cost)
= Full cost
+ Profit (% of full cost)
= Ex-works price
+ Logistics (packaging, freight, duties)
= Landed / Total Cost of Acquisition
```

## Factory Overhead

Factory overhead covers indirect costs of running the manufacturing facility: facility rent/depreciation, utilities not directly tied to a machine, indirect labor (supervisors, material handlers, maintenance), quality department, factory IT, environmental/safety compliance, and general factory supplies.

### Overhead Rates by Industry and Factory Type

| Factory type / industry | Overhead % (of direct conversion + labor) | Notes |
|---|---|---|
| **Precision machining (job shop, small)** | 120-180% | Small shops have high overhead relative to low volume |
| **Precision machining (production, medium-large)** | 80-130% | Better absorption across higher volume |
| **Metal stamping / forming** | 70-110% | Lower skill requirement, higher automation |
| **Injection molding** | 90-140% | Mold depreciation can inflate overhead significantly |
| **Die casting** | 100-150% | Energy-intensive, high capital equipment |
| **Electronic assembly** | 80-120% | Cleanroom / ESD requirements add cost |
| **General mechanical assembly** | 60-90% | Lower capital intensity |
| **Welding / fabrication** | 80-120% | Ventilation, safety requirements |
| **Surface treatment (plating, anodizing, painting)** | 100-160% | Environmental compliance, chemical handling |

### Regional Overhead Adjustments

Factory overhead rates also vary by region due to facility costs, energy prices, and regulatory burden.

| Region | Adjustment vs. US baseline |
|---|---|
| USA (baseline) | 1.0× |
| Western Europe (Germany, France) | 1.05-1.15× (higher energy, stricter regulation) |
| Eastern Europe | 0.70-0.85× |
| China (coastal) | 0.60-0.80× |
| China (inland) | 0.50-0.70× |
| India | 0.45-0.65× |
| Mexico | 0.65-0.80× |
| Japan | 1.0-1.10× |

### How to Apply

1. Select the base overhead % from the factory type table
2. Choose a point within the range based on factory size (smaller = higher %) and automation level (more automated = lower %)
3. Apply the regional adjustment if the supplier is not US-based
4. Use the midpoint of the resulting range as your "reasonable best-in-class" assumption
5. Document your choice and tag as medium confidence unless you have specific factory data

## SGA (Selling, General & Administrative)

SGA covers corporate-level costs not tied to the factory floor: sales staff, executive management, corporate offices, legal, HR, accounting, insurance, corporate IT, R&D amortization.

### SGA Rates by Company Size

| Company size (annual revenue) | Typical SGA % (of total factory cost) |
|---|---|
| Small (<$50M revenue) | 10-15% |
| Mid-size ($50M-$500M) | 7-12% |
| Large ($500M-$5B) | 5-9% |
| Very large (>$5B) | 4-7% |

### SGA by Industry

| Industry | Typical SGA % |
|---|---|
| Automotive tier 1-2 suppliers | 5-8% |
| Industrial / mechanical components | 7-12% |
| Aerospace / defense suppliers | 10-15% |
| Medical device manufacturing | 12-18% |
| Consumer electronics (contract mfg) | 4-7% |
| Chemical / process industries | 6-10% |

### How to Apply

If you know the supplier's approximate size and industry, cross-reference both tables and use the overlapping range. If unknown, use 8% as a reasonable default for mid-size industrial manufacturers.

## Profit Margins

Profit is expressed as a percentage of full cost (factory cost + SGA). It represents the supplier's return for capital employed, risk, and intellectual property.

### Typical Profit Margins by Context

| Context | Typical profit % |
|---|---|
| **Commodity parts, high competition** | 3-6% |
| **Standard manufactured parts** | 5-8% |
| **Engineered-to-order / custom parts** | 8-12% |
| **Proprietary / sole-source parts** | 10-20%+ |
| **Contract manufacturing (electronics)** | 3-6% |
| **Aerospace certified parts** | 10-15% |
| **Medical / regulated parts** | 12-18% |
| **Services (outsourced processes)** | 8-15% |

### How to Apply

1. Assess the competitive landscape: how many qualified suppliers exist?
2. More competition → lower reasonable profit margin
3. Proprietary technology / captive supply → higher margin is "reasonable" (even if you don't like it)
4. Use the midpoint of the applicable range
5. If the implied profit from the supplier's quote seems far above these ranges, that's a negotiation point — but frame it as "we'd like to understand what drives the premium" not "your margin is too high"

## Quick Reference: Default Assumptions

For a fast estimate when you lack specific company data, use these defaults:

| Parameter | Default value | Confidence |
|---|---|---|
| Factory overhead | 100% of conversion + labor | Medium |
| SGA | 8% of factory cost | Medium |
| Profit | 7% of full cost | Medium |
| Packaging | $0.50-2.00 per unit (size dependent) | Low |
| Domestic freight | $0.50-3.00 per unit (weight/size dependent) | Low |

These defaults are calibrated for a mid-size, standard manufactured component supplier in a developed economy. Adjust for specific contexts using the detailed tables above.

## Sources
- Annual reports and financial statements of publicly traded suppliers (gross/operating margin analysis)
- Industry surveys from AMT (Association for Manufacturing Technology), MEMA, IPC
- Procurement benchmark databases (Kearney, Hackett Group)
- Should be cross-referenced with actual supplier financial data when available
