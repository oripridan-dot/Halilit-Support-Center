"""
Trusted Sources — The "Golden Circle" of authoritative review sources.

Only these domains are allowed to be cited by the JIT agent.
Organized by credibility tier:
  Tier 1: Professional editorial reviews (Sound On Sound, MusicRadar, etc.)
  Tier 2: Retailer authority reviews (Sweetwater, Thomann)
  Tier 3: Community & data sources (Gearspace, Equipboard, Reddit)
"""

from dataclasses import dataclass, field


@dataclass
class TrustedSource:
    domain: str
    name: str
    tier: int  # 1=professional, 2=retailer, 3=community
    logo_key: str  # for frontend logo lookup
    search_label: str  # human-friendly label


# ── The Golden Circle ──

TRUSTED_SOURCES: list[TrustedSource] = [
    # Tier 1 — Professional Editorial
    TrustedSource("soundonsound.com", "Sound On Sound",
                  1, "sos", "Sound On Sound"),
    TrustedSource("musicradar.com", "MusicRadar",
                  1, "musicradar", "MusicRadar"),
    TrustedSource("attackmagazine.com", "Attack Magazine",
                  1, "attack", "Attack Magazine"),
    TrustedSource("sonicstate.com", "Sonic State",
                  1, "sonicstate", "Sonic State"),
    TrustedSource("mixonline.com", "Mix Magazine", 1, "mix", "Mix Magazine"),
    TrustedSource("musictech.com", "MusicTech", 1, "musictech", "MusicTech"),

    # Tier 2 — Retailer Authority
    TrustedSource("sweetwater.com", "Sweetwater",
                  2, "sweetwater", "Sweetwater"),
    TrustedSource("thomann.de", "Thomann", 2, "thomann", "Thomann"),

    # Tier 3 — Community & Data
    TrustedSource("equipboard.com", "Equipboard",
                  3, "equipboard", "Equipboard"),
    TrustedSource("modulargrid.net", "ModularGrid",
                  3, "modulargrid", "ModularGrid"),
    TrustedSource("gearspace.com", "Gearspace", 3, "gearspace", "Gearspace"),
    TrustedSource("reddit.com", "Reddit", 3, "reddit", "Reddit"),
]

# Quick lookup
TRUSTED_DOMAINS = {s.domain for s in TRUSTED_SOURCES}
TRUSTED_BY_DOMAIN = {s.domain: s for s in TRUSTED_SOURCES}


def get_search_site_filter(tiers: list[int] | None = None) -> str:
    """
    Build a Google/Serper site: filter string for trusted sources.

    Args:
        tiers: Optional list of tiers to include. None = all tiers.

    Returns:
        String like "site:soundonsound.com OR site:musicradar.com OR ..."
    """
    sources = TRUSTED_SOURCES
    if tiers:
        sources = [s for s in sources if s.tier in tiers]
    return " OR ".join(f"site:{s.domain}" for s in sources)


def get_review_search_query(product_name: str, tiers: list[int] | None = None) -> str:
    """Build a complete search query for trusted reviews of a product."""
    site_filter = get_search_site_filter(tiers or [1, 2])
    return f'({site_filter}) "{product_name}" review'


def is_trusted_url(url: str) -> bool:
    """Check if a URL belongs to a trusted source."""
    return any(domain in url for domain in TRUSTED_DOMAINS)


def identify_source(url: str) -> TrustedSource | None:
    """Identify which trusted source a URL belongs to."""
    for domain, source in TRUSTED_BY_DOMAIN.items():
        if domain in url:
            return source
    return None
