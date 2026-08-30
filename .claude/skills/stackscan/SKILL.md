---
name: stackscan
description: Run and extend the stackscan vendor-stack scanner - scan domains for their SaaS vendor stack, add new vendor fingerprints, validate the fingerprint database, run the offline test suite. Use when asked to scan a domain, identify a company's vendors, or teach the scanner a new vendor.
---

# stackscan

Detects a company's vendor stack (commerce platform, ESP/CRM, payments,
analytics, support, mail infrastructure, hosting, corporate SaaS) from
public signals: DNS records and one homepage fetch. Stdlib-only Python,
no API keys, no LLM calls at scan time. The fingerprints live as data in
`fingerprints/*.json`; the engine lives in `stackscan/`.

## Running scans

```bash
python3 -m stackscan scan gymshark.com allbirds.com          # direct
python3 -m stackscan scan --input brands.csv --csv out.csv   # CSV in/out
python3 -m stackscan scan example.com --evidence             # show the matched records
python3 -m stackscan scan example.com --dns-only             # skip the page layer
python3 -m stackscan scan example.com --json out.json        # full detail + evidence
python3 -m stackscan list                                    # what the database knows
```

DNS goes over DNS-over-HTTPS (Cloudflare, then Google), so scans work
wherever HTTPS works. In sandboxes that block those hosts, only the
offline fixture mode is testable: `--fixtures tests/fixtures/acme`.

Output confidence: an unmarked vendor is **confirmed** (DNS/MX/NS/header/IP
- infrastructure the vendor had to be authorized into). A `~` suffix means
**observed** on the page only - JS tags can linger after a vendor is churned.

## Adding a vendor fingerprint (the discovery loop)

Never invent a fingerprint from memory. The scanner surfaces its own
training data - work from evidence:

1. Scan real domains. Anything unexplained appears under **Unmatched
   signals** (SPF includes, CNAME targets, interesting page hosts).
2. Identify which vendor an unmatched signal belongs to (check the
   hostname, the vendor's docs, or their SPF/DKIM setup guides).
3. Add the vendor to the right `fingerprints/*.json` file. Patterns are
   lowercase regex matched against lowercased text. Prefer `dns`/`mx`/`ns`
   signals (confirmed) over `page` (observed). Keep patterns specific
   enough not to match English prose in HTML - `"gladly\\.com"`, never
   `"gladly"`.
4. Validate and test: `python3 -m stackscan validate && python3 -m unittest`.
5. Re-scan the domain that surfaced the signal and confirm the vendor now
   appears with sensible evidence (`--evidence`).

Channels per vendor: `dns` (SPF/CNAME/DMARC text), `mx`, `ns`, `page`,
`headers` ({header-name: regex}), `ip_cidr` (CIDR list). `"shared": true`
marks resold infrastructure (e.g. SparkPost) that is suppressed when a
named vendor in the same category also matched.

New category = new JSON file with `category`, `label`, `order`, `vendors`.

## Before committing

`python3 -m stackscan validate` must print OK and `python3 -m unittest`
must pass. If engine behavior changed, extend the fixtures under
`tests/fixtures/acme/` rather than adding network-dependent tests - the
suite must stay runnable offline.
