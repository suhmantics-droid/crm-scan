"""Load and validate the fingerprint database under fingerprints/.

Each JSON file is one category. A vendor is a name plus signal patterns on
one or more channels:

    dns        regex against SPF strings, CNAME targets and DMARC records
    mx         regex against the apex MX hosts
    ns         regex against the apex nameservers
    page       regex against URLs extracted from the homepage (script srcs,
               links, loader snippets) and any GTM containers it loads.
               URL-only on purpose: cookie-consent banners and blog posts
               mention vendor NAMES in prose ("we accept Klarna"), and a
               name in prose is not evidence. A vendor's asset URL is.
    page_text  regex against the raw HTML, for the few signatures that are
               markup rather than a URL (window.Shopify). Use sparingly.
    headers    {header-name: regex} against homepage response headers
    ip_cidr    CIDR ranges checked against the apex A records

Patterns are matched against lowercased text; write them lowercase. dns/mx/
ns/headers/ip hits are 'confirmed' (infrastructure the vendor had to be
authorized into); page hits are 'observed' (tags can linger after churn).

"shared": true marks infrastructure several vendors resell (e.g. SparkPost).
A shared vendor is dropped from a category when a non-shared vendor in the
same category also matched, because the ambiguous tag adds nothing.
"""

import ipaddress
import json
import re
from pathlib import Path

CHANNELS = ("dns", "mx", "ns", "page", "page_text")
VENDOR_KEYS = set(CHANNELS) | {"name", "headers", "ip_cidr", "shared", "notes"}

DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent / "fingerprints"


class Vendor:
    def __init__(self, name, category, label):
        self.name = name
        self.category = category
        self.label = label
        self.shared = False
        self.patterns = {}  # channel -> [(raw, compiled)]
        self.headers = []  # [(header-name, raw, compiled)]
        self.cidrs = []  # [ip_network]


def load_db(db_dir=None, categories=None):
    """Return (vendors, labels) where labels is {category: label} in display order."""
    db_dir = Path(db_dir or DEFAULT_DB_DIR)
    vendors, meta = [], []
    for path in sorted(db_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        cat = doc["category"]
        if categories and cat not in categories:
            continue
        meta.append((doc.get("order", 999), cat, doc.get("label", cat)))
        for entry in doc["vendors"]:
            v = Vendor(entry["name"], cat, doc.get("label", cat))
            v.shared = bool(entry.get("shared"))
            for ch in CHANNELS:
                pats = entry.get(ch, [])
                if pats:
                    v.patterns[ch] = [(p, re.compile(p)) for p in pats]
            for hname, pat in entry.get("headers", {}).items():
                v.headers.append((hname.lower(), pat, re.compile(pat)))
            for cidr in entry.get("ip_cidr", []):
                v.cidrs.append(ipaddress.ip_network(cidr))
            vendors.append(v)
    labels = {cat: label for _, cat, label in sorted(meta)}
    return vendors, labels


def bundle_db(db_dir=None):
    """Combine the category files into one document for the web scanner.

    Vendors pass through untouched so web/app.js reads the same keys the
    Python engine does. Sorted by display order, same as load_db.
    """
    db_dir = Path(db_dir or DEFAULT_DB_DIR)
    categories = []
    for path in sorted(db_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        categories.append(doc)
    categories.sort(key=lambda d: d.get("order", 999))
    return {"source": "fingerprints/", "categories": categories}


def validate_db(db_dir=None):
    """Lint the database; returns a list of problem strings (empty = clean)."""
    db_dir = Path(db_dir or DEFAULT_DB_DIR)
    problems = []
    seen_names = {}
    files = sorted(db_dir.glob("*.json"))
    if not files:
        return [f"no fingerprint files found in {db_dir}"]

    for path in files:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{path.name}: invalid JSON ({e})")
            continue
        for key in ("category", "label", "vendors"):
            if key not in doc:
                problems.append(f"{path.name}: missing '{key}'")
        for entry in doc.get("vendors", []):
            name = entry.get("name", "<unnamed>")
            where = f"{path.name} / {name}"
            if "name" not in entry:
                problems.append(f"{path.name}: vendor without a name")
            if name in seen_names:
                problems.append(f"{where}: duplicate of vendor in {seen_names[name]}")
            seen_names[name] = path.name

            unknown = set(entry) - VENDOR_KEYS
            if unknown:
                problems.append(f"{where}: unknown keys {sorted(unknown)}")

            has_signal = False
            for ch in CHANNELS:
                for pat in entry.get(ch, []):
                    has_signal = True
                    if pat != pat.lower():
                        problems.append(f"{where}: pattern '{pat}' is not lowercase")
                    try:
                        re.compile(pat)
                    except re.error as e:
                        problems.append(f"{where}: bad regex '{pat}' ({e})")
            for hname, pat in entry.get("headers", {}).items():
                has_signal = True
                try:
                    re.compile(pat)
                except re.error as e:
                    problems.append(f"{where}: bad header regex '{pat}' ({e})")
            for cidr in entry.get("ip_cidr", []):
                has_signal = True
                try:
                    ipaddress.ip_network(cidr)
                except ValueError as e:
                    problems.append(f"{where}: bad CIDR '{cidr}' ({e})")
            if not has_signal:
                problems.append(f"{where}: no signals on any channel")
    return problems
