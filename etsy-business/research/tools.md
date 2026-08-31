# Free tool stack

Dated 2026-08-31. Paid tools only where the free path genuinely fails.

| Tool | URL | Purpose | Free tier | Limit | Best use | API | Automation potential |
|---|---|---|---|---|---|---|---|
| Etsy Search Analytics / Marketplace Insights | etsy.com (Seller Dashboard) | First-party keyword volumes + conversion | Free with shop | Needs open shop | Weekly keyword validation; replaces every third-party guess | No | Low |
| Etsy Shop Stats | Seller Dashboard | Views, visits, conversion per listing | Free | n/a | Kill/scale decisions per listing | No | Low |
| Etsy Share & Save | help.etsy.com | 4% fee reduction on self-driven traffic | Free | Links only | Wrap every external link | No | Medium |
| eRank | erank.com | Etsy keyword volume/competition estimates | Free plan | Limited lookups/day | Tag bank building; trend reports (their blog is free) | No | Low |
| Google Trends | trends.google.com | Directional demand, seasonality | Free | Relative data only | Validate seasonality windows (Jan tax, Apr new tax year) | Unofficial | Medium |
| Google Keyword Planner | ads.google.com | Google-side volumes for descriptions/Pinterest | Free w/ account | Ranges without spend | Long-tail description keywords | Yes | Medium |
| Google Sheets | sheets.google.com | Product format #1 + ops tracking | Free | n/a | Products, keyword DB, order log | Yes (Apps Script) | HIGH: Apps Script for demo data, protection, versioning |
| LibreOffice / Excel (existing licence) | libreoffice.org | Product format #2 (.xlsx) | Free | Feature parity quirks | Native Excel builds; test both engines | Scripts | HIGH via Claude Code + openpyxl |
| Python + openpyxl/xlsxwriter (via Claude Code) | local | Programmatic spreadsheet generation & QA | Free | n/a | The production engine: variants, protection, tests | n/a | VERY HIGH |
| Canva Free | canva.com | Listing images, PDF guides, doc-style products | Free | Pro assets need link-delivery rules | Listing image system; quick-start PDFs | Limited | Medium |
| Photopea | photopea.com | PSD-grade mockup editing in browser | Free | Ads in UI | Hero mockups without Photoshop | No | Low |
| Figma Free | figma.com | Reusable listing-image template system | Free | 3 files | Image template library | Yes | Medium |
| CapCut / OBS | capcut.com / obsproject.com | Listing videos + walkthroughs | Free | Watermark care | 15-30s dashboard demos; product walkthrough videos | No | Medium |
| Loom Free | loom.com | Support/walkthrough videos | Free | 25 videos, 5 min | Buyer walkthroughs (5 min fits) | No | Low |
| Pinterest Business | pinterest.com | The digital-product discovery channel | Free | n/a | 3-5 pins/day from listing images; Share & Save links | Yes | HIGH (bulk pin from CSV) |
| Google Search Console + a simple landing page | search.google.com | Long-term off-Etsy SEO | Free | n/a | Phase 2 (Shopify/suhmantics decision) | Yes | Medium |
| HMRC guidance pages | gov.uk | Source of truth for categories/labels in UK products | Free | Not advice | Product accuracy; copy accuracy | No | n/a |
| ChatGPT/Claude (existing) | n/a | Copy drafts, variant generation, QA review | Existing | n/a | See ai-production-system.md | Yes | HIGH |
| Claude Code | this repo | The production line itself | Existing | n/a | Build, test, version every product; generate listing kits | n/a | VERY HIGH |

## Paid tools deliberately NOT adopted yet

- eRank Pro / EverBee / Sale Samurai (£5-25/mo): only if free eRank + Marketplace Insights prove insufficient after month 1.
- Etsy Ads: off until a listing proves organic conversion, then £1-3/day on winners only (see finance models; sub-£10 items never get ads).
- Adobe/office subscriptions: unnecessary; the stack above covers production.

Total required monthly tool spend at launch: £0. One-off: Etsy setup fee (~£15-25 REPORTED, confirm at signup) + listing fees (£0.15 each).
