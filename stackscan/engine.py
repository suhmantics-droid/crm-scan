"""The scan itself: gather public signals for a domain, match fingerprints.

Two layers, same as crm-scan.ps1:

  DNS   - SPF includes, DKIM selector CNAMEs, DMARC rua, MX, NS, plus CNAMEs
          on the service subdomains where SaaS vendors live (help., status.,
          careers., login., ...). All confirmed infrastructure.
  PAGE  - one homepage GET for JS tags (and the GTM containers it loads),
          plus response headers and apex A records for platform detection.

Anything unrecognised and not generic plumbing is surfaced rather than
silently dropped - that is how a vendor with no fingerprint yet gets
discovered and added to the database.
"""

import ipaddress
import re
from concurrent.futures import ThreadPoolExecutor

# Marketing-mail subdomains worth probing for SPF/CNAME. Trimmed to the
# productive ones (from crm-scan): the long tail roughly doubles DNS time
# and rarely adds a platform.
EMAIL_SUBS = ("email", "e", "mail", "news", "marketing", "mkt", "edm", "go",
              "links", "hello", "m", "info")

DKIM_SELECTORS = ("k1", "k2", "kl", "dkim", "dkim1", "selector1", "selector2",
                  "mte1", "dd", "ometria", "default", "s1", "s2", "google",
                  "mandrill")

# Service subdomains are the generalization beyond email: help.brand.com
# CNAMEs to brand.zendesk.com, careers.brand.com to boards.greenhouse.io,
# status.brand.com to statuspage.io. One CNAME query each.
SERVICE_SUBS = ("help", "support", "status", "careers", "jobs", "login",
                "sso", "auth", "id", "account", "autodiscover", "shop",
                "my", "app", "community", "blog")

# Sending prefixes stripped to recover the brand domain:
# email.brand.co.uk -> brand.co.uk
PREFIXES = {"email", "e", "mail", "news", "updates", "marketing", "go",
            "links", "m", "enews", "emails", "mailing", "r1", "cmp", "edm",
            "info", "hello", "click", "message", "em", "comms", "newsletter",
            "www"}

# Residual plumbing excluded from the unknown-vendor catch-all. Most of the
# old crm-scan GENERIC list became real fingerprints in the database; what
# remains here is SPF syntax noise, registrars and shorteners.
NOISE_RX = re.compile(
    r"_spf|^all$|^spf[.-]|\.spf\.|dkim\.|domainkey|secureserver|godaddy|"
    r"domaincontrol|namecheap|ionos|\bovh\b|gandi|123-reg|register\.|"
    r"registrar|short\.io|bit\.ly|\.arpa$"
)

# Hosts on the page that are interesting enough to surface when unmatched
# (same heuristic as crm-scan, widened past loyalty into the new categories).
PAGE_UNKNOWN_KEEP = re.compile(
    r"loyal|reward|review|personali|cdp|engage|wallet|subscrib|retention|"
    r"sms|checkout|payment|analytic|chat|widget|track|convert"
)
PAGE_UNKNOWN_DROP = re.compile(
    r"google|gstatic|facebook|jquery|doubleclick|cookiebot|onetrust|youtube|"
    r"jsdelivr|cloudfront|cloudflare|bootstrap|unpkg|polyfill|fontawesome"
)

CONFIRMED_CHANNELS = {"dns", "mx", "ns", "headers", "ip"}


class Finding:
    def __init__(self, vendor):
        self.vendor = vendor  # Vendor object (name, category, label, shared)
        self.channels = set()
        self.evidence = []  # human-readable, capped

    @property
    def confidence(self):
        return "confirmed" if self.channels & CONFIRMED_CHANNELS else "observed"


class DomainResult:
    def __init__(self, company, domain, method):
        self.company = company
        self.domain = domain
        self.method = method
        self.findings = []
        self.unknowns = []

    def by_category(self):
        """{category: [Finding, ...]} preserving database vendor order."""
        out = {}
        for f in self.findings:
            out.setdefault(f.vendor.category, []).append(f)
        return out


def resolve_brand_domain(company, raw):
    """Recover the registrable brand domain from a company name or raw value."""
    def clean(s):
        s = (s or "").strip().lower()
        s = re.sub(r"^https?://", "", s).split("/")[0]
        return s

    def is_domain(s):
        return bool(re.fullmatch(r"[a-z0-9][a-z0-9.-]*\.[a-z]{2,}", s or ""))

    cand = next((c for c in (clean(raw), clean(company)) if is_domain(c)), "")
    while cand:
        labels = cand.split(".")
        if len(labels) >= 3 and labels[0] in PREFIXES:
            cand = ".".join(labels[1:])
        else:
            break
    return cand


def _collect_dns(domain, resolver, workers):
    """Fan out every DNS probe, return the per-channel signal texts."""
    jobs = [("apex_txt", domain, "TXT"),
            ("mx", domain, "MX"),
            ("ns", domain, "NS"),
            ("a", domain, "A"),
            ("dmarc", f"_dmarc.{domain}", "TXT")]
    for sub in EMAIL_SUBS:
        jobs.append(("sub_txt", f"{sub}.{domain}", "TXT"))
        jobs.append(("cname", f"{sub}.{domain}", "CNAME"))
    for sub in SERVICE_SUBS:
        jobs.append(("cname", f"{sub}.{domain}", "CNAME"))
    for sel in DKIM_SELECTORS:
        jobs.append(("cname", f"{sel}._domainkey.{domain}", "CNAME"))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        answers = list(pool.map(lambda j: (j, resolver.query(j[1], j[2])), jobs))

    dns_texts, mx, ns, ips, cname_targets, spf_texts = [], [], [], [], [], []
    for (kind, name, _), rdata in answers:
        if not rdata:
            continue
        if kind in ("apex_txt", "sub_txt"):
            for s in rdata:
                if "spf" in s.lower():
                    dns_texts.append((f"SPF {name}", s))
                    spf_texts.append(s)
        elif kind == "dmarc":
            for s in rdata:
                dns_texts.append((f"DMARC {name}", s))
        elif kind == "cname":
            for target in rdata:
                dns_texts.append((f"CNAME {name}", target))
                cname_targets.append(target)
        elif kind == "mx":
            mx.extend((f"MX {name}", h) for h in rdata)
        elif kind == "ns":
            ns.extend((f"NS {name}", h) for h in rdata)
        elif kind == "a":
            ips.extend(rdata)

    # Expand SPF includes one level: the ESP's own record is where the
    # giveaway usually sits (include:_spf.klaviyo.com names the vendor even
    # when the brand's record does not).
    includes = []
    for s in spf_texts:
        includes.extend(m.group(1) for m in re.finditer(r"include:([^\s]+)", s))
    includes = list(dict.fromkeys(includes))[:15]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        expanded = list(pool.map(lambda i: (i, resolver.query(i, "TXT")), includes))
    for inc, rdata in expanded:
        dns_texts.append((f"SPF include {inc}", inc))  # the include name itself signals
        for s in rdata:
            if "spf" in s.lower():
                dns_texts.append((f"SPF include {inc}", s))

    return {"dns": dns_texts, "mx": mx, "ns": ns, "ips": ips,
            "cname_targets": cname_targets, "includes": includes}


def _collect_page(domain, fetcher):
    """One homepage GET (www first), plus the GTM containers it references."""
    result = None
    for url in (f"https://www.{domain}", f"https://{domain}"):
        result = fetcher.fetch(url)
        if result and result.body:
            break
    if not result:
        return None

    texts = [("homepage", result.body)]
    # A GTM container often loads the martech the page itself never references.
    gtm_ids = list(dict.fromkeys(re.findall(r"GTM-[A-Z0-9]{4,}", result.body)))[:3]
    for gid in gtm_ids:
        js = fetcher.fetch(f"https://www.googletagmanager.com/gtm.js?id={gid}")
        if js and js.body:
            texts.append((f"GTM {gid}", js.body))
    return {"texts": texts, "headers": result.headers}


def _snippet(text, match, width=34):
    start = max(0, match.start() - width)
    frag = text[start:match.end() + width].replace("\n", " ").strip()
    return f"...{frag}..." if len(text) > len(frag) else frag


def _match(vendors, dns_sig, page_sig):
    findings = {}

    def hit(vendor, channel, evidence):
        f = findings.setdefault(vendor.name, Finding(vendor))
        f.channels.add(channel)
        if len(f.evidence) < 3:
            f.evidence.append(evidence)

    for v in vendors:
        for channel in ("dns", "mx", "ns"):
            for raw, rx in v.patterns.get(channel, []):
                for source, text in dns_sig[channel]:
                    m = rx.search(text.lower())
                    if m:
                        hit(v, channel, f"{source}: {_snippet(text.lower(), m)}")
                        break  # one evidence line per pattern is plenty
        for net in v.cidrs:
            for ip in dns_sig["ips"]:
                try:
                    if ipaddress.ip_address(ip) in net:
                        hit(v, "ip", f"A record {ip} in {net}")
                except ValueError:
                    continue
        if page_sig:
            for raw, rx in v.patterns.get("page", []):
                for source, text in page_sig["texts"]:
                    if rx.search(text.lower()):
                        hit(v, "page", f"{source} matches /{raw}/")
                        break
            for hname, raw, rx in v.headers:
                val = page_sig["headers"].get(hname)
                if val and rx.search(val.lower()):
                    hit(v, "headers", f"header {hname}: {val[:60]}")

    # Shared infrastructure (SparkPost et al.) adds nothing once a real
    # vendor in the same category is identified.
    named = {f.vendor.category for f in findings.values() if not f.vendor.shared}
    return [f for f in findings.values()
            if not (f.vendor.shared and f.vendor.category in named)]


def _surface_unknowns(dns_sig, page_sig, domain, vendors):
    """Signals nothing in the database explains - the discovery mechanism."""
    dns_rx = [rx for v in vendors
              for ch in ("dns", "mx", "ns")
              for _, rx in v.patterns.get(ch, [])]
    unknowns = []
    for cand in dns_sig["includes"] + dns_sig["cname_targets"]:
        c = cand.lower().rstrip(".")
        if not c or domain in c or NOISE_RX.search(c):
            continue
        if any(rx.search(c) for rx in dns_rx):
            continue
        unknowns.append(c)

    if page_sig:
        page_rx = [rx for v in vendors for _, rx in v.patterns.get("page", [])]
        html = page_sig["texts"][0][1].lower()
        for m in re.finditer(r'src="https?://([^/"]+)', html):
            host = m.group(1)
            if not PAGE_UNKNOWN_KEEP.search(host):
                continue
            if PAGE_UNKNOWN_DROP.search(host) or domain in host:
                continue
            if any(rx.search(host) for rx in page_rx):
                continue
            unknowns.append(host)

    return list(dict.fromkeys(unknowns))[:6]


def scan_domain(company, domain, vendors, resolver, fetcher=None, workers=12):
    """Scan one domain. fetcher=None means DNS layer only."""
    dns_sig = _collect_dns(domain, resolver, workers)
    page_sig = _collect_page(domain, fetcher) if fetcher else None

    if fetcher is None:
        method = "dns-only"
    elif page_sig is None:
        method = "dns-only (page blocked)"
    else:
        method = "page+dns"

    result = DomainResult(company, domain, method)
    result.findings = _match(vendors, dns_sig, page_sig)
    result.unknowns = _surface_unknowns(dns_sig, page_sig, domain, vendors)
    return result
