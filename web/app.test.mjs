// Offline tests for the web scanner's engine: the acme fixtures are served
// through a stubbed fetch in DoH JSON wire format, so this exercises the
// real parsing path end to end. Run: node --test web/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  TYPE_CODES, extractAnswers, resolveBrandDomain, scanDomain,
} from "./app.js";

const fixtures = JSON.parse(readFileSync(
  new URL("../tests/fixtures/acme/dns.json", import.meta.url), "utf-8"));
const db = JSON.parse(readFileSync(
  new URL("./fingerprints.json", import.meta.url), "utf-8"));

// Serve fixtures the way a DoH endpoint would put them on the wire:
// TXT quoted, CNAME/NS/MX with trailing dots, MX with a preference.
function fixtureFetch(url) {
  const params = new URL(url).searchParams;
  const name = params.get("name");
  const type = params.get("type");
  const rdata = fixtures[`${type}:${name}`] || [];
  const answer = rdata.map((data) => ({
    name,
    type: TYPE_CODES[type],
    data: type === "TXT" ? `"${data}"`
      : type === "MX" ? `10 ${data}.`
      : type === "A" ? data
      : `${data}.`,
  }));
  return Promise.resolve({
    ok: true,
    json: async () => (answer.length ? { Status: 0, Answer: answer } : { Status: 3 }),
  });
}

test("extractAnswers unquotes and rejoins split TXT strings", () => {
  const payload = { Answer: [{ type: 16, data: '"v=spf1 include:a" " ~all"' }] };
  assert.deepEqual(extractAnswers(payload, "TXT"), ["v=spf1 include:a ~all"]);
});

test("extractAnswers strips MX preference and skips the CNAME chain", () => {
  const payload = {
    Answer: [
      { type: 5, data: "alias.example.com." },
      { type: 15, data: "10 mx.example.com." },
    ],
  };
  assert.deepEqual(extractAnswers(payload, "MX"), ["mx.example.com"]);
});

test("resolveBrandDomain strips prefixes and URLs", () => {
  assert.equal(resolveBrandDomain("email.gymshark.co.uk"), "gymshark.co.uk");
  assert.equal(resolveBrandDomain("https://www.allbirds.com/pages/x"), "allbirds.com");
  assert.equal(resolveBrandDomain("not a domain"), "");
});

test("full scan against the acme fixtures", async () => {
  const result = await scanDomain("acmeoutfitters.example", db, fixtureFetch);
  const names = new Map(result.findings.map((f) => [f.name, f]));

  // Same expectations as the Python suite's DNS layer.
  for (const name of ["Klaviyo", "Mailchimp", "Google Workspace", "SendGrid",
                      "Zendesk", "Greenhouse", "EasyDMARC", "Cloudflare",
                      "Shopify"]) {
    assert.ok(names.has(name), `${name} not detected`);
    assert.equal(names.get(name).confidence, "confirmed", name);
  }
  assert.ok(!names.has("SparkPost"), "shared vendor must be suppressed");

  assert.ok(result.unknowns.includes("acme.mysterystatus-example.net"));
  assert.ok(!result.unknowns.some((u) => u.includes("zendesk")));
  assert.ok(!result.unknowns.some((u) => u.includes("_spf")));

  const mailchimp = names.get("Mailchimp");
  assert.ok(mailchimp.evidence.some((e) => e.includes("k1._domainkey")),
    "evidence names the DKIM record");
  assert.ok(names.get("Shopify").evidence.some((e) => e.includes("23.227.38.74")),
    "Shopify confirmed from its published IP range");
});
