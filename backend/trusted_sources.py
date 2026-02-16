"""
TRUSTED SOURCES — The Golden Circle

Whitelist of world-class review sites trusted for contextual intelligence.
These are the ONLY external sources the JIT agent may consult.

Per Source Rules: Contextual data requires 3+ independent trusted sources.
"""

from typing import List, Dict

# ═══════════════════════════════════════════════════════════════════════════
# THE GOLDEN CIRCLE — Trusted Review Domains
# ═══════════════════════════════════════════════════════════════════════════

TRUSTED_SOURCES: List[Dict[str, str]] = [
    {
        "name": "Sound On Sound",
        "domain": "soundonsound.com",
        "logo": "/assets/trusted/soundonsound.png",
        "specialty": "In-depth studio & instrument reviews",
    },
    {
        "name": "MusicRadar",
        "domain": "musicradar.com",
        "logo": "/assets/trusted/musicradar.png",
        "specialty": "Guitar, keys, drums, and production reviews",
    },
    {
        "name": "Sweetwater",
        "domain": "sweetwater.com",
        "logo": "/assets/trusted/sweetwater.png",
        "specialty": "Detailed product specs and expert reviews",
    },
    {
        "name": "Attack Magazine",
        "domain": "attackmagazine.com",
        "logo": "/assets/trusted/attack.png",
        "specialty": "Electronic music production and DJ gear",
    },
    {
        "name": "Sonic State",
        "domain": "sonicstate.com",
        "logo": "/assets/trusted/sonicstate.png",
        "specialty": "Synths, studio gear, and production tech",
    },
    {
        "name": "Equipboard",
        "domain": "equipboard.com",
        "logo": "/assets/trusted/equipboard.png",
        "specialty": "What gear do famous musicians use",
    },
    {
        "name": "Reverb",
        "domain": "reverb.com",
        "logo": "/assets/trusted/reverb.png",
        "specialty": "Market pricing and community reviews",
    },
    {
        "name": "Gearslutz / Gearspace",
        "domain": "gearspace.com",
        "logo": "/assets/trusted/gearspace.png",
        "specialty": "Professional audio community forums",
    },
    {
        "name": "Bonedo",
        "domain": "bonedo.de",
        "logo": "/assets/trusted/bonedo.png",
        "specialty": "German music gear reviews (detailed tests)",
    },
]

# Quick lookup sets
TRUSTED_DOMAINS = {s["domain"] for s in TRUSTED_SOURCES}
TRUSTED_NAMES = {s["name"] for s in TRUSTED_SOURCES}


def get_trusted_domains() -> List[str]:
    """Return list of trusted domains for site-restricted search."""
    return [s["domain"] for s in TRUSTED_SOURCES]


def build_site_restricted_query(product_name: str, max_sites: int = 6) -> str:
    """
    Build a Google-style site-restricted search query.
    Example: "Roland FP-30X review site:soundonsound.com OR site:sweetwater.com ..."
    """
    domains = get_trusted_domains()[:max_sites]
    site_parts = " OR ".join(f"site:{d}" for d in domains)
    return f"{product_name} review ({site_parts})"


def get_source_info(domain_or_name: str) -> Dict[str, str]:
    """Get info for a trusted source by domain or name."""
    domain_or_name_lower = domain_or_name.lower()
    for source in TRUSTED_SOURCES:
        if (
            source["domain"].lower() in domain_or_name_lower
            or source["name"].lower() in domain_or_name_lower
        ):
            return source
    return {"name": domain_or_name, "domain": "", "logo": "", "specialty": ""}


def is_trusted_domain(url: str) -> bool:
    """Check if a URL belongs to a trusted source."""
    url_lower = url.lower()
    return any(domain in url_lower for domain in TRUSTED_DOMAINS)
