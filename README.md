# crm-scan

Detect which email platform, loyalty stack and mail host a brand runs, from DNS records and one page fetch.

No API keys. No enrichment vendor. No LLM calls. Pure PowerShell.

```powershell
.\crm-scan.ps1 -Domain gymshark.com
```
```
[1/1] gymshark.com  ->  Mailchimp, Marketo, Oracle Bronto, Braze
```

Also in this repo: [`yt-transcript.ps1`](#also-here-yt-transcriptps1), which pulls a YouTube transcript out of the caption track YouTube has already generated.

---

## Why this exists

I needed the CRM and email platform for 490 retail brands.

The obvious build was AI agents plus a scraping API. I piloted it on ten brands. It cost **532,000 tokens**, roughly **53k per brand**, which projected to about **26 million tokens** for the full list.

Then I looked at what the agents were actually doing: fetching a page and matching strings against a list of vendor names.

**A regex does not need a language model.**

Rebuilt on DNS lookups and a homepage regex, the same 490 brands returned **195 confirmed platforms in about 20 minutes at effectively zero token cost**. Same answers. The pilot alone had cost more than the entire rewritten run.

That is the whole idea. Most enrichment problems are lookup problems wearing an AI costume.

---

## The insight it's built on

**An ESP's SPF record is its master sending-IP list.**

When a brand sends marketing email through Klaviyo or Dotdigital, it has to authorise that platform to send on its behalf: publicly, in DNS, forever. So a brand's marketing subdomain quietly announces which platform it runs, to anyone who asks the right question.

Most people check the apex domain and find nothing useful. Marketing mail almost never sends from the apex. It sends from `email.brand.com`, `news.brand.com`, `mkt.brand.com`, each with its own SPF record.

Three record types carry the signal:

| Record | What it reveals |
|---|---|
| **SPF** on sending subdomains | The ESP authorised to send |
| **DKIM** selector CNAMEs | Often the cleanest fingerprint. `k1._domainkey → dkim.mcsv.net` is Mailchimp |
| **DMARC** `rua` address | Frequently names the vendor outright |

---

## Two layers, because one isn't enough

**DNS** catches sending platforms: Dotdigital, Klaviyo, Emarsys, Salesforce Marketing Cloud, Iterable, Listrak, Marketo, Oracle Responsys.

**Page** catches onsite platforms that are invisible to DNS because they are JavaScript tags, never email senders: Bloomreach, LoyaltyLion, Yotpo, Nosto, Attentive, Trustpilot.

Neither layer alone gives you the stack. Run both.

### When the homepage is blocked

Roughly **46% of one 1,015-domain list sat behind Cloudflare or Akamai** and returned 403 to any plain request. The expensive answer is a paid rendering service for every blocked site. The cheap answer is to ask something else:

- **Shopify** confirms itself via `/products.json`, which usually answers through the wall, or via its published `23.227.32.0/19` range.
- **Store locators** appear in `sitemap.xml` and `robots.txt`, which are served to crawlers by design. That recovered physical-presence data for 1,483 domains.
- **Mail host** comes from DNS, which cannot be blocked at all.

A blocked homepage costs you the onsite layer. It does not cost you the scan.

### Mail host: MX alone is wrong

Tempting to read the MX record and call it. It fails, because security gateways like Proofpoint and Mimecast sit in front of the real mailbox host and mask it. On one run that left **336 domains classified as a useless "Other"**.

Classifying from SPF includes, the `autodiscover` CNAME and DKIM selectors instead resolved the same list into **3,022 Microsoft and 818 Google**. It reuses DNS text already fetched, so it costs nothing extra.

Useful because Microsoft-heavy lists are materially harder to land cold email in.

---

## It tells you what it doesn't know

The signature tables are not exhaustive, and a scanner that silently drops what it cannot name is worse than useless: it reports a confident blank.

Anything that looks like a marketing platform but matches no signature goes into an **`Unknown`** column for a human to read. Generic infrastructure (Google, Microsoft, Cloudflare, SendGrid, DMARC monitors, link shorteners) is filtered out so the column stays short enough to actually review.

This is not a nicety. Building the public version of this tool, a test scan on `gymshark.com` surfaced `bronto.com` and `bm23.com` in that column: **Oracle Bronto, a real ESP with no signature in the table**. It's in the table now. That is the intended loop: the tool finds what it doesn't know, a human confirms it, the signature gets added.

---

## Usage

```powershell
# One or more domains
.\crm-scan.ps1 -Domain gymshark.com, allbirds.com

# A CSV with a Company and/or Domain column (headers auto-detected)
.\crm-scan.ps1 -InputCsv brands.csv -OutputCsv results.csv

# DNS only: faster and quieter, skips the page fetch entirely
.\crm-scan.ps1 -InputCsv brands.csv -DnsOnly

# Be polite on long lists
.\crm-scan.ps1 -InputCsv brands.csv -DelaySeconds 2
```

Requires Windows PowerShell 5.1 or PowerShell 7+. No modules, no keys, no install.

### Real output

From `examples-input.csv`, unedited:

| Domain | CRM | Mail host | Shopify | Method |
|---|---|---|---|---|
| gymshark.com | Mailchimp, Marketo, Oracle Bronto, Braze | Microsoft | yes | page+dns |
| allbirds.com | Mailchimp, Iterable | Google | yes | page+dns |
| lush.com | Mailchimp, Listrak | | | dns-only (blocked) |
| glossier.com | | | yes | page+dns |
| huel.com | | | yes | page+dns |

`lush.com` refused the homepage and still returned two platforms. That is the DNS layer earning its place.

### Messy input

Brand lists arrive broken. The domain recovery step handles the common shapes:

- Domain sitting in the Company column
- Raw sending domains: `email.barrheadtravel.co.uk` reduces to `barrheadtravel.co.uk`
- Duplicates: one real list collapsed **4,394 rows to 1,015 unique domains**, so the scan does 77% less work

On that 490-brand run, domain recovery alone lifted coverage from **67 to 195 brands**. It was worth more than any signature I added.

---

## Honest limitations

- **Presence, not usage.** A record proves a platform was authorised, not that it is used today or that it is the primary system. Stale SPF entries outlive migrations.
- **Multiple hits are normal.** A brand can run one platform for campaigns and another for transactional mail. The tool reports what it finds rather than guessing which is "the" CRM.
- **Transactional infrastructure is filtered, not reported.** SendGrid, Mailgun and Amazon SES are plumbing, not a marketing CRM, so they are deliberately excluded.
- **A blocked homepage costs the onsite layer.** Loyalty and reviews platforms will under-report on those rows. The `Method` column always tells you which rows were affected.
- **Signature coverage is finite.** That's what the `Unknown` column is for.

No result from this tool should enter a system of record without a human reading it. Its job is to narrow a list, not to be the last word.

---

## Also here: `yt-transcript.ps1`

Give it a YouTube link, get the transcript.

```powershell
.\yt-transcript.ps1 https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Same thesis as the scanner, pointed at a different problem.

The obvious build is to download the audio and run it through a speech-to-text model: yt-dlp, ffmpeg, a couple of gigabytes of Whisper weights, a minute of compute per video, or an API bill per hour of audio.

None of that is necessary, because **YouTube has already transcribed the video.** Anything with speech carries a caption track, either uploaded by the channel or generated by YouTube's own ASR, and both are public. The transcription has already happened and someone else has already paid for it. The job is to ask for it, not to redo it.

So this tool fetches, it does not transcribe. No keys, no models, no downloads, no waiting.

### Two layers, because one isn't enough

**InnerTube** is the player endpoint the YouTube clients themselves call. It answers with the caption track list as JSON. Three client contexts are tried in turn, because any single one of them can be refused on a given day.

**Page scrape** is the fallback: lift `ytInitialPlayerResponse` out of the watch page HTML, which needs a brace-matching parse rather than a regex, since caption text is full of braces and quotes.

Either layer yields a timed-text URL. That gets fetched as `json3`, falling back to YouTube's older XML track if the modern format is refused.

### Usage

```powershell
# Plain text to the console
.\yt-transcript.ps1 https://youtu.be/VIDEOID

# Subtitles to a file
.\yt-transcript.ps1 VIDEOID -Format Srt -OutputPath subs.srt

# A list of videos into a folder, one file each
.\yt-transcript.ps1 -InputFile videos.txt -OutputPath .\transcripts -Format Timestamps

# What captions does this video actually have?
.\yt-transcript.ps1 VIDEOID -ListTracks

# A specific language, or a machine translation of whatever it has
.\yt-transcript.ps1 VIDEOID -Language de
.\yt-transcript.ps1 VIDEOID -Translate fr
```

`watch`, `youtu.be`, `shorts`, `embed` and `live` URLs are all accepted, as is a bare 11-character video ID.

| Format | Output |
|---|---|
| `Text` (default) | Flowing wrapped paragraphs, readable as prose |
| `Lines` | One caption cue per line |
| `Timestamps` | `[mm:ss] text` per cue |
| `Srt` / `Vtt` | Subtitle files |
| `Json` | Cues with start and end seconds, plus video metadata |

Caption cues are three or four words each, so the default format runs them back together and breaks a paragraph at a sentence end. Auto-generated tracks have no punctuation at all, which is what the hard length backstop is for.

Manual captions are preferred over auto-generated ones in the same language, because a human wrote them. `-NoAuto` refuses ASR tracks outright.

### It tells you what it doesn't know

Same rule as the scanner. A video that could not be transcribed is named in the summary with the reason: no caption track published, not playable anonymously, track listed but empty, or not a YouTube URL at all. Nothing is silently dropped into a confident blank.

### Honest limitations

- **Auto-generated captions are ASR output.** They mishear proper nouns, they carry no punctuation or speaker labels, and they are worse on accents, crosstalk and background music. The header on a written file records whether the track was auto or manual, and you should care which.
- **No captions means no transcript.** A small number of videos publish none. This tool will tell you that rather than guessing. Getting one anyway means downloading the audio and running ASR yourself, which is exactly the expensive path the tool exists to avoid.
- **These endpoints are undocumented and YouTube changes them.** When every layer fails at once, that is almost always the reason rather than anything about the specific video.
- **Transcript text belongs to whoever made the video.** Fetching it is not the same as being licensed to republish it.

---

## Scope

Read-only. Public DNS queries and ordinary GET requests, the same traffic any browser makes visiting the site. It does not attempt authentication, does not evade bot protection, and treats a 403 as an answer rather than an obstacle to route around.

`yt-transcript.ps1` holds the same line: it asks for the public caption data the web player asks for when you press CC. It does not download audio or video, does not sign in, and does not reach anything behind an age gate or a paywall.

Rate-limit yourself on large lists with `-DelaySeconds`.

## Licence

MIT.
