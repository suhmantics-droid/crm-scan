"""Console, CSV and JSON output for scan results."""

import csv
import json
import os
import sys


def _color(code, text):
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def render_console(result, labels, show_evidence=False):
    lines = []
    header = f"{result.domain or result.company}"
    tag = "" if result.method == "page+dns" else f"  [{result.method}]"
    if not result.findings:
        lines.append(f"{header} -> {_color('90', '(nothing found)')}{tag}")
        return "\n".join(lines)

    lines.append(f"{_color('1', header)}{tag}")
    grouped = result.by_category()
    for cat, label in labels.items():
        findings = grouped.get(cat)
        if not findings:
            continue
        names = []
        for f in findings:
            mark = "" if f.confidence == "confirmed" else " ~"
            names.append(f"{f.vendor.name}{mark}")
        lines.append(f"  {label:<24} {_color('32', ', '.join(names))}")
        if show_evidence:
            for f in findings:
                for ev in f.evidence:
                    lines.append(_color("90", f"      {f.vendor.name}: {ev}"))
    if result.unknowns:
        lines.append(f"  {'Unmatched signals':<24} {_color('33', ', '.join(result.unknowns))}")
    return "\n".join(lines)


def to_json(results, labels):
    docs = []
    for r in results:
        docs.append({
            "company": r.company,
            "domain": r.domain,
            "method": r.method,
            "vendors": [
                {
                    "name": f.vendor.name,
                    "category": f.vendor.category,
                    "confidence": f.confidence,
                    "channels": sorted(f.channels),
                    "evidence": f.evidence,
                }
                for f in r.findings
            ],
            "unmatched_signals": r.unknowns,
        })
    return json.dumps({"labels": labels, "results": docs}, indent=2)


def write_csv(results, labels, path):
    """One row per domain, one column per category. '~' marks a vendor seen
    only on the page (tags can linger); unmarked vendors are DNS/header/IP
    confirmed."""
    fields = ["Company", "Domain"] + list(labels.values()) + ["Unmatched", "Method"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in results:
            row = {"Company": r.company, "Domain": r.domain,
                   "Unmatched": ", ".join(r.unknowns), "Method": r.method}
            grouped = r.by_category()
            for cat, label in labels.items():
                names = []
                for f in grouped.get(cat, []):
                    mark = "" if f.confidence == "confirmed" else " ~"
                    names.append(f"{f.vendor.name}{mark}")
                row[label] = ", ".join(names)
            w.writerow(row)
