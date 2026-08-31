# 30-day launch plan

Dated 2026-08-31. Assumes ~2h/day weekdays, lighter weekends. Every day: Task / Output / Time / Tool / Success criterion. Days are sequential working days; slippage shifts the tail, never the QA gates.

| Day | Task | Output | Time | Tool | Success criterion |
|---|---|---|---|---|---|
| 1 | Name checks (Etsy, .co.uk, IPO trademark, Companies House) + open shop account + buy domain | Shop registered, name locked, domain parked | 2h | Browser | Shop exists; name clear on all four checks |
| 2 | Pull Marketplace Insights + eRank free for the 25 priority keywords in keywords.csv; record volumes | keywords.csv updated with real volumes | 2h | Etsy dashboard, eRank | Every priority-1 keyword has a volume or a measured "UNKNOWN" |
| 3 | Live competitor pass on Etsy app: top 10 listings for 5 core families; record prices/reviews; read 100+ reviews; append findings | competitors.csv + review-mining.md updated with live data | 2h | Etsy app | 50 rows with real review counts; any thesis-breaking surprise flagged |
| 4 | DECISION GATE: confirm flagship spec against day 2-3 data; write flagship spec YAML | Flagship spec | 2h | Editor | Spec has worked examples for every calculation |
| 5-6 | Build flagship (Sheets + Excel) via production SOP steps 1-2 | Both files built | 4h | Claude Code, Sheets, openpyxl | Automated QA section A passes |
| 7 | QA flagship (B + C passes), fix, re-run | QA log entry | 2h | qa-sop.md | Full checklist green |
| 8 | Package: quick-start PDF, walkthrough video, zips; shop branding (banner, icon, about, policies) | Deliverables + shop shell complete | 2.5h | Canva, OBS/Loom | 15-min buyer test passes on clean account |
| 9 | Listing 1 live (title/tags/desc from master CSV, 8 images + video); test purchase | Flagship live | 2h | Etsy, Figma/Canva template | Listing live; test download works |
| 10 | Build + QA Mileage Log (entry SKU) | Product 3 done | 2h | SOPs | QA green |
| 11 | List Mileage Log; build Tax Estimator | Listing 2 live; product 2 built | 2h | SOPs | QA green on estimator maths vs worked examples |
| 12 | QA + list Tax Estimator; create Starter Bundle listing | Listings 3-4 live | 2h | SOPs | 4 live listings |
| 13 | Pinterest business account; board structure; first 10 pins from listing images (Share & Save links) | Pinterest live | 1.5h | Pinterest | 10 pins scheduled |
| 14 | Weekly review #1: stats, fix anything broken; rest | Notes | 1h | Etsy stats | Baseline metrics recorded |
| 15-16 | Build freelancer edition (ledger skin) + invoice-chase tracker | Products 4+7 built | 4h | SOPs | QA green both |
| 17 | List both; social handles reserved (TikTok/IG); first screen-demo short recorded | Listings 5-6 live; 1 short posted | 2h | CapCut | 6 live listings |
| 18-19 | Build CRM + Follow-up Engine (client engine full build) | Product 5 built | 4h | SOPs | QA green incl. Today-view logic |
| 20 | List CRM; 5 more pins; second short | Listing 7 live | 2h | Etsy, Pinterest | 7 live |
| 21 | Weekly review #2; respond to any messages <24h; price/thumbnail tweaks only if data (≥100 views) supports | Notes | 1h | Stats | Response time 100%; no blind tweaks |
| 22-23 | Build Cleaning Business Kit (quote calc + trackers) | Product 6 built | 4h | SOPs | QA green incl. quote maths |
| 24 | List Cleaning Kit; build Salon kit (client-engine skin) | Listing 8 live; product 8 built | 2.5h | SOPs | QA green |
| 25 | List Salon kit; build Groomer kit (skin) | Listing 9 live; product 9 built | 2h | SOPs | QA green |
| 26 | List Groomer kit + Run Your Trade bundle draft; pin batch | Listing 10 live | 2h | Etsy | **10 live listings: launch set complete** |
| 27 | Etsy-message follow-up flow set up (thank-you + help offer, no review begging); FAQ sweep into listings | Message templates live | 1.5h | Etsy, cs-sop | Templates comply with review policy |
| 28 | Weekly review #3: full funnel table (views→favourites→orders per listing) | Metrics table | 1.5h | Stats export | Every listing has data recorded |
| 29 | First iteration pass: re-SEO the 2 weakest listings (new lead keyword + thumbnail) | 2 listings revised | 2h | keywords.csv | Changes logged for 14-day comparison |
| 30 | Month-1 retro vs targets (10 listings, 5-10 sales, 3+ reviews, keyword data). Write month-2 build order | Retro + plan | 2h | This repo | Honest LOW/BASE/HIGH read + next 10 builds chosen |

## Non-negotiables throughout
- Reply to every message <24h from day 9.
- No listing skips QA. No fake urgency, no fake reviews, no keyword-stuffed titles.
- Log everything in the production register: month 2 decisions are data decisions.
