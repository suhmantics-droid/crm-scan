import unittest

from stackscan.dns_client import DohResolver


def payload_txt(*strings):
    return {"Status": 0,
            "Answer": [{"name": "x", "type": 16, "data": f'"{s}"'}
                       for s in strings]}


class ScriptedResolver(DohResolver):
    """DohResolver whose network layer is a scripted list of outcomes.

    Each entry is either an exception instance (raised) or a payload dict
    (returned). The script is consumed one entry per _fetch call.
    """

    def __init__(self, script):
        super().__init__(attempts=2, backoff=0)
        self.script = list(script)
        self.calls = 0

    def _fetch(self, url):
        self.calls += 1
        step = self.script.pop(0) if self.script else OSError("script empty")
        if isinstance(step, Exception):
            raise step
        return step


class TestDohResolver(unittest.TestCase):
    def test_provider_failure_falls_through_to_next(self):
        r = ScriptedResolver([OSError("throttled"), payload_txt("v=spf1 a")])
        self.assertEqual(r.query("brand.com", "TXT"), ["v=spf1 a"])

    def test_failures_are_never_cached(self):
        # Both providers down twice (attempts=2 x 2 providers = 4 calls),
        # then the network recovers. The empty answer from the outage must
        # not have been cached as truth - that would blank out the domain
        # for the rest of a long run.
        r = ScriptedResolver([OSError()] * 4 + [payload_txt("v=spf1 b")])
        self.assertEqual(r.query("brand.com", "TXT"), [])
        self.assertEqual(r.query("brand.com", "TXT"), ["v=spf1 b"])

    def test_servfail_is_an_outage_not_an_answer(self):
        r = ScriptedResolver([{"Status": 2}] * 4 + [payload_txt("v=spf1 c")])
        self.assertEqual(r.query("brand.com", "TXT"), [])
        self.assertEqual(r.query("brand.com", "TXT"), ["v=spf1 c"])

    def test_real_answers_are_cached(self):
        r = ScriptedResolver([payload_txt("v=spf1 d")])
        self.assertEqual(r.query("brand.com", "TXT"), ["v=spf1 d"])
        self.assertEqual(r.query("brand.com", "TXT"), ["v=spf1 d"])
        self.assertEqual(r.calls, 1)

    def test_nxdomain_is_a_cacheable_answer(self):
        r = ScriptedResolver([{"Status": 3}])
        self.assertEqual(r.query("missing.brand.com", "CNAME"), [])
        self.assertEqual(r.query("missing.brand.com", "CNAME"), [])
        self.assertEqual(r.calls, 1)

    def test_split_txt_strings_are_rejoined(self):
        payload = {"Status": 0, "Answer": [
            {"name": "x", "type": 16, "data": '"v=spf1 include:a" " ~all"'}]}
        self.assertEqual(DohResolver._extract(payload, "TXT"),
                         ["v=spf1 include:a ~all"])

    def test_mx_preference_stripped_and_cname_chain_skipped(self):
        payload = {"Status": 0, "Answer": [
            {"name": "x", "type": 5, "data": "alias.example.com."},
            {"name": "x", "type": 15, "data": "10 mx.example.com."}]}
        self.assertEqual(DohResolver._extract(payload, "MX"),
                         ["mx.example.com"])
