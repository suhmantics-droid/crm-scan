// stackscan web - the DNS layer of stackscan, running entirely in the
// browser. Possible because Cloudflare's and Google's DNS-over-HTTPS
// endpoints are CORS-enabled: the page queries DNS itself, no backend.
//
// This is a port of stackscan/engine.py's DNS layer. The page layer
// (homepage JS tags, headers) needs the CLI: browsers cannot fetch
// arbitrary sites cross-origin. Keep the two in sync when probes change.
//
// ES module usable from the browser page and from node (web/app.test.mjs).

export const TYPE_CODES = { A: 1, NS: 2, CNAME: 5, MX: 15, TXT: 16 };

const PROVIDERS = [
  "https://cloudflare-dns.com/dns-query?",
  "https://dns.google/resolve?",
];

export const EMAIL_SUBS = ["email", "e", "mail", "news", "marketing", "mkt",
  "edm", "go", "links", "hello", "m", "info"];

export const DKIM_SELECTORS = ["k1", "k2", "kl", "dkim", "dkim1", "selector1",
  "selector2", "mte1", "dd", "ometria", "default", "s1", "s2", "google",
  "mandrill"];

export const SERVICE_SUBS = ["help", "support", "status", "careers", "jobs",
  "login", "sso", "auth", "id", "account", "autodiscover", "shop", "my",
  "app", "community", "blog"];

const PREFIXES = new Set(["email", "e", "mail", "news", "updates", "marketing",
  "go", "links", "m", "enews", "emails", "mailing", "r1", "cmp", "edm",
  "info", "hello", "click", "message", "em", "comms", "newsletter", "www"]);

const NOISE_RX = new RegExp(
  "_spf|^all$|^spf[.-]|\\.spf\\.|dkim\\.|domainkey|secureserver|godaddy|" +
  "domaincontrol|namecheap|ionos|\\bovh\\b|gandi|123-reg|register\\.|" +
  "registrar|short\\.io|bit\\.ly|\\.arpa$");

const CONFIRMED = new Set(["dns", "mx", "ns", "ip"]);

export function resolveBrandDomain(raw) {
  let cand = (raw || "").trim().toLowerCase()
    .replace(/^https?:\/\//, "").split("/")[0];
  if (!/^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}$/.test(cand)) return "";
  for (;;) {
    const labels = cand.split(".");
    if (labels.length >= 3 && PREFIXES.has(labels[0])) {
      cand = labels.slice(1).join(".");
    } else break;
  }
  return cand;
}

export async function dohQuery(fetchFn, name, rtype) {
  const params = new URLSearchParams({ name, type: rtype });
  for (const base of PROVIDERS) {
    try {
      const resp = await fetchFn(base + params.toString(), {
        headers: { accept: "application/dns-json" },
      });
      if (!resp.ok) continue;
      return extractAnswers(await resp.json(), rtype);
    } catch {
      continue; // next provider; both failing means no answer
    }
  }
  return [];
}

export function extractAnswers(payload, rtype) {
  const want = TYPE_CODES[rtype];
  const out = [];
  for (const ans of payload.Answer || []) {
    if (ans.type !== want) continue; // A queries also return the CNAME chain
    let data = ans.data || "";
    if (rtype === "TXT") {
      data = data.split('"').filter((p) => p && p !== " ").join("");
    } else if (rtype === "MX") {
      data = data.split(/\s+/).pop();
    }
    out.push(data.replace(/\.$/, ""));
  }
  return out;
}

function buildProbes(domain) {
  const probes = [
    { kind: "apex_txt", name: domain, type: "TXT" },
    { kind: "mx", name: domain, type: "MX" },
    { kind: "ns", name: domain, type: "NS" },
    { kind: "a", name: domain, type: "A" },
    { kind: "dmarc", name: `_dmarc.${domain}`, type: "TXT" },
  ];
  for (const s of EMAIL_SUBS) {
    probes.push({ kind: "sub_txt", name: `${s}.${domain}`, type: "TXT" });
    probes.push({ kind: "cname", name: `${s}.${domain}`, type: "CNAME" });
  }
  for (const s of SERVICE_SUBS) {
    probes.push({ kind: "cname", name: `${s}.${domain}`, type: "CNAME" });
  }
  for (const sel of DKIM_SELECTORS) {
    probes.push({ kind: "cname", name: `${sel}._domainkey.${domain}`, type: "CNAME" });
  }
  return probes;
}

async function runBatched(jobs, worker, limit, onProgress) {
  const results = new Array(jobs.length);
  let next = 0, done = 0;
  async function lane() {
    for (;;) {
      const i = next++;
      if (i >= jobs.length) return;
      results[i] = await worker(jobs[i]);
      if (onProgress) onProgress(++done, jobs.length);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, jobs.length) }, lane));
  return results;
}

export async function collectDns(domain, fetchFn, onProgress) {
  const probes = buildProbes(domain);
  const answers = await runBatched(
    probes, (p) => dohQuery(fetchFn, p.name, p.type), 10, onProgress);

  const sig = { dns: [], mx: [], ns: [], ips: [], cnameTargets: [], includes: [] };
  const spfTexts = [];
  probes.forEach((p, i) => {
    for (const data of answers[i] || []) {
      if (p.kind === "apex_txt" || p.kind === "sub_txt") {
        if (data.toLowerCase().includes("spf")) {
          sig.dns.push([`SPF ${p.name}`, data]);
          spfTexts.push(data);
        }
      } else if (p.kind === "dmarc") {
        sig.dns.push([`DMARC ${p.name}`, data]);
      } else if (p.kind === "cname") {
        sig.dns.push([`CNAME ${p.name}`, data]);
        sig.cnameTargets.push(data);
      } else if (p.kind === "mx") {
        sig.mx.push([`MX ${p.name}`, data]);
      } else if (p.kind === "ns") {
        sig.ns.push([`NS ${p.name}`, data]);
      } else if (p.kind === "a") {
        sig.ips.push(data);
      }
    }
  });

  // Expand SPF includes one level: the ESP's own record is where the
  // giveaway usually sits.
  const seen = new Set();
  for (const s of spfTexts) {
    for (const m of s.matchAll(/include:([^\s]+)/g)) {
      if (!seen.has(m[1])) seen.add(m[1]);
    }
  }
  sig.includes = [...seen].slice(0, 15);
  const expanded = await runBatched(
    sig.includes, (inc) => dohQuery(fetchFn, inc, "TXT"), 10);
  sig.includes.forEach((inc, i) => {
    sig.dns.push([`SPF include ${inc}`, inc]);
    for (const s of expanded[i] || []) {
      if (s.toLowerCase().includes("spf")) sig.dns.push([`SPF include ${inc}`, s]);
    }
  });
  return sig;
}

function ipInCidr(ip, cidr) {
  const toInt = (a) => a.split(".").reduce((n, o) => n * 256 + (+o), 0);
  const [net, bits] = cidr.split("/");
  if (!/^\d+\.\d+\.\d+\.\d+$/.test(ip)) return false;
  const mask = bits === "0" ? 0 : (-1 << (32 - +bits)) >>> 0;
  return ((toInt(ip) & mask) >>> 0) === ((toInt(net) & mask) >>> 0);
}

function snippet(text, match, width = 34) {
  const start = Math.max(0, match.index - width);
  const frag = text.slice(start, match.index + match[0].length + width)
    .replace(/\n/g, " ").trim();
  return frag.length < text.length ? `...${frag}...` : frag;
}

export function matchVendors(db, sig) {
  const findings = [];
  for (const cat of db.categories) {
    for (const v of cat.vendors) {
      const channels = new Set();
      const evidence = [];
      const hit = (ch, ev) => {
        channels.add(ch);
        if (evidence.length < 3) evidence.push(ev);
      };
      for (const ch of ["dns", "mx", "ns"]) {
        for (const pat of v[ch] || []) {
          const rx = new RegExp(pat);
          for (const [source, text] of sig[ch]) {
            const m = rx.exec(text.toLowerCase());
            if (m) {
              hit(ch, `${source}: ${snippet(text.toLowerCase(), m)}`);
              break; // one evidence line per pattern is plenty
            }
          }
        }
      }
      for (const cidr of v.ip_cidr || []) {
        for (const ip of sig.ips) {
          if (ipInCidr(ip, cidr)) hit("ip", `A record ${ip} in ${cidr}`);
        }
      }
      if (channels.size) {
        findings.push({
          name: v.name, category: cat.category, label: cat.label,
          shared: !!v.shared, channels: [...channels].sort(), evidence,
          confidence: [...channels].some((c) => CONFIRMED.has(c))
            ? "confirmed" : "observed",
        });
      }
    }
  }
  // Shared infrastructure (SparkPost et al.) adds nothing once a real
  // vendor in the same category is identified.
  const named = new Set(findings.filter((f) => !f.shared).map((f) => f.category));
  return findings.filter((f) => !(f.shared && named.has(f.category)));
}

export function surfaceUnknowns(db, sig, domain) {
  const dnsRx = [];
  for (const cat of db.categories) {
    for (const v of cat.vendors) {
      for (const ch of ["dns", "mx", "ns"]) {
        for (const pat of v[ch] || []) dnsRx.push(new RegExp(pat));
      }
    }
  }
  const out = [];
  for (const cand of [...sig.includes, ...sig.cnameTargets]) {
    const c = cand.toLowerCase().replace(/\.$/, "");
    if (!c || c.includes(domain) || NOISE_RX.test(c)) continue;
    if (dnsRx.some((rx) => rx.test(c))) continue;
    if (!out.includes(c)) out.push(c);
  }
  return out.slice(0, 6);
}

export async function scanDomain(rawInput, db, fetchFn, onProgress) {
  const domain = resolveBrandDomain(rawInput);
  if (!domain) return { domain: "", error: "not a scannable domain" };
  const sig = await collectDns(domain, fetchFn, onProgress);
  return {
    domain,
    findings: matchVendors(db, sig),
    unknowns: surfaceUnknowns(db, sig, domain),
    queried: sig.dns.length + sig.mx.length + sig.ns.length,
  };
}
