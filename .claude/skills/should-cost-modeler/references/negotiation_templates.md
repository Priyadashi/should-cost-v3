# Negotiation Templates and Diagnostic Questions

## Purpose
This file provides reusable negotiation frameworks, diagnostic question banks, and contract clause templates. These are commodity-agnostic — they supplement the commodity-specific questions in each commodity module.

## The Core Negotiation Framing

Open every cost discussion with this positioning statement (adapt the exact words to your style):

> "We have built a detailed cost model for this part/service based on publicly available market data and industry benchmarks. We want to share our assumptions with you openly. Where our assumptions differ from yours, we want to understand why. If you can show us better data, we will update our model. Our goal is a fair price based on facts, not a number pulled from thin air."

This framing accomplishes three things:
1. Signals competence (we did the work)
2. Signals fairness (we're open to being wrong)
3. Shifts the burden of proof (the supplier must explain their costs, not just defend their price)

## Diagnostic Question Bank by Cost Category

### Material Cost Questions

Use when: your material cost assumption differs from the supplier's quoted material content by more than 10%.

- What material grade are you using? Is it the grade specified, or are you using a more expensive substitute?
- From which supplier(s) do you purchase this material? When was the last time you renegotiated your material contract?
- What is your material utilization rate for this part? How does it compare to your average for similar parts?
- Are you including material scrap allowance in your cost? What is your typical scrap rate for this process?
- What lot size do you purchase material in? Are there minimum order quantity premiums embedded in your rate?
- Are you aware of our internal material purchasing program? Would participating in our volume agreements reduce your input cost?
- Has the material specification changed since the last quote? Are we comparing the same part number and revision?

### Process / Conversion Cost Questions

Use when: your conversion cost estimate differs from the supplier's by more than 15%.

- What machine type and model do you use for this operation? What is its rated capacity/tonnage?
- What cycle time are you achieving on this part? How does it compare to your estimate when the part was first quoted?
- How many setups does this part require? Have you explored fixture changes that could reduce setup count?
- What batch size do you typically run for our orders? Is there a more economical batch size that better amortizes setup?
- What is your overall equipment effectiveness (OEE) for the machines running this part?
- Are you running this part on the optimal machine for the operation, or is it running on an oversized/undersized machine due to scheduling constraints?
- What feed rates and speeds are you using? Are they at the material manufacturer's recommended parameters?

### Labor Cost Questions

Use when: your labor assumption differs from the supplier's, or labor appears high relative to the process.

- How many operators are assigned to this operation? Is it attended or can it run lights-out/semi-attended?
- What is the operator's role during the machine cycle — are they actively working or waiting?
- What skill level is required for this operation? Could a less skilled (lower cost) operator perform it with appropriate training or fixtures?
- What is the labor content per unit vs. per batch? How much is direct productive labor vs. setup/changeover?
- Are overtime premiums or shift differentials included in the quoted rate? What percentage of this work runs on overtime?

### Overhead and SGA Questions

Use when: the implied overhead or SGA seems high relative to industry benchmarks.

- Can you provide a breakdown of your overhead rate? What are the major components?
- How do you allocate overhead to individual parts — by machine hours, labor hours, or revenue?
- Has your overhead rate changed significantly in the past 2-3 years? What drove the change?
- Are there any one-time costs (tooling amortization, engineering charges, certification costs) embedded in the unit price that should be broken out separately?

### Profit and Pricing Questions

Use when: the gap between your full-cost estimate and the supplier's quote suggests excessive margin.

- We respect that you need a fair return on your investment. Can you help us understand what level of margin you need to maintain this business?
- Are there any costs in your quote that are not related to our part specifically — allocation of R&D, capital for other programs, etc.?
- How does the pricing for this part compare to similar parts you manufacture for other customers at similar volumes?
- Is there price texturing in effect — are some parts in our portfolio underpriced while others carry a premium to compensate?

## Time-Phased Savings Framework

### Recover Now (negotiate immediately)
These are savings between the quoted price and the does-cost — the supplier cannot justify them even using their own assumptions.

Typical sources:
- Excess profit above reasonable benchmarks
- Price texturing that overcharges on some parts
- Outdated pricing that hasn't tracked material cost decreases
- Unexplained cost elements the supplier cannot substantiate

Contract action: immediate price reduction effective with next purchase order.

### Short-Term (0-6 months, contractually committed)
These are savings between the does-cost and should-cost — achievable by improving operations within the supplier's current capital base.

Typical sources:
- Optimizing batch sizes and order quantities
- Correcting non-optimal machine routings
- Implementing lean manufacturing improvements
- Reducing scrap and rework rates
- Improving material utilization

Contract action: specify the improvement, the target cost reduction, and the implementation date. Include automatic price deduction on the due date unless both parties agree to an extension.

### Medium-Term (6-18 months, roadmap with milestones)
These are savings between the should-cost and could-cost — requiring capital investment, new technology, or sourcing changes.

Typical sources:
- Investing in more productive equipment
- Moving production to a lower-total-cost location
- Qualifying a new, more efficient supplier
- Implementing automation for labor-intensive steps
- Redesigning tooling for higher throughput

Contract action: joint investment plan with shared cost/benefit. Define milestones, target cost at each milestone, and commitment to re-quote at each stage.

## Contract Clause Templates

### Commodity Index Linkage
```
The unit price shall be adjusted quarterly based on changes in [INDEX NAME]
published by [SOURCE]. The base index value is [VALUE] as of [DATE].

Adjustment formula:
  New price = Base price × (Material share × (Current index / Base index)
              + (1 - Material share))

Where Material share = [XX]% of the unit price.

Adjustments apply only when the index moves more than [±X]% from the
previous adjustment point. Adjustments are capped at [±Y]% per quarter.
```

### Annual Productivity Improvement
```
Conversion cost elements of the unit price shall be reduced by [X]% annually,
effective [DATE] each year, reflecting expected productivity improvements through
lean manufacturing, process optimization, and learning curve effects.

This reduction applies to: [machine time, labor, and factory overhead] but
NOT to: [raw materials, which are indexed separately, or logistics].
```

### Milestone-Based Reduction
```
The parties agree to the following cost reduction roadmap:

Milestone 1: [Description of supplier action] by [DATE]
  → Price reduces by $[X] per unit effective [DATE]

Milestone 2: [Description of action] by [DATE]
  → Price reduces by $[X] per unit effective [DATE]

If a milestone is not achieved by its target date, the parties shall meet
within 30 days to agree on a revised timeline. The price reduction associated
with a missed milestone shall take effect no later than [X months] after
the original target date.
```

### Price Re-Opener Trigger
```
Either party may request a price review if:
- Annual order volume deviates more than [±20]% from the contracted volume
- A material index used in the pricing formula moves more than [±15]% in
  a 90-day period
- A significant change in product design or specification affects
  manufacturing cost by more than [±10]%

The review shall be conducted using the agreed-upon cost model and completed
within [30] days of the request.
```

## Sources
- McKinsey Cleansheet methodology (negotiation framing and cost threshold segmentation)
- BCG "Profit from the Source" (technical vs. commercial levers, catalyst workshop principles)
- Kearney Purchasing Chessboard (process benchmark, supplier pricing review)
- US Department of Defense should-cost review guidelines
- Industry standard contract practices from CIPS and ISM
