"""CLI entry point: python3 -m stackscan {scan,validate,list}"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from . import __version__
from .dns_client import DohResolver, FixtureResolver
from .engine import resolve_brand_domain, scan_domain
from .fingerprints import DEFAULT_DB_DIR, bundle_db, load_db, validate_db
from .http_client import FixtureFetcher, HttpFetcher
from .report import render_console, to_json, write_csv


def _read_targets(args):
    if args.input:
        with open(args.input, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            sys.exit(f"input CSV is empty: {args.input}")
        cols = rows[0].keys()
        ccol = next((c for c in cols if c.lower().startswith("company")), None)
        dcol = next((c for c in cols if c.lower().startswith("domain")), None)
        if not ccol and not dcol:
            sys.exit(f"no Company or Domain column found; columns: {', '.join(cols)}")
        return [((r.get(ccol) or "").strip(), (r.get(dcol) or "").strip())
                for r in rows]
    return [(d, d) for d in args.domains]


def cmd_scan(args):
    categories = set(args.categories.split(",")) if args.categories else None
    vendors, labels = load_db(args.fingerprints, categories)

    if args.fixtures:
        fx = Path(args.fixtures)
        resolver = FixtureResolver(json.loads((fx / "dns.json").read_text()))
        fetcher = None if args.dns_only else FixtureFetcher(
            json.loads((fx / "http.json").read_text()))
    else:
        resolver = DohResolver(timeout=args.timeout)
        fetcher = None if args.dns_only else HttpFetcher(timeout=args.timeout)

    targets = _read_targets(args)
    # Dedupe before scanning. On one real list this collapsed 4,394 rows to
    # 1,015 unique domains.
    seen = {}
    results = []
    for n, (company, raw) in enumerate(targets, 1):
        domain = resolve_brand_domain(company, raw)
        if not domain:
            from .engine import DomainResult
            results.append(DomainResult(company, "", "needs-domain"))
            print(f"[{n}/{len(targets)}] {company} -> no resolvable domain")
            continue
        if domain in seen:
            results.append(seen[domain])
            continue
        result = scan_domain(company, domain, vendors, resolver, fetcher,
                             workers=args.workers)
        seen[domain] = result
        results.append(result)
        print(f"[{n}/{len(targets)}] ", end="")
        print(render_console(result, labels, show_evidence=args.evidence))
        if args.delay:
            time.sleep(args.delay)

    if args.csv:
        write_csv(results, labels, args.csv)
        print(f"\nWritten to {args.csv}")
    if args.json:
        Path(args.json).write_text(to_json(results, labels), encoding="utf-8")
        print(f"Written to {args.json}")

    found = sum(1 for r in results if r.findings)
    print(f"\nScanned {len(targets)} rows, {len(seen)} unique domains. "
          f"Vendors identified on {found}.")


def cmd_validate(args):
    problems = validate_db(args.fingerprints)
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    vendors, labels = load_db(args.fingerprints)
    print(f"OK: {len(vendors)} vendors across {len(labels)} categories.")


def cmd_list(args):
    categories = set(args.categories.split(",")) if args.categories else None
    vendors, labels = load_db(args.fingerprints, categories)
    for cat, label in labels.items():
        names = [v.name + (" (shared)" if v.shared else "")
                 for v in vendors if v.category == cat]
        print(f"{label} ({cat}): {len(names)}")
        print(f"  {', '.join(names)}")


def cmd_benchmark(args):
    """Score the scanner against domains whose stacks are known.

    The truth CSV has Domain and Vendors columns; Vendors is
    semicolon-separated. A vendor prefixed with ! is a known ABSENCE
    (detecting it is a hard false positive). Vendors detected but not
    listed are reported as unverified extras for a human to judge, not
    counted as errors - a truth file is rarely exhaustive.
    """
    vendors, labels = load_db(args.fingerprints)
    if args.fixtures:
        fx = Path(args.fixtures)
        resolver = FixtureResolver(json.loads((fx / "dns.json").read_text()))
        fetcher = None if args.dns_only else FixtureFetcher(
            json.loads((fx / "http.json").read_text()))
    else:
        resolver = DohResolver(timeout=args.timeout)
        fetcher = None if args.dns_only else HttpFetcher(timeout=args.timeout)

    with open(args.truth, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows or "Domain" not in rows[0] or "Vendors" not in rows[0]:
        sys.exit("truth CSV needs Domain and Vendors columns "
                 "(Vendors semicolon-separated, ! prefix = known absent)")

    hits = misses = violations = 0
    extras_all = []
    for row in rows:
        domain = resolve_brand_domain("", row["Domain"])
        expected, forbidden = set(), set()
        for v in row["Vendors"].split(";"):
            v = v.strip()
            if not v:
                continue
            (forbidden if v.startswith("!") else expected).add(v.lstrip("!"))

        result = scan_domain("", domain, vendors, resolver, fetcher,
                             workers=args.workers)
        found = {f.vendor.name: f for f in result.findings}

        for name in sorted(expected):
            if name in found:
                hits += 1
            else:
                misses += 1
                print(f"MISS  {domain}: {name} not detected")
        for name in sorted(forbidden):
            if name in found:
                violations += 1
                ev = "; ".join(found[name].evidence)
                print(f"FALSE {domain}: {name} detected but known absent ({ev})")
        extras = sorted(set(found) - expected - forbidden)
        if extras:
            extras_all.append(f"  {domain}: {', '.join(extras)}")
        if args.delay:
            time.sleep(args.delay)

    total = hits + misses
    print(f"\nRecall: {hits}/{total} known vendors detected"
          + (f" ({hits / total:.0%})" if total else ""))
    print(f"Hard false positives (known-absent detected): {violations}")
    if extras_all:
        print("Unverified extras (judge these by hand; each one is either "
              "a win or a fingerprint bug):")
        print("\n".join(extras_all))
    if misses or violations:
        sys.exit(1)


def cmd_bundle(args):
    out = Path(args.out)
    out.write_text(json.dumps(bundle_db(args.fingerprints), indent=1) + "\n",
                   encoding="utf-8")
    print(f"Written to {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="stackscan",
        description="Detect a company's vendor stack from public signals: "
                    "DNS records and one page fetch. No API keys, no LLM calls.")
    ap.add_argument("--version", action="version", version=__version__)
    ap.add_argument("--fingerprints", default=str(DEFAULT_DB_DIR),
                    help="fingerprint database directory")
    sub = ap.add_subparsers(dest="command", required=True)

    sc = sub.add_parser("scan", help="scan one or more domains")
    sc.add_argument("domains", nargs="*", help="domains to scan")
    sc.add_argument("--input", help="CSV with Company and/or Domain columns")
    sc.add_argument("--csv", help="write results to this CSV")
    sc.add_argument("--json", help="write full results (with evidence) to JSON")
    sc.add_argument("--dns-only", action="store_true",
                    help="skip the page layer: faster, quieter")
    sc.add_argument("--categories", help="comma-separated category filter")
    sc.add_argument("--evidence", action="store_true",
                    help="print the matched record behind each vendor")
    sc.add_argument("--delay", type=float, default=0,
                    help="seconds between domains; be polite on long lists")
    sc.add_argument("--workers", type=int, default=12,
                    help="parallel DNS queries per domain")
    sc.add_argument("--timeout", type=int, default=15)
    sc.add_argument("--fixtures", help="offline mode: directory with dns.json "
                                       "and http.json (for tests)")
    sc.set_defaults(func=cmd_scan)

    va = sub.add_parser("validate", help="lint the fingerprint database")
    va.set_defaults(func=cmd_validate)

    ls = sub.add_parser("list", help="show vendors in the database")
    ls.add_argument("--categories", help="comma-separated category filter")
    ls.set_defaults(func=cmd_list)

    bu = sub.add_parser("bundle",
                        help="regenerate the web scanner's fingerprint bundle")
    bu.add_argument("--out", default="web/fingerprints.json")
    bu.set_defaults(func=cmd_bundle)

    be = sub.add_parser("benchmark",
                        help="score the scanner against known-stack domains")
    be.add_argument("--truth", required=True,
                    help="CSV with Domain,Vendors (semicolon-separated; "
                         "! prefix marks a known-absent vendor)")
    be.add_argument("--dns-only", action="store_true")
    be.add_argument("--delay", type=float, default=0)
    be.add_argument("--workers", type=int, default=12)
    be.add_argument("--timeout", type=int, default=15)
    be.add_argument("--fixtures", help="offline mode (for tests)")
    be.set_defaults(func=cmd_benchmark)

    args = ap.parse_args(argv)
    if args.command == "scan" and not args.domains and not args.input:
        ap.error("give domains to scan, or --input a CSV")
    args.func(args)


if __name__ == "__main__":
    main()
