import unittest

from stackscan.fingerprints import load_db, validate_db


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
