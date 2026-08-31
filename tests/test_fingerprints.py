import json
import unittest
from pathlib import Path

from stackscan.fingerprints import bundle_db, load_db, validate_db


class TestDatabase(unittest.TestCase):
    def test_database_is_clean(self):
        self.assertEqual(validate_db(), [])

    def test_database_loads_with_content(self):
        vendors, labels = load_db()
        self.assertGreater(len(vendors), 100)
        self.assertGreaterEqual(len(labels), 10)
        # Every vendor carries at least one signal (validate also checks this,
        # but load_db must agree after parsing).
        for v in vendors:
            self.assertTrue(
                v.patterns or v.headers or v.cidrs, f"{v.name} has no signals"
            )

    def test_category_filter(self):
        vendors, labels = load_db(categories={"payments"})
        self.assertEqual(set(labels), {"payments"})
        self.assertTrue(all(v.category == "payments" for v in vendors))

    def test_web_bundle_is_in_sync(self):
        # The web scanner ships a generated copy of the database. A stale
        # copy means the page and the CLI disagree about vendors.
        bundle_path = Path(__file__).parent.parent / "web" / "fingerprints.json"
        self.assertTrue(bundle_path.exists(), "run: python3 -m stackscan bundle")
        self.assertEqual(
            json.loads(bundle_path.read_text(encoding="utf-8")),
            bundle_db(),
            "web/fingerprints.json is stale - run: python3 -m stackscan bundle",
        )
