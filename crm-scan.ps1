<#
.SYNOPSIS
  Detect a brand's email/CRM platform, loyalty stack and mail host from DNS + homepage HTML.

.DESCRIPTION
  No API keys, no paid enrichment vendor, no LLM calls. Two free layers:

    DNS   — SPF includes, DKIM selector CNAMEs and DMARC rua records fingerprint the
            sending platform. An ESP's SPF record is effectively its master sending-IP
            list, so a brand's marketing subdomain announces which ESP it runs.
    PAGE  — onsite tags (loyalty, reviews, personalisation) are JavaScript and therefore
            invisible to DNS. A homepage regex catches those.

  Sites behind Cloudflare/Akamai often refuse the homepage. Rather than paying a rendering
  service, this falls back to signals that survive the wall: the Shopify products endpoint,
  published Shopify IP ranges, and sitemap.xml / robots.txt for store locators.

.PARAMETER Domain
  One or more domains to scan directly.

.PARAMETER InputCsv
  CSV containing a Company and/or Domain column. Headers are auto-detected.

.PARAMETER OutputCsv
  Where to write results. Defaults to .\crm-scan-results.csv

.EXAMPLE
  .\crm-scan.ps1 -Domain gymshark.com, allbirds.com

.EXAMPLE
  .\crm-scan.ps1 -InputCsv brands.csv -OutputCsv results.csv

.NOTES
  Read-only. Public DNS queries and ordinary GET requests only, the same traffic a browser
  makes. Rate-limit yourself on large lists and respect robots.txt.
#>
[CmdletBinding(DefaultParameterSetName = 'Direct')]
param(
  [Parameter(ParameterSetName = 'Direct', Mandatory = $true, Position = 0)]
  [string[]]$Domain,

  [Parameter(ParameterSetName = 'Csv', Mandatory = $true)]
  [string]$InputCsv,

  [string]$OutputCsv = 'crm-scan-results.csv',
  [string]$CompanyHeader = 'Company',
  [string]$DomainHeader = 'Domain',

  # Skip the page layer. DNS only: faster, quieter, catches ESPs but not onsite tags.
  [switch]$DnsOnly,

  # Seconds to wait between domains. Be polite on long lists.
  [int]$DelaySeconds = 0
)

$ErrorActionPreference = 'Continue'
$UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

# ---------------------------------------------------------------- signatures --
# Onsite platforms. These are JS tags, so DNS cannot see them.
$PAGE = [ordered]@{
  'bloomreach|exponea' = 'Bloomreach'; 'loyaltylion' = 'LoyaltyLion'; 'klaviyo' = 'Klaviyo'
  'yotpo' = 'Yotpo'; 'scarabresearch|emarsys' = 'Emarsys'
  'dotdigital|dotmailer|dmtrk|trackedlink' = 'Dotdigital'; 'useinsider' = 'Insider'
  '\bnosto' = 'Nosto'; 'ometria' = 'Ometria'; 'klevu' = 'Klevu'; 'gorgias' = 'Gorgias'
  'trustpilot' = 'Trustpilot'; 'reviews\.io|reviews\.co\.uk' = 'Reviews.io'; 'feefo' = 'Feefo'
  'hubspot' = 'HubSpot'; 'attentivemobile' = 'Attentive'; 'smile\.io' = 'Smile'
  'mcsv\.net|chimpstatic|list-manage|mailchimp' = 'Mailchimp'; 'tiqcdn|tealium' = 'Tealium'
  'cdn\.segment' = 'Segment'; 'braze|appboy' = 'Braze'; 'cordial' = 'Cordial'
  'sailthru' = 'Sailthru'; 'antavo' = 'Antavo'; 'punchh' = 'Punchh'
  'marketo|mktoresp' = 'Marketo'; 'pardot' = 'Pardot'; 'sendinblue|brevo' = 'Brevo'
  'omnisend' = 'Omnisend'; 'activecampaign' = 'ActiveCampaign'; 'ortto' = 'Ortto'
  'wunderkind|bounceexchange' = 'Wunderkind'; 'drip\.com|getdrip' = 'Drip'
  'mailerlite' = 'MailerLite'; 'acoustic|silverpop' = 'Acoustic'; 'voyado' = 'Voyado'
  'okendo' = 'Okendo'; 'rebuyengine' = 'Rebuy'; 'stamped\.io' = 'Stamped'
}

# Sending platforms visible in SPF / DKIM / CNAME records.
$DNSSIG = [ordered]@{
  'dotmailer|dotdigital|dmtrk' = 'Dotdigital'; 'klaviyo' = 'Klaviyo'
  'mcsv\.net|mailchimp|mandrill' = 'Mailchimp'
  'exacttarget|cust-spf|mta\.salesforce|custdkim\.salesforce' = 'Salesforce MC'
  'exponea|bloomreach' = 'Bloomreach'; 'emarsys' = 'Emarsys'; 'ometria' = 'Ometria'
  'sailthru' = 'Sailthru'; 'iterable' = 'Iterable'; 'marketo|mktomail' = 'Marketo'
  'pardot' = 'Pardot'; 'hubspotemail|hubspot\.net|hs-sending' = 'HubSpot'
  'oracleemaildelivery|responsys|rsys\.' = 'Oracle Responsys'; 'eloqua|elqemail' = 'Oracle Eloqua'
  'msgfocus' = 'Adestra'; 'emailvision' = 'SmartFocus'; 'customeriomail' = 'Customer.io'
  'cmail\d|createsend' = 'Campaign Monitor'; 'zcsend' = 'Zoho'
  'alterian|cheetahmail|cheetahdigital' = 'Marigold'; 'epidm\.net' = 'Optimizely'
  'm-pages|\bmapp' = 'Mapp'; 'slgnt\.eu|selligent' = 'Selligent'; 'listrak' = 'Listrak'
  # Added after the unknown-vendor catch-all surfaced it on a live scan (gymshark.com).
  'bronto\.com|bm23\.com' = 'Oracle Bronto'
  'sparkpost' = 'SparkPost (shared)'
}

$LOYALTY = @('LoyaltyLion','Yotpo','Nosto','Klevu','Trustpilot','Smile','Antavo','Attentive',
             'Punchh','Wunderkind','Okendo','Rebuy','Stamped','Reviews.io','Feefo')

# Marketing-mail subdomains worth probing. Trimmed to the productive ones: the long tail
# roughly doubles DNS time and rarely adds a platform.
$SUBS = @('email','e','mail','news','marketing','mkt','edm','go','links','hello','m','info')
$DKIMSEL = @('k1','k2','kl','dkim','dkim1','selector1','selector2','mte1','dd','ometria','default','s1','s2','google')

# Sending prefixes stripped to recover the brand domain: email.brand.co.uk -> brand.co.uk
$PREFIX = @('email','e','mail','news','updates','marketing','go','links','m','enews','emails',
            'mailing','r1','cmp','edm','info','hello','click','message','em','comms','newsletter')

# Plumbing, not a marketing CRM. Excluded from the unknown-vendor catch-all.
$GENERIC = 'google|outlook|microsoft|protection\.|amazonses|amazonaws|sendgrid|mailgun|mandrill|' +
           'mimecast|messagelabs|proofpoint|pphosted|barracuda|cloudflare|zendesk|_spf|spf\.protection|' +
           '\bspf\.|^all$|servers\.mcsv|transmail|fastly|akamai|secureserver|godaddy|myshopify|shopify|' +
           'wix|squarespace|register|namecheap|ionos|ovh|gandi|heroku|vercel|netlify|123-reg|zoho\b|' +
           'easydmarc|dmarcian|valimail|short\.io|bit\.ly|onmicrosoft'

# ------------------------------------------------------------------- helpers --
function Get-Homepage {
  param([string]$d)
  foreach ($u in "https://www.$d", "https://$d") {
    try {
      return (Invoke-WebRequest -Uri $u -UserAgent $UA -TimeoutSec 20 -UseBasicParsing `
                                -MaximumRedirection 5 -ErrorAction Stop).Content
    } catch { }
  }
  return $null
}

function Get-TxtStrings {
  param([string]$name)
  try { return (Resolve-DnsName $name -Type TXT -ErrorAction Stop | Where-Object { $_.Strings }).Strings }
  catch { return @() }
}

function Get-DnsPlatforms {
  param([string]$d)
  $blob = @(); $includes = @(); $cnames = @()

  # NB: $host is a read-only automatic variable in PowerShell — do not use it as a loop var.
  foreach ($probe in (@($d) + ($SUBS | ForEach-Object { "$_.$d" }))) {
    $spf = Get-TxtStrings $probe | Where-Object { $_ -match 'spf' }
    if ($spf) { $blob += ($spf -join ' ') }
    try {
      $nh = (Resolve-DnsName $probe -Type CNAME -ErrorAction Stop).NameHost
      if ($nh) { $blob += ($nh -join ' '); $cnames += $nh }
    } catch { }
  }

  foreach ($sel in $DKIMSEL) {
    try {
      $nh = (Resolve-DnsName "$sel._domainkey.$d" -Type CNAME -ErrorAction Stop).NameHost
      if ($nh) { $blob += ($nh -join ' '); $cnames += $nh }
    } catch { }
  }

  # DMARC aggregate-report addresses frequently name the ESP.
  $dmarc = Get-TxtStrings "_dmarc.$d"
  if ($dmarc) { $blob += ($dmarc -join ' ') }

  $text = ($blob -join ' ').ToLower()

  # Expand SPF includes one level: the ESP's own record is where the giveaway usually sits.
  foreach ($m in [regex]::Matches($text, 'include:([^\s]+)')) {
    $inc = $m.Groups[1].Value
    $includes += $inc
    $sub = Get-TxtStrings $inc | Where-Object { $_ -match 'spf' }
    if ($sub) { $text += ' ' + ($sub -join ' ').ToLower() }
  }

  $hits = @()
  foreach ($k in $DNSSIG.Keys) { if ($text -match $k) { $hits += $DNSSIG[$k] } }

  # Anything unrecognised and not generic infra is surfaced rather than silently dropped.
  # This is how a platform with no signature yet gets discovered.
  $unknown = @()
  foreach ($x in (@($includes) + @($cnames))) {
    if (-not $x) { continue }
    $xl = $x.ToLower().TrimEnd('.')
    if ($xl -match $GENERIC) { continue }
    $known = $false
    foreach ($k in $DNSSIG.Keys) { if ($xl -match $k) { $known = $true; break } }
    if (-not $known) { $unknown += $xl }
  }

  return [pscustomobject]@{
    Platforms = @($hits | Select-Object -Unique)
    Unknown   = @($unknown | Select-Object -Unique | Select-Object -First 4)
    SpfText   = $text
  }
}

function Get-MailHost {
  param([string]$d, [string]$spfText)
  # MX alone is unreliable: security gateways (Mimecast, Proofpoint) mask the real host.
  # SPF includes, the autodiscover CNAME and DKIM selectors are what actually settle it.
  if ($spfText -match '_spf\.google\.com|googlemail\.com')      { return 'Google' }
  if ($spfText -match 'spf\.protection\.outlook\.com|protection\.outlook') { return 'Microsoft' }
  try {
    $ad = (Resolve-DnsName "autodiscover.$d" -Type CNAME -ErrorAction Stop).NameHost
    if ($ad -match 'outlook\.com') { return 'Microsoft' }
  } catch { }
  foreach ($sel in @('selector1','selector2')) {
    try {
      $nh = (Resolve-DnsName "$sel._domainkey.$d" -Type CNAME -ErrorAction Stop).NameHost
      if ($nh -match 'onmicrosoft\.com') { return 'Microsoft' }
    } catch { }
  }
  return ''
}

function Get-PagePlatforms {
  param([string]$html)
  $hits = @(); $unknown = @()
  if (-not $html) { return [pscustomobject]@{ Platforms = @(); Unknown = @() } }
  $l = $html.ToLower()

  foreach ($k in $PAGE.Keys) { if ($l -match $k) { $hits += $PAGE[$k] } }

  # A GTM container often loads the martech the page itself does not reference.
  foreach ($g in ([regex]::Matches($html, 'GTM-[A-Z0-9]{4,}') | ForEach-Object { $_.Value } | Select-Object -Unique)) {
    try {
      $c = (Invoke-WebRequest -Uri "https://www.googletagmanager.com/gtm.js?id=$g" -UserAgent $UA `
                              -TimeoutSec 12 -UseBasicParsing -ErrorAction Stop).Content.ToLower()
      foreach ($k in $PAGE.Keys) { if ($c -match $k) { $hits += $PAGE[$k] } }
    } catch { }
  }

  foreach ($m in [regex]::Matches($l, 'src="https?://([^/"]+)')) {
    $hn = $m.Groups[1].Value
    if ($hn -notmatch '(loyal|reward|review|personali|cdp|engage|wallet|subscrib|attentive|retention|sms)') { continue }
    if ($hn -match '(google|gstatic|facebook|cloudflare|jquery|doubleclick|hotjar|cookiebot|onetrust|youtube|shopify|jsdelivr|cloudfront|bootstrap)') { continue }
    $known = $false
    foreach ($k in $PAGE.Keys) { if ($hn -match $k) { $known = $true; break } }
    if (-not $known) { $unknown += $hn }
  }

  return [pscustomobject]@{
    Platforms = @($hits | Select-Object -Unique)
    Unknown   = @($unknown | Select-Object -Unique | Select-Object -First 4)
  }
}

function Test-Shopify {
  param([string]$d, [string]$html)
  # Works even when the homepage is blocked: the products endpoint usually answers through
  # the wall, and Shopify publishes its 23.227.32.0/19 range.
  if ($html -and $html -match 'cdn\.shopify|/cdn/shop/|window\.Shopify') { return $true }
  try {
    $r = Invoke-WebRequest -Uri "https://$d/products.json?limit=1" -UserAgent $UA -TimeoutSec 12 `
                           -UseBasicParsing -ErrorAction Stop
    if ($r.StatusCode -eq 200 -and $r.Content -match '"products"') { return $true }
  } catch { }
  try {
    $ips = (Resolve-DnsName $d -Type A -ErrorAction Stop).IPAddress
    foreach ($ip in $ips) { if ($ip -match '^23\.227\.(3[2-9]|4[0-9]|5[0-9]|6[0-3])\.') { return $true } }
  } catch { }
  return $false
}

function Resolve-BrandDomain {
  param([string]$company, [string]$current)
  $isDomain = { param($s) $s -and $s -notmatch '\s' -and $s -match '^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}$' }

  $cand = ''
  if (& $isDomain $current)                { $cand = $current.ToLower() }
  elseif (& $isDomain $company.ToLower())  { $cand = $company.ToLower() }

  if ($cand) {
    # Strip sending prefixes until the brand domain is left.
    $changed = $true
    while ($changed) {
      $changed = $false
      $lab = $cand.Split('.')
      if ($lab.Count -ge 3 -and ($PREFIX -contains $lab[0])) {
        $cand = ($lab[1..($lab.Count - 1)] -join '.'); $changed = $true
      }
    }
    return $cand
  }
  return ''
}

# ---------------------------------------------------------------------- main --
if ($PSCmdlet.ParameterSetName -eq 'Csv') {
  if (-not (Test-Path $InputCsv)) { throw "Input CSV not found: $InputCsv" }
  $rows = Import-Csv $InputCsv
  if (-not $rows) { throw "Input CSV is empty: $InputCsv" }
  $cols = $rows[0].PSObject.Properties.Name
  $cCol = $cols | Where-Object { $_ -match "(?i)^$CompanyHeader" } | Select-Object -First 1
  $dCol = $cols | Where-Object { $_ -match "(?i)^$DomainHeader" }  | Select-Object -First 1
  if (-not $cCol -and -not $dCol) { throw "No '$CompanyHeader' or '$DomainHeader' column found. Columns: $($cols -join ', ')" }
  $targets = $rows | ForEach-Object {
    [pscustomobject]@{
      Company = if ($cCol) { "$($_.$cCol)".Trim() } else { '' }
      Raw     = if ($dCol) { "$($_.$dCol)".Trim() } else { '' }
    }
  }
} else {
  $targets = $Domain | ForEach-Object { [pscustomobject]@{ Company = $_; Raw = $_ } }
}

# Dedupe before scanning. On one real list this collapsed 4,394 rows to 1,015 unique domains.
$seen = @{}
$results = New-Object System.Collections.ArrayList
$n = 0
$total = @($targets).Count

foreach ($t in $targets) {
  $n++
  $d = Resolve-BrandDomain $t.Company $t.Raw

  if (-not $d) {
    [void]$results.Add([pscustomobject]@{
      Company = $t.Company; Domain = ''; CRM = ''; Loyalty = ''; MailHost = ''
      Shopify = ''; Unknown = ''; Method = 'needs-domain'
    })
    Write-Host ("[{0}/{1}] {2,-30} -> no resolvable domain" -f $n, $total, $t.Company) -ForegroundColor DarkGray
    continue
  }

  if ($seen.ContainsKey($d)) {
    $prev = $seen[$d]
    [void]$results.Add([pscustomobject]@{
      Company = $t.Company; Domain = $d; CRM = $prev.CRM; Loyalty = $prev.Loyalty
      MailHost = $prev.MailHost; Shopify = $prev.Shopify; Unknown = $prev.Unknown
      Method = 'duplicate'
    })
    continue
  }

  $html = if ($DnsOnly) { $null } else { Get-Homepage $d }
  $dns  = Get-DnsPlatforms $d
  $page = if ($DnsOnly) { [pscustomobject]@{ Platforms = @(); Unknown = @() } } else { Get-PagePlatforms $html }

  $all = @($dns.Platforms + $page.Platforms) | Select-Object -Unique
  $crm = @($all | Where-Object { $LOYALTY -notcontains $_ })
  $loy = @($all | Where-Object { $LOYALTY -contains $_ })

  # SparkPost is shared infrastructure behind several ESPs. If a real vendor was identified,
  # the ambiguous tag adds nothing.
  if ($crm.Count -gt 1) { $crm = @($crm | Where-Object { $_ -ne 'SparkPost (shared)' }) }

  $method = if ($DnsOnly) { 'dns-only' } elseif ($html) { 'page+dns' } else { 'dns-only (blocked)' }

  $rec = [pscustomobject]@{
    Company  = $t.Company
    Domain   = $d
    CRM      = ($crm -join ', ')
    Loyalty  = ($loy -join ', ')
    MailHost = (Get-MailHost $d $dns.SpfText)
    Shopify  = if ($DnsOnly) { '' } elseif (Test-Shopify $d $html) { 'yes' } else { '' }
    Unknown  = ((@($dns.Unknown) + @($page.Unknown) | Select-Object -Unique) -join ', ')
    Method   = $method
  }

  $seen[$d] = $rec
  [void]$results.Add($rec)

  $colour = if ($rec.CRM) { 'Green' } elseif ($method -match 'blocked') { 'Yellow' } else { 'DarkGray' }
  Write-Host ("[{0}/{1}] {2,-30} -> {3} {4}" -f $n, $total, $d,
              $(if ($rec.CRM) { $rec.CRM } else { '(none found)' }),
              $(if ($method -match 'blocked') { '[blocked]' } else { '' })) -ForegroundColor $colour

  if ($DelaySeconds -gt 0) { Start-Sleep -Seconds $DelaySeconds }
}

$results | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8

$found   = @($results | Where-Object { $_.CRM }).Count
$blocked = @($results | Where-Object { $_.Method -match 'blocked' }).Count
Write-Host ""
Write-Host ("Scanned {0} rows, {1} unique domains." -f $total, $seen.Count)
Write-Host ("CRM identified: {0}  ({1:P0} coverage)" -f $found, $(if ($total) { $found / $total } else { 0 }))
Write-Host ("Homepage blocked: {0}  (DNS layer still applied)" -f $blocked)
Write-Host ("Written to {0}" -f $OutputCsv)
