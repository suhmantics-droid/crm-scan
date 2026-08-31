# Production SOP: from spec to shippable product

Dated 2026-08-31. Target: engine products 2-3 days, vertical skins 1 day, entry products 0.5 day.

## 1. Spec (human, 30-60 min)
Write the vertical spec: audience; jobs-to-be-done; tabs; fields with types/dropdowns; every calculation WITH a worked example (input → expected output); demo persona (name-free realistic business, e.g. "mobile groomer, 60 clients, £38 average groom"); copy angle; primary keyword.

## 2. Build (Claude Code session)
- Sheets build: structure generated, then formulas; named ranges for anything referenced twice; data validation on every enterable column; protected ranges on all non-input cells; input cells styled (three-colour convention: input/calculated/reference).
- Excel build: generated separately via openpyxl from the same spec (NOT exported from Sheets: exports break validation/protection). Feature parity checklist run.
- Demo data: loaded copy for screenshots; a clean copy for delivery; both generated from the spec.

## 3. Package
- Quick-start PDF (1-2 pages) from the template: which file to open, cell colours, weekly routine, video link, support promise.
- Walkthrough video (human, ≤12 min, Loom/OBS): setup → weekly entry → the payoff view.
- Delivery zip per format + instructions insert. Etsy digital limits: keep each file ≤20MB, ≤5 files per listing (use a PDF with links if ever exceeded).

## 4. Verify
Run qa-sop.md in full. No listing without a passed checklist logged in the production register.

## 5. List
Listing built per research/seo.md SOP + listings/image-briefs.md. Draft in the listing-master.csv row first, then into Etsy.

## 6. Version + register
- Product version vX.Y in the file's Settings tab footer and the register.
- Register row: product, version, spec hash, QA date, licence register refs (fonts/mockups), listing URL, launch date.
- Updates: fix → bump version → replace listing file → message recent buyers if the fix matters ("your file has been updated, re-download for free").

## Weekly operating rhythm (target ≤10 h/wk after launch month)
- Mon (1h): stats review: views/favourites/conversion per listing; pick the week's 2-3 builds.
- Tue-Thu (2h/day): build + list per this SOP.
- Fri (1h): support sweep, review responses, Pinterest scheduling for the week.
- Season exception: Dec-Jan support and content get daily 30-min sweeps.
