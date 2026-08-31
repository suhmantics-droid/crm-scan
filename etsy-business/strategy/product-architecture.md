# Product architecture

Dated 2026-08-31. Prices chosen from the fee math (fixed fees punish sub-£5; ads only pay above ~£12) and category comparables; validate against live conversion in month 1-2 (willingness-to-pay testing = price moves of ±£3 on duplicate-market listings, one variable at a time).

## The ladder (applies to each product family)

| Tier | Role | Price band | Examples |
|---|---|---|---|
| ENTRY | Cheap, high-intent, review velocity, funnel | £4.99-8.99 | HMRC Mileage Log £4.99; Day-Rate Calculator £8.99; Tax Estimator £9.99 |
| CORE | The flagship job-to-be-done | £12.99-16.99 | Sole Trader Bookkeeping £16.99; CRM+Follow-up £14.99; trade kits £12.99 |
| PREMIUM | Deeper/bigger versions | £19.99-24.99 | Landlord Tracker £19.99; multi-property/multi-user variants |
| BUNDLE | Same-buyer combinations | £24.99-29.99 | Self-Employed Starter (bookkeeping+estimator+mileage) £24.99 |
| MEGA BUNDLE | Whole-line value anchor | £34.99-49.99 | "Everything for your trade" £34.99; whole-shop £49.99 later |
| UPSELL | Post-purchase companion at small discount | n/a | Bought bookkeeping → CRM at 20% off (via Etsy post-purchase message/coupon) |
| CROSS-SELL | In-listing + packaging slide | n/a | Every kit shows its family grid on image 8 |
| CUSTOM | "Your logo + categories set up for you" | +£10-15 | Personalisation add-on on kits (bounded scope, 1 revision) |
| SEASONAL | Tax-year editions | same price | 2026/27 → 2027/28 refresh each March; free to past buyers (retention), new SKU for search ("2027/28") |

## The two engines behind every SKU

1. **LEDGER ENGINE**: settings → income ledger → expense ledger (HMRC categories) → dashboards (M/Q/Y) → tax summary (SA box mapping) → set-aside estimator → mileage. Skins into: sole trader, freelancer, Etsy seller, landlord (swap ledger for per-property), reseller (adds COGS/platform fees), driver, holiday let, market trader.
2. **CLIENT ENGINE**: contacts → pipeline (stages with exit criteria) → next-action engine (today view) → follow-up log → won/lost analytics. Skins into: generic CRM, recruiter, salon/groomer client cards (adds service history), trades quote tracker (adds quote→job conversion).

Every SKU = engine + vertical fields + vertical copy + vertical demo data. Architecture rule: an engine change propagates to all skins (see operations/production-sop.md).

## Willingness-to-pay research plan (do not assume the prices)

- Week 1: record top-10 competitor prices per family with review counts (Etsy app).
- Month 1-2: A/B via duplicate-format listings at ±£2-3; keep the winner.
- Bundle price = ~55-65% of components' sum: matches category convention and protects AOV.
- January test: raise flagship to £19.99 during peak demand; watch conversion.
