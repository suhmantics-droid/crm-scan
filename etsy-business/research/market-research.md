# Etsy digital market research: platform context, category sweep, and where the money is

Dated 2026-08-31. Confidence labels: VERIFIED (seen on Etsy directly / official), REPORTED (secondary source with numbers), ESTIMATED, INFERRED, ANECDOTAL, UNKNOWN. Etsy Marketplace Insights requires a seller account and was NOT accessible from this environment; that is the first thing to pull once the shop account exists.

---

## 1. Platform context

- Etsy remains a ~90M+ active-buyer marketplace with built-in discovery, which is the entire reason to start here rather than Gumroad/Shopify with no audience. REPORTED: [kupkaike.com](https://kupkaike.com/blog/gumroad-vs-etsy-for-selling-digital-products).
- Income is a power law. Median active shops (all categories) gross low hundreds per month; digital sellers reportedly do better (median roughly £400-800/mo claimed by one aggregator, top digital shops £8k-30k+/mo from 50-200 optimised listings). Treat these medians as ESTIMATED, weakly sourced: [insightagent.app](https://www.insightagent.app/guides/how-much-do-you-make-on-etsy), [customcy.com](https://customcy.com/blog/how-much-do-etsy-sellers-make/). The load-bearing fact is the shape (power law, catalogue-driven), not the exact medians.
- Digital conversion runs meaningfully above physical: overall Etsy benchmark 1-3%, digital reported at 3-7% with top listings higher, because there is no shipping friction. REPORTED: [outfy.com](https://www.outfy.com/blog/etsy-conversion-rate/), [gelato.com](https://www.gelato.com/blog/etsy-conversion-rate), [merchize.com](https://merchize.com/what-is-a-good-conversion-rate-on-etsy/). For modelling we use 2-3% (see finance/).
- Etsy Ads for digital: CPC reported $0.15-0.75; sub-$10 products are proportionally too expensive to advertise; £15+ products can sustain ads at ROAS ≥3. REPORTED: [mydesigns.io](https://mydesigns.io/blog/etsy-ads/), [goldcityventures.com](https://goldcityventures.com/are-etsy-ads-worth-it/).
- eRank Q2 2026: "digital products" as a search term ranked #6 on Etsy (up from #45 a year earlier); demand for the digital category itself is rising, not fading. REPORTED: [help.erank.com](https://help.erank.com/blog/top-etsy-searches-q2-2026/).

## 2. Category sweep (verdicts)

| Category | Demand | Competition | Typical price | Verdict |
|---|---|---|---|---|
| Budget planners / personal finance sheets | Very high ("google sheets budget" ~1,324 Etsy searches/mo, 112% CTR, REPORTED via eRank data quoted by [snazzydesignsforever.com](https://snazzydesignsforever.com/the-best-google-sheets-templates-to-sell-now/)) | Very high | £3-15 | SATURATED at generic level; premium/annual-refresh niches still work |
| Bookkeeping / accounting spreadsheets (small business) | High, proven premium sales (listing with 3.1k reviews at 4.8★ VERIFIED via search snippet: [etsy listing 1762253018](https://www.etsy.com/listing/1762253018/etsy-seller-bookkeeping-spreadsheet-etsy); 4,741 favourites on another, REPORTED) | Medium-high, mostly US-centric or Etsy-seller-centric | £8-30 | **UNDERSERVED in UK-specific and trade-specific versions** |
| UK sole trader / self assessment tax sheets | Clear existing sales, sophisticated products exist (VERIFIED listings mirror HMRC boxes) | Medium, thin quality tail | £7-25 | **UNDERSERVED + regulatory catalyst (MTD)** |
| Landlord / rental property trackers (UK) | Clear demand; competitor products already sophisticated (758-formula 2026/27 UK tracker, Section 24 handling, VERIFIED listing exists) | Medium-high | £10-30 | BALANCED; strong adjacent line, harder to lead with |
| Sales/CRM/lead trackers | Real listings across verticals (coaches, real estate, freelancers) VERIFIED; volume signals weaker than bookkeeping | Medium, quality mediocre | £5-20 | UNDERSERVED on depth (most are formatted tables, not sales systems) |
| Pricing calculators (crafters, bakers, candles, services) | Established niche, meta-market to Etsy sellers themselves | Medium | £5-15 | BALANCED, good entry products |
| Client onboarding / welcome packets (Canva) | Established, many 20-35 page kits VERIFIED | High, design-led | £10-40 | SATURATED unless verticalized; design is the differentiator (not our edge) |
| Wedding-vendor business templates (pricing guides, email scripts) | Established market pages VERIFIED | High | £10-40 | BALANCED but aesthetic-competitive |
| Wedding consumer (invitations, seating charts) | Huge | Extreme | £5-25 | SATURATED, no edge |
| CV / resume templates | Huge | Extreme (design-led, race to bottom) | £3-15 | SATURATED |
| Job-search trackers / interview prep | Moderate | Medium | £5-15 | BALANCED; adjacency for later |
| Notion templates | Sells on Etsy; Gumroad is the premium venue; 2026 velocity in life-admin + profession-specific systems. REPORTED: [kupkaike.com](https://kupkaike.com/blog/best-selling-notion-templates-etsy-gumroad-2026), [sendowl.com](https://www.sendowl.com/blog/tips-and-advice/best-selling-notion-template-categories) | Medium | £5-30 | BALANCED; format option, not a niche |
| Planners (ADHD, wellness), digital planners | Very high | Very high | £3-20 | SATURATED |
| SVG/cut files | Very high ("png" ~42k searches/mo May 2026, REPORTED eRank: [help.erank.com](https://help.erank.com/blog/trend-report/fastest-growing-etsy-keywords-summer-2026/)) | Extreme + IP minefield | £1-5 | SATURATED, excluded |
| Social media templates | High | Extreme | £5-25 | SATURATED |
| Trades/service business paperwork (cleaning, etc.) | Many market pages exist (VERIFIED); products basic | Low-medium per trade | £4-15 | **UNDERSERVED per-vertical: the "boring money" pocket** |
| Prompt packs | n/a | n/a | n/a | EXCLUDED by policy |
| Personalised digital (portraits, star maps) | High | High | £5-25 | Fulfilment labour per order; excluded by near-zero-fulfilment requirement |

## 3. The finding that drives the strategy

Three facts compound:

1. **Premium B2B digital demonstrably sells on Etsy.** A £10-20 bookkeeping spreadsheet with 3,100 reviews implies (at typical review rates of 15-25% of orders, INFERRED) five figures of unit sales on a single listing.
2. **The UK version of this market has a legal deadline attached.** Making Tax Digital for Income Tax: mandatory digital records + quarterly updates from 6 April 2026 for sole traders/landlords earning over £50k (864,000 people), dropping to £30k in April 2027 and £20k planned 2028. VERIFIED: [gocardless.com](https://gocardless.com/blog/mtd-itsa-sole-traders-landlords-2026-guide), [bytestart.co.uk](https://www.bytestart.co.uk/news-insights/864000-sole-traders-and-landlords-face-new-mtd-reporting-rules-from-april-2026/). Off-the-shelf software (£10-30/mo subscriptions) is exactly what a chunk of this market resents paying for; the "no subscription, own your records" motivation is a documented buyer pattern (see review-mining.md).
3. **The existing supply is weakest where we are strongest.** Complaint mining shows the category's recurring failures are process failures: broken/unprotected formulas, no instructions, no support, US assumptions. These are solved by engineering discipline, not graphic design.

The consumer printable market is real but is a design-and-volume game with power-law odds. The UK small-business money-admin market is smaller but has: higher prices, buyer urgency with a calendar (31 Jan self assessment, 6 April MTD waves), repeat purchase (new tax year = new edition), and natural per-trade verticalization that multiplies the catalogue without new invention.

## 4. Seasonality map (for the launch calendar)

- **September-January**: UK tax anxiety season (self assessment deadline 31 Jan). Peak for bookkeeping/tax products. We launch into it.
- **November-January**: budget/planner season (new-year energy). REPORTED: [snazzydesignsforever.com](https://snazzydesignsforever.com/the-best-google-sheets-templates-to-sell-now/).
- **March-April**: UK new tax year (6 April), MTD wave anniversaries; "2027/28 edition" refresh moment.
- **Year-round**: trades/service paperwork, landlord tools, CRM/lead trackers.

## 5. What we could not verify (honest gaps)

- Exact Etsy search volumes for our core keywords (Marketplace Insights + eRank free tier to be pulled once the shop account exists; first task in 30-day plan). UNKNOWN.
- Review counts for most named competitors (search snippets exposed only some). Marked UNKNOWN in competitors.csv.
- The digital-seller median income figures are aggregator claims without raw data. ESTIMATED at best.
- No empirical dataset on time-to-first-sale for digital shops exists; only forum anecdotes (2 days to several months). ANECDOTAL. The previous "165 days to first $1,000" figure is a Printify POD statistic and is NOT reused here for digital.
