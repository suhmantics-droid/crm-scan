# FINAL REPORT: the Etsy digital business to build

Dated 2026-08-31. The 24 answers, each with its evidence file.

**1. What should I sell?** UK small-business money and operations spreadsheets: flagship = UK Sole Trader Bookkeeping + Self Assessment Tracker 2026/27 (Google Sheets + Excel, £16.99), surrounded by a tax estimator, mileage log, per-trade business kits (cleaning, salon, dog groomer, trades), a CRM/follow-up engine, and bundles. (strategy/winner.md)

**2. Who buys it?** UK one-person businesses: sole traders, freelancers, service trades, landlords, resellers. One buyer identity, many verticals. (research/customer-segments.md)

**3. Why do they buy?** A legal duty to keep digital records (MTD: 864k people from Apr 2026, £30k wave Apr 2027), January dread, subscription resentment ("buy once, own it, data stays in your account"), and wanting to look/feel like a real business. (research/customer-problems.md)

**4. What do they search?** "bookkeeping spreadsheet uk", "self assessment spreadsheet", "sole trader accounts", "lead tracker", "cleaning business invoice", "landlord spreadsheet uk", + 500-term database with sources. (research/keywords.csv)

**5. How competitive is it?** The generic ends (budget planners, CV templates) are saturated and scored down accordingly; the UK-specific, trade-specific and method-deep pockets are underserved. Verdicts per category in research/market-research.md.

**6. What are competitors doing?** Selling individually decent but unbranded products: 3.1k-review bookkeeping listings, sophisticated landlord trackers, formatted-table CRMs, document-only trade kits. (research/competitor-analysis.md)

**7. What are they doing badly?** Fragile/unprotected formulas, missing instructions, US defaults, single-format files, no support, no updates, no sales method inside sales tools. Every one documented from buyer complaints. (research/review-mining.md)

**8. Why can we win?** The category's failure modes are engineering/process failures, and our production system (Claude Code + QA SOP) makes the quality floor cheap; plus UK-first positioning with a dated regulatory catalyst nobody on the platform owns yet, plus domain-credible sales tools. (strategy/winner.md)

**9. What does it cost?** ~£50 startup (setup fee + 20 listings + £0 tools). ~£10/wk of time after launch month. (research/tools.md, finance/)

**10. What price?** Ladder: £4.99 entry → £12.99-16.99 core → £19.99-24.99 premium → £24.99-34.99 bundles. Flagship £16.99. (strategy/product-architecture.md)

**11. What is the margin?** ~84-86% net of all UK Etsy fees at core prices; ~66% on offsite-ad-attributed sales; Share & Save sales better by 4pts. Worked math per SKU in finance/unit-economics.csv.

**12. How many sales for £1k/mo?** ~67 orders/month at £15 AOV (2.2/day) ≈ 2,700 visits at 2.5% conversion. BASE timing: month 5-7. (finance/£1k-model.md)

**13. How many for £5k/mo?** ~294 orders/month at £17 AOV (~9.8/day, ~11,800 visits). Verdict: POSSIBLE BUT DIFFICULT, months 12-18 if base case lands, needs 150+ listings, bundles ≥30%, and probably the Shopify layer. (finance/£5k-model.md)

**14. How many listings?** 10 by day 30, 35-45 by day 90, 80-100 by month 6, 150-250 by month 12: with 5-15 winners doing the heavy lifting (the category is a power law; breadth buys tickets, quality converts them). (strategy/catalogue-strategy.md)

**15. First 20 products?** products/first-20.csv: flagship + estimator + mileage + freelancer + CRM + cleaning kit + invoice-chase + salon + groomer + starter bundle, then trades/gardener/pricing/reseller/landlord/Etsy-seller/market-trader/trade-bundle/recruiter/commission.

**16. Shop name?** SortedSheets (recommended; alternatives TallyKit, TheSoloBooks). Clear the name day 1 (Etsy/.co.uk/IPO/Companies House). (strategy/positioning.md)

**17. Connected to Suhmantics?** No: separate brand, built to stand alone and graduate to its own Shopify property; aufentic stays completely separate. Suhmantics may own it legally, never customer-facing. (strategy/positioning.md)

**18. What on Shopify?** Nothing yet. Gate: £750/mo × 2 months + 300 orders. Then: mega bundles, pro/setup services, email launches, optional Tax Year Club. (strategy/shopify-strategy.md)

**19. What on Pinterest?** The secondary engine: 3-5 pins/day (product pins + UK tax checklist infographics), all Share & Save links, batched weekly. (content/content-strategy.md)

**20. What on TikTok?** 2-3 shorts/week: 20-40s screen demos and "UK tax facts for the self-employed"; same clips to Shorts/Reels. (content/content-strategy.md + 100-content-ideas.md)

**21. What to automate?** Spreadsheet generation (both formats from one spec), QA test suite, demo data, listing drafts, keyword clustering, image text variants, pin scheduling, support drafts, monthly stats tables. (operations/ai-production-system.md)

**22. What NOT to automate?** Final formula verification, the hostile-buyer QA pass, tax-figure accuracy checks against gov.uk, sending any customer message, review responses, pricing decisions, and anything Etsy requires to be honest (AI disclosure, claims). (operations/qa-sop.md)

**23. What could kill it?** (a) Cold-start discovery failure: mitigated by tax-season launch timing, entry SKUs for review velocity, Pinterest from day 1, and the day-90 kill/pivot gate; (b) an accuracy error in a tax-adjacent product: mitigated by the C-pass accuracy gate and records-not-advice framing; (c) platform dependence/suspension: mitigated by clean policy posture (no PLR, no prompts, disclosed AI, original work) and the email list + Shopify path; (d) a strong incumbent copying the MTD positioning: mitigated by moving now and owning updates/support.

**24. What do I do tomorrow?** Day 1 of launch/30-day-plan.md: clear the shop name (Etsy, .co.uk, IPO, Companies House), open the shop account, buy the domain. Then day 2: pull Marketplace Insights volumes for the 25 priority keywords and update keywords.csv with real numbers.
