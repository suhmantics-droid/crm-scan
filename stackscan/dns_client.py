"""DNS lookups over DNS-over-HTTPS.

DoH instead of the system resolver for two reasons: it works identically on
every OS with nothing installed, and it keeps working in locked-down
environments (CI, containers, corporate proxies) where raw port-53 DNS is
blocked but HTTPS is not. Proxies are honored via the standard HTTPS_PROXY
environment variable, which urllib reads on its own.
"""

import json
import ssl
import threading
import urllib.error
import urllib.parse
import urllib.request

TYPE_CODES = {"A": 1, "NS": 2, "CNAME": 5, "MX": 15, "TXT": 16}

# Both providers speak the same JSON dialect. Cloudflare requires the accept
# header; Google ignores it. Order is a preference, not a ranking claim.
PROVIDERS = {
    "cloudflare": "https://cloudflare-dns.com/dns-query?",
    "google": "https://dns.google/resolve?",
}


class DohResolver:
    """Resolves names via DoH JSON, with an in-memory cache per process."""

    def __init__(self, providers=("cloudflare", "google"), timeout=8):
        self.providers = [PROVIDERS[p] for p in providers]
        self.timeout = timeout
        self._cache = {}
        self._lock = threading.Lock()
        self._ctx = ssl.create_default_context()

    def query(self, name, rtype):
        """Return rdata strings for (name, rtype); [] on NXDOMAIN or error.

        TXT strings are unquoted and re-joined (long records arrive split).
        CNAME/NS/MX targets lose their trailing dot; MX loses its preference.
        """
        key = (name.lower(), rtype)
        with self._lock:
            if key in self._cache:
                return self._cache[key]

        result = []
        params = urllib.parse.urlencode({"name": name, "type": rtype})
        for base in self.providers:
            try:
                req = urllib.request.Request(
                    base + params, headers={"accept": "application/dns-json"}
                )
                with urllib.request.urlopen(
                    req, timeout=self.timeout, context=self._ctx
                ) as resp:
                    payload = json.loads(resp.read().decode("utf-8", "replace"))
                result = self._extract(payload, rtype)
                break
            except (urllib.error.URLError, OSError, ValueError):
                continue  # next provider; both failing means no answer

        with self._lock:
            self._cache[key] = result
        return result

    @staticmethod
    def _extract(payload, rtype):
        want = TYPE_CODES[rtype]
        out = []
        for ans in payload.get("Answer") or []:
            if ans.get("type") != want:
                continue  # A queries also return the CNAME chain; skip it
            data = ans.get("data", "")
            if rtype == "TXT":
                # '"part one" "part two"' -> 'part onepart two'
                parts = [p for p in data.split('"') if p and p != " "]
                data = "".join(parts)
            elif rtype == "MX":
                data = data.split()[-1]
            out.append(data.rstrip("."))
        return out


class FixtureResolver:
    """Offline resolver for tests: answers come from a recorded dict.

    Keys are 'TYPE:name' (e.g. 'TXT:email.brand.com'), values are lists of
    rdata strings in the same shape DohResolver returns.
    """

    def __init__(self, records):
        self.records = {k.lower(): v for k, v in records.items()}

    def query(self, name, rtype):
        return list(self.records.get(f"{rtype}:{name}".lower(), []))
