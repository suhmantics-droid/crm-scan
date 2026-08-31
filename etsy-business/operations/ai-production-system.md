# AI production system

Dated 2026-08-31. Governing rule: AI is the factory, the operator is the designer and QA. Etsy policy (research/etsy-policy.md): AI-assisted work is allowed; disclosure is required where AI-generated content ships in the product; prompt packs are excluded entirely; everything must be genuinely our original design.

## What AI legitimately does here (and what it must not)

| Stage | AI does | AI must NOT |
|---|---|---|
| Ideation/research | Cluster keywords, summarize competitor patterns, draft segment maps | Invent demand numbers (everything sourced or UNKNOWN: the rule this repo already follows) |
| Product build | Via Claude Code: generate spreadsheet structure + formulas with openpyxl/Apps Script, generate both formats from one spec, generate demo data, run the QA test suite | Ship an unreviewed formula: every calculation hand-verified against a worked example before listing |
| Copy | Draft listings from the copy bank (mined customer language), draft guides, draft chase-email scripts | Publish AI-scented filler; the banned-words list lives in listing-copy.md rules |
| Design | Generate layout specs; batch-produce image text variants | Generate fake "customer photos" or fake reviews (policy + ethics) |
| Variants | Skin engines into verticals (fields, categories, demo data, copy) from a vertical spec file | Change engine maths per-vertical without re-running QA |
| Support | Draft replies from the FAQ; nightly summary of new messages | Auto-send anything: human sends every reply |
| Analytics | Monthly listing-performance table from Etsy stats CSV export; prune/scale recommendations | Act on its own recommendations without review |

## Disclosure practice

- Spreadsheet products where AI assisted construction but every formula/structure is operator-designed and verified: honest description line: "Designed and tested by me; built with AI-assisted tooling." Mark Etsy's AI disclosure where the listing contains AI-generated content (e.g. any AI-written guide prose we keep). When in doubt, disclose: the cost of over-disclosure is ~zero, the cost of under-disclosure is the shop.

## The pipeline (one product, end to end)

1. **SPEC** (30-60 min, human): vertical spec YAML: audience, fields, categories, calculations with worked examples, demo persona.
2. **BUILD** (Claude Code): generate Sheets (Apps Script or manual from generated CSV/structure) + Excel (openpyxl): tabs, formulas, protection ranges, styling, demo data.
3. **VERIFY** (scripted + human): automated checks (formula parity across both formats against the worked examples, protection coverage, no broken refs) + human 15-minute "act like a buyer" pass per qa-sop.md.
4. **PACKAGE** (Claude Code + human): quick-start PDF from template, walkthrough video recorded by human (10 min), files zipped per format.
5. **LIST** (draft by AI, human finalizes): title/tags from keywords.csv, description from copy bank, images from the 8-slot system.
6. **LOG**: entry in the production register (product, version, date, QA checklist hash, licence register refs).

Throughput target once engines exist: one vertical SKU per ~1 working day; one entry SKU per half day.

## Repo note

This file system lives in a git repo already: product specs and generation scripts should live in a private repo (`/etsy-products/`, separate from this public research repo) so every product is versioned, diffable, and regenerable: that is the real moat of the production system.
