"""stackscan - vendor-stack fingerprinting from public signals.

Grown out of crm-scan.ps1: the same two-layer idea (DNS records first, one
page fetch second), generalized from "which ESP does this brand run" to
"what is this company's vendor stack", with the fingerprints moved out of
the code into a data-driven database under fingerprints/.

Stdlib only. No API keys, no enrichment vendor, no LLM calls.
"""

__version__ = "0.1.0"
