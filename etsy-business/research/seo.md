# Etsy SEO: current mechanics (2026) and the repeatable listing framework

Dated 2026-08-31. Sources: 2026 SEO guides from tool vendors and platforms ([gelato.com](https://www.gelato.com/blog/etsy-seo-guide), [printify.com](https://printify.com/blog/etsy-seo-how-to-get-noticed-on-etsy/), [getbetterlisting.com titles](https://getbetterlisting.com/en/blog/etsy-title-seo-2026-formulas) and [tags](https://getbetterlisting.com/en/blog/etsy-tag-seo-best-practices), [listifyai.net](https://www.listifyai.net/blog/etsy-seo-guide-2026)); Etsy Seller Handbook for Share & Save ([etsy.com](https://www.etsy.com/seller-handbook/article/1187231088945)). Labels: REPORTED unless marked. Algorithm claims are vendor-reported, not Etsy-official; treat as best current practice, verify against Seller Handbook once the account exists.

## How ranking works now (2026 consensus)

1. **Query matching** across title, tags, categories, attributes, and (now) description keywords.
2. **Contextual relevance**: the algorithm matches meaning, not just exact strings, and penalizes mismatch between what tags claim and what the listing/images actually are. REPORTED.
3. **Listing quality score**: CTR and conversion feed ranking; listings that convert rank better, compounding. REPORTED ([outfy.com](https://www.outfy.com/blog/etsy-conversion-rate/)).
4. **Customer experience score**: reviews, completed about section, policies, response times.
5. Digital products skip the shipping-price factor entirely: one structural advantage.

## The framework (apply to every listing)

### Title (140 chars, first ~40 weighted most)
Formula: `[Primary keyword, natural phrasing] | [Secondary keyword + qualifier] | [Audience or use keyword]`
- Front-load the exact primary search phrase; natural language, no filler adjectives, no repeated phrases.
- Example (ours): `UK Sole Trader Bookkeeping Spreadsheet | Self Assessment Tax Tracker Google Sheets & Excel | Self Employed Accounts Template`

### Tags (all 13, multi-word)
- 2-4 word phrases; no single words; expand reach beyond the title rather than repeating it verbatim; cover: audience ("sole trader uk"), problem ("self assessment help"), format ("google sheets template"), occasion/season ("tax year 2026 27"), synonyms ("self employed accounts").
- Keep a tag bank per product family in keywords.csv; rotate underperformers quarterly using Etsy stats.

### Category and attributes
- Deepest matching category (they act as extra tags). Digital download attributes set precisely; AI-assistance disclosure where applicable.

### Description
- First 2 sentences: primary keyword + what it is + who it is for (Etsy now indexes descriptions; Google indexes them fully).
- Then scannable blocks: WHAT'S INSIDE / HOW IT WORKS (3 steps) / FORMATS & REQUIREMENTS / FAQ / SUPPORT PROMISE. This mirrors what converts in the category and feeds Google long-tail.

### Images (the conversion engine; 8-10 per listing)
1. Hero mockup: product on a laptop/phone frame, benefit headline, UK flag cue where relevant.
2. "What's included" grid.
3. Dashboard close-up with real-looking data.
4. 3-step "how it works".
5. Feature callouts (locked formulas, both formats, video guide).
6. Social proof / support promise card.
7. FAQ card. 8. Year/edition badge.
- **Video on every listing** (15-30s screen capture of the dashboard updating). Etsy reports video lifts conversion; digital buyers need to see the thing working. REPORTED.

### Reviews
- Follow-up message sequence (allowed: thank-you + help offer; never incentivized reviews). Fast support turns problems into 5★ (see review-mining.md).

### Pricing and SEO
- Do not compete at £3-5: fixed fees eat it, conversion-quality buyers distrust it in this category, and ads can never pay there. £9.99+ singles, £24.99+ bundles.

### New listings cadence
- Steady drip (2-3/week) beats bulk dumps: each new listing is a fresh search entry; consistent shop activity correlates with search favor. REPORTED/ANECDOTAL.

### Share & Save (fee-side SEO)
- Every external link we post (Pinterest, TikTok bio, blog) uses the Share & Save link: 6.5% transaction fee drops to 2.5% on those sales. VERIFIED (Etsy handbook + help pages).

## Listing SOP checklist (copy into every listing build)

- [ ] Primary keyword chosen from keywords.csv (buyer intent, not browse)
- [ ] Title formula applied; primary phrase in first 40 chars
- [ ] 13 multi-word tags from the family tag bank; no title duplicates beyond the core phrase
- [ ] Deepest category + all attributes + AI disclosure if applicable
- [ ] Description: 2 keyword-rich opening sentences + WHAT'S INSIDE / HOW IT WORKS / FORMATS / FAQ / SUPPORT
- [ ] 8+ images per the image-briefs.md system, 1 video
- [ ] Both file formats attached (or link-PDF for Canva/Notion products) + quick-start PDF
- [ ] Price checked against family price ladder
- [ ] Share & Save link generated and stored in content calendar
