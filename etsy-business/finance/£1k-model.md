# The £1,000/month model

Dated 2026-08-31. Everything here is MODELLED, not forecast. Observed data, assumptions, and modelled results are separated per the brief.

## Observed inputs (evidence class in brackets)
- Net margin ~83-85% at core prices; blended net/order ≈ £12.60-13.40 at £15-16 AOV (CALCULATED from REPORTED fee rates: see unit-economics.csv).
- Etsy digital conversion benchmarks: overall 1-3%; digital reported 3-7% (REPORTED, tool-vendor sources).
- Category price comparables support £12.99-19.99 cores and £24.99+ bundles (VERIFIED/REPORTED).
- Orders per listing per month: no published average exists (UNKNOWN): modelled 0.15/0.5/1.2 (LOW/BASE/HIGH) per catalogue-strategy.md, consistent with the observed power-law shape.

## Assumptions (chosen, not observed)
- AOV £15 blended (price ladder + ~20% bundle share). Conversion 2.5% used (below digital benchmark midpoint: deliberate conservatism). Review rate ~20% of orders. Seasonal multiplier 1.5-2x Nov-Jan on the finance line.

## The arithmetic
£1,000 gross/month ÷ £15 AOV = **~67 orders/month ≈ 2.2/day** (net to us ≈ £850).
If the target is £1,000 NET: ~79 orders/month.

Traffic required at 2.5% conversion: 67 ÷ 0.025 = **~2,680 visits/month** (~90/day).

Listings required:
| Scenario | Orders/listing/mo | Listings for 67 orders |
|---|---|---|
| LOW (0.15) | 447 (not viable: quality floor + winners needed, not raw count) |
| BASE (0.5) | ~134 |
| HIGH (1.2) | ~56 |

The honest reading: raw listing count alone gets there only in BASE at ~135 listings. Reality in this category is a skewed distribution: a few winners at 5-20 orders/mo carry a long tail near zero. The plan therefore aims for **80-100 quality listings, of which 5-8 become winners**, + the seasonal spike doing the rest.

## Scenarios (month 6, ~80-100 listings live)
| | LOW | BASE | HIGH |
|---|---|---|---|
| Orders/mo | 25 | 65-80 | 140 |
| Gross | ~£375 | ~£975-1,200 | ~£2,240 |
| Net after fees | ~£315 | ~£820-1,010 | ~£1,880 |
| When £1k gross/mo hits | month 10-12 (needs Jan peak) | **month 5-7** | month 3-4 |

## What must be true for BASE
1. 10 listings live in month 1, ~80 by month 6 (production SOP throughput: comfortably feasible at ≤10h/wk).
2. At least 2 of the first 10 listings find search traction in tax season (the reason we launch the flagship into Sept-Jan).
3. Review flywheel: entry SKUs at £4.99-9.99 generate 25+ reviews by month 3.
4. Pinterest + Share & Save adds 15-25% incremental visits by month 4-6.

## Sensitivity (what breaks it)
- Conversion 1.5% instead of 2.5% → visits needed ~4,500/mo → push HIGH-case content or delay to month 8-10.
- AOV £12 (bundles fail) → 84 orders needed → bundle strategy is not optional.
- Zero winners by day 60 → invoke the pivot checkpoint in launch/90-day-plan.md (re-SEO, re-thumbnail, re-price before adding volume).
