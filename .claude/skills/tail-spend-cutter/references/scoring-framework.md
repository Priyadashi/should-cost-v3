# Tail Spend Scoring Framework

## 20-Factor Model (5 Dimensions)

### Dimension 1: Financial/Volume (30% weight)

| # | Factor | Score 1 (Low) | Score 3 (Medium) | Score 5 (High) | Data Source |
|---|--------|---------------|-------------------|-----------------|-------------|
| 1 | Share of category spend | <1% | 1-5% | >5% | Calculated |
| 2 | Absolute spend | <$10K | $10K-$100K | >$100K | Spend data |
| 3 | Order frequency | <2/yr | 2-12/yr | >12/yr | Transaction count |
| 4 | Avg order size | <$500 | $500-$5K | >$5K | Calculated |
| 5 | Payment terms | Net 15 or worse | Net 30 | Net 45+ | AP data |
| 6 | Spend trend (YoY) | Declining >10% | Stable ±10% | Growing >10% | Historical |

**Sub-weights within dimension**: Equal (each ~16.7% of 30%)

### Dimension 2: Relationship (15% weight)

| # | Factor | Score 1 | Score 3 | Score 5 | Data Source |
|---|--------|---------|---------|---------|-------------|
| 7 | Supplier duration | <1 year | 1-3 years | >3 years | First transaction |
| 8 | Contract status | No contract | Expired/informal | Active contract | Contract data |
| 9 | Usage breadth | 1 department | 2-3 departments | 4+ departments | Org mapping |

**Sub-weights**: Equal (each ~33.3% of 15%)

### Dimension 3: Geographic (10% weight)

| # | Factor | Score 1 | Score 3 | Score 5 | Data Source |
|---|--------|---------|---------|---------|-------------|
| 10 | Domestic vs international | International (high risk) | International (low risk) | Domestic | Address data |
| 11 | Distance to facility | >1000 mi | 100-1000 mi | <100 mi | Geocoding |

**Sub-weights**: Equal (each 50% of 10%)

### Dimension 4: Performance & Risk (25% weight)

| # | Factor | Score 1 | Score 3 | Score 5 | Data Source |
|---|--------|---------|---------|---------|-------------|
| 12 | Quality score | <80% | 80-95% | >95% | QA data |
| 13 | Delivery performance | <85% on-time | 85-95% | >95% | Receiving data |
| 14 | Financial stability | High risk | Medium risk | Low risk | D&B / credit |
| 15 | Switching cost | High (custom/sole source) | Medium | Low (commodity) | Category analysis |

**Sub-weights**: Equal (each 25% of 25%)

### Dimension 5: Market (20% weight)

| # | Factor | Score 1 | Score 3 | Score 5 | Data Source |
|---|--------|---------|---------|---------|-------------|
| 16 | Number of alternatives | 0-1 | 2-4 | 5+ | Market research |
| 17 | Category criticality | Mission-critical | Important | Nice-to-have | Business impact |
| 18 | Market concentration | Monopoly/oligopoly | Moderate | Fragmented | Industry data |
| 19 | Price transparency | Opaque | Moderate | Transparent | Market analysis |
| 20 | Substitutability | No substitutes | Partial substitutes | Full substitutes | Category analysis |

**Sub-weights**: Equal (each 20% of 20%)

---

## Composite Scores

### Consolidation Priority Score (CPS) — Range 1-5

```
CPS = (Financial_Dim × 0.30) + (Relationship_Dim × 0.15) + (Geographic_Dim × 0.10)
    + (Performance_Dim × 0.25) + (Market_Dim × 0.20)
```

Each dimension score is the weighted average of its factors (1-5 scale).

**Interpretation:**
- CPS 1.0 - 2.0: Retain (strategic/critical supplier)
- CPS 2.0 - 3.0: Renegotiate (improve terms)
- CPS 3.0 - 4.0: Consolidate (merge into preferred supplier)
- CPS 4.0 - 5.0: Eliminate (find alternative or discontinue)

### Savings Potential Score (SPS) — Range 0-1

```
SPS = (market_alternatives_norm × 0.30) + (spend_volume_norm × 0.25)
    + (switching_cost_inv_norm × 0.25) + (price_transparency_norm × 0.20)
```

Where `_norm` means normalized to 0-1 from the raw factor scores, and `_inv_norm` is inverted (low switching cost = high savings potential).

### Risk Score (RS) — Range 0-1

```
RS = (criticality_norm × 0.30) + (switching_cost_norm × 0.25)
   + (quality_norm × 0.20) + (financial_stability_inv_norm × 0.15)
   + (concentration_norm × 0.10)
```

Higher RS = higher risk of disruption if supplier is changed.

---

## Decision Matrix

| CPS Range | RS < 0.3 (Low Risk) | RS 0.3-0.6 (Med Risk) | RS > 0.6 (High Risk) |
|-----------|---------------------|------------------------|----------------------|
| 4.0 - 5.0 | **Eliminate** | **Consolidate** (careful) | **Renegotiate** (monitor) |
| 3.0 - 4.0 | **Consolidate** | **Consolidate** | **Renegotiate** |
| 2.0 - 3.0 | **Renegotiate** | **Renegotiate** | **Retain** (optimize) |
| 1.0 - 2.0 | **Retain** | **Retain** | **Retain** (strategic) |

---

## Missing Data Handling

When a factor has no data available:
1. Assign neutral score of 3 (middle of 1-5 range)
2. Redistribute that factor's weight proportionally to other factors in the same dimension
3. Flag the supplier in the data quality report
4. If >50% of factors are missing for a supplier, flag as "Insufficient Data" — do not recommend action

## Weight Customization

Users can customize weights at two levels:
1. **Dimension level**: Adjust the 5 dimension weights (must sum to 1.0)
2. **Factor level**: Adjust individual factor weights within a dimension (must sum to 1.0 within dimension)

Default weights reflect consulting best practices for general tail spend analysis. Industry-specific adjustments:
- **Manufacturing**: Increase Performance & Risk to 35%, decrease Market to 15%
- **Services**: Increase Relationship to 25%, decrease Geographic to 5%
- **Technology**: Increase Market to 25%, decrease Geographic to 5%
- **Healthcare**: Increase Performance & Risk to 35%, increase Relationship to 20%, decrease Financial to 20%
