import json
import tempfile
import unittest
from pathlib import Path

from stackscan.dns_client import FixtureResolver
from stackscan.engine import resolve_brand_domain, scan_domain
from stackscan.fingerprints import load_db
from stackscan.http_client import FixtureFetcher
from stackscan.report import to_json, write_csv

FIXTURES = Path(__file__).parent / "fixtures" / "acme"


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
        # Hotjar is only referenced inside the GTM container, not the page.
        self.assertIn("Hotjar", self.by_name)
        self.assertTrue(
            any("GTM" in ev for ev in self.by_name["Hotjar"].evidence))

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
