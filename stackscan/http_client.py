"""One-page HTTP layer: ordinary GETs, the same traffic a browser makes."""

import gzip
import ssl
import urllib.error
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class FetchResult:
    def __init__(self, url, status, headers, body):
        self.url = url
        self.status = status
        # Header names lowercased so fingerprints match case-insensitively.
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.body = body


class HttpFetcher:
    def __init__(self, timeout=20):
        self.timeout = timeout
        self._ctx = ssl.create_default_context()

    def fetch(self, url):
        """GET a URL; None on any failure. Redirects are followed by urllib."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Encoding": "gzip",
            },
        )
        try:
            with urllib.request.urlopen(
                req, timeout=self.timeout, context=self._ctx
            ) as resp:
                raw = resp.read(4_000_000)  # a homepage, not a mirror job
                if resp.headers.get("Content-Encoding", "") == "gzip":
                    try:
                        raw = gzip.decompress(raw)
                    except OSError:
                        pass
                return FetchResult(
                    resp.geturl(),
                    resp.status,
                    dict(resp.headers.items()),
                    raw.decode("utf-8", "replace"),
                )
        except (urllib.error.URLError, OSError, ValueError):
            return None


class FixtureFetcher:
    """Offline fetcher for tests: URL -> {status, headers, body} dict."""

    def __init__(self, pages):
        self.pages = pages

    def fetch(self, url):
        page = self.pages.get(url)
        if not page:
            return None
        return FetchResult(
            url, page.get("status", 200), page.get("headers", {}), page.get("body", "")
        )
