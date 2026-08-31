# QA SOP: nothing fragile ships

Dated 2026-08-31. Rationale: the category's #1 documented complaint is broken/fragile files (research/review-mining.md). QA is the brand.

## A. Automated checks (Claude Code script, both formats)
- [ ] Every calculation in the spec reproduces its worked example exactly (Sheets AND Excel)
- [ ] Cross-format parity: same inputs → same outputs to 2dp on every calculated cell
- [ ] No #REF!/#DIV/0!/#N/A anywhere, including with empty inputs and zero rows
- [ ] Every non-input cell is inside a protected range; every input cell is not
- [ ] All dropdowns/data validation fire; no orphan named ranges
- [ ] 500-row stress fill: no formula range cliffs (formulas cover the full table, not the first 50 rows)
- [ ] Dates behave as DD/MM; currency renders £; tax-year boundaries (5/6 April) bucket correctly

## B. Human "hostile buyer" pass (15 min)
- [ ] Open on a machine/account that has never seen the file; follow ONLY the quick-start PDF
- [ ] Try to break it: paste over a formula (blocked?), sort the table (survives?), delete a row (survives or clearly warns?), enter text in a number cell (validation message helpful?)
- [ ] Open the Excel file in LibreOffice (many UK buyers will): degrade gracefully?
- [ ] Phone check: dashboards readable on mobile Sheets app?
- [ ] Timer test: from download to first meaningful entry ≤15 minutes using only the guide

## C. Accuracy gate (finance products only)
- [ ] Every rate/threshold (mileage rates, tax bands, NI) checked against current gov.uk pages, with the source URL + checked-date recorded IN the file's reference tab
- [ ] Estimator assumptions stated on the tab itself, not just the listing
- [ ] Disclaimer present: records/planning tool, not tax advice; no "MTD compliant filing" claims

## D. Listing QA
- [ ] Screenshots match the shipping version (no stale images)
- [ ] Title/tags/description from listing-master.csv; banned words absent; AI disclosure set if applicable
- [ ] Test purchase download on a buyer account for listing #1 and any new delivery mechanism

## E. Licence register
Every third-party asset (font, mockup frame, icon set) logged: asset, source, licence type, URL, date. No unlogged asset ships.

## Failure rule
Any B-pass failure = fix and full re-run of A. Any post-launch buyer-reported break = same-day fix, version bump, free update message to buyers, and a new QA case added so it can never recur.
