import json
import tempfile
import unittest
from pathlib import Path

from stackscan.dns_client import FixtureResolver
from stackscan.engine import resolve_brand_domain, scan_domain
from stackscan.fingerprints import load_db
from stackscan.http_client import FixtureFetcher
from stackscan.report import to_json, write_csv

FIX_ROOT = Path(__file__).parent / "fixtures"
FIXTURES = FIX_ROOT / "acme"


def scan_acme(dns_only=False):
    vendors, labels = load_db()
    resolver = FixtureResolver(json.loads((FIXTURES / "dns.json").read_text()))
    fetcher = None if dns_only else FixtureFetcher(
        json.loads((FIXTURES / "http.json").read_text()))
    result = scan_domain("Acme Outfitters", "acmeoutfitters.example",
                         vendors, resolver, fetcher)
    return result, labels


class TestBrandDomain(unittest.TestCase):
    def test_sending_prefixes_are_stripped(self):
        self.assertEqual(
            resolve_brand_domain("Gymshark", "email.gymshark.co.uk"),
            "gymshark.co.uk")

    def test_urls_are_cleaned(self):
        self.assertEqual(
            resolve_brand_domain("Allbirds", "https://www.allbirds.com/pages/x"),
            "allbirds.com")

    def test_company_name_is_not_a_domain(self):
        self.assertEqual(resolve_brand_domain("Some Company", ""), "")


class TestScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result, cls.labels = scan_acme()
        cls.by_name = {f.vendor.name: f for f in cls.result.findings}

    def test_method(self):
        self.assertEqual(self.result.method, "page+dns")

    def test_dns_layer_confirms_vendors(self):
        # SPF include -> Klaviyo; DKIM selector CNAME -> Mailchimp;
        # MX + SPF -> Google Workspace; service CNAMEs -> Zendesk, Greenhouse;
        # DMARC rua -> EasyDMARC; NS + header -> Cloudflare; IP range -> Shopify.
        for name in ("Klaviyo", "Mailchimp", "Google Workspace", "SendGrid",
                     "Zendesk", "Greenhouse", "EasyDMARC", "Cloudflare",
                     "Shopify"):
            self.assertIn(name, self.by_name, f"{name} not detected")
            self.assertEqual(self.by_name[name].confidence, "confirmed", name)

    def test_page_layer_observes_tags(self):
        for name in ("Stripe", "LoyaltyLion", "Google Tag Manager"):
            self.assertIn(name, self.by_name, f"{name} not detected")
            self.assertEqual(self.by_name[name].confidence, "observed", name)

    def test_gtm_container_expansion(self):
        # Hotjar loads only inside the GTM container; the homepage merely
        # mentions it in prose, which must not be the source of the hit.
        self.assertIn("Hotjar", self.by_name)
        self.assertTrue(
            any("GTM" in ev for ev in self.by_name["Hotjar"].evidence))

    def test_prose_mentions_are_not_detections(self):
        # The fixture homepage says "We accept Klarna and Afterpay", reviews
        # "Mixpanel vs Hotjar", name-drops Trustpilot, and has a cookie
        # notice listing Tidio and PowerReviews. None of their assets load,
        # so none of them may be reported - a vendor name in prose is not
        # evidence. This is the cookie-banner false-positive trap.
        for decoy in ("Klarna", "Afterpay", "Mixpanel", "Trustpilot",
                      "Tidio", "PowerReviews"):
            self.assertNotIn(decoy, self.by_name,
                             f"{decoy} detected from a prose mention")

    def test_page_text_channel_matches_markup(self):
        # window.Shopify is inline JS, not a URL - the page_text channel
        # exists for exactly this signature.
        self.assertTrue(
            any("window\\.shopify" in ev
                for ev in self.by_name["Shopify"].evidence),
            self.by_name["Shopify"].evidence)

    def test_shared_vendor_is_suppressed(self):
        # sparkpostmail.com is in the SPF, but SendGrid (non-shared, same
        # category) is too - the ambiguous tag adds nothing.
        self.assertNotIn("SparkPost", self.by_name)

    def test_unknown_signals_are_surfaced(self):
        self.assertIn("acme.mysterystatus-example.net", self.result.unknowns)
        self.assertIn("widget.newloyaltything.example", self.result.unknowns)
        # Known and generic hosts must not leak into the unknown list.
        joined = " ".join(self.result.unknowns)
        self.assertNotIn("zendesk", joined)
        self.assertNotIn("_spf", joined)

    def test_evidence_names_the_record(self):
        self.assertTrue(
            any("k1._domainkey" in ev for ev in self.by_name["Mailchimp"].evidence))

    def test_dns_only_mode(self):
        result, _ = scan_acme(dns_only=True)
        names = {f.vendor.name for f in result.findings}
        self.assertIn("Klaviyo", names)
        self.assertNotIn("Stripe", names)
        self.assertEqual(result.method, "dns-only")


class TestCollisionDecoys(unittest.TestCase):
    def test_lookalike_hosts_are_not_detections(self):
        # decoycorp's DNS is built entirely of lookalike hosts that CONTAIN
        # vendor patterns as substrings: portal.clever.co (not Lever),
        # shop.twix.com (not Wix), sso.oauth0.com (not Auth0),
        # monitor.asagari.net (not Agari), jobs.wintergreenhouse.io (not
        # Greenhouse), ats.lever.company (not lever.co), cdn.breakfastly.net
        # (not Fastly), relay.sozoho.com (not Zoho), SPF includes
        # spf.literable.net (not Iterable) and mail.embraze.io (not Braze),
        # and the page loads cdn.sundrip.com (not Drip) and
        # static.concordial.example.net (not Cordial). Every one must come
        # back as an unmatched signal, never as a vendor claim.
        vendors, _ = load_db()
        fx = FIX_ROOT / "decoys"
        resolver = FixtureResolver(json.loads((fx / "dns.json").read_text()))
        fetcher = FixtureFetcher(json.loads((fx / "http.json").read_text()))
        result = scan_domain("", "decoycorp.example", vendors, resolver, fetcher)

        claimed = [f.vendor.name for f in result.findings]
        self.assertEqual(claimed, [], f"lookalikes claimed as vendors: {claimed}")
        # Surfaced for a human, not silently dropped (the list caps at 6,
        # so assert on entries early in probe order).
        joined = " ".join(result.unknowns)
        self.assertIn("asagari", joined, result.unknowns)
        self.assertIn("lever.company", joined, result.unknowns)


class TestReport(unittest.TestCase):
    def test_json_and_csv_round_trip(self):
        result, labels = scan_acme()
        doc = json.loads(to_json([result], labels))
        self.assertEqual(doc["results"][0]["domain"], "acmeoutfitters.example")
        vendors = {v["name"]: v for v in doc["results"][0]["vendors"]}
        self.assertEqual(vendors["Klaviyo"]["confidence"], "confirmed")
        self.assertTrue(vendors["Klaviyo"]["evidence"])

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.csv"
            write_csv([result], labels, out)
            text = out.read_text()
        self.assertIn("Klaviyo", text)
        self.assertIn("Stripe ~", text)  # page-only vendors carry the marker
