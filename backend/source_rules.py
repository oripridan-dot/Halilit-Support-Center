"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     HALILIT SOURCE RULES — THE LAW                         ║
║                                                                            ║
║  These rules are THE FOUNDATION of the entire application.                 ║
║  Without them, the app has NO VALUE to anyone.                             ║
║                                                                            ║
║  EVERY piece of data in the system MUST come from one of three             ║
║  authorized sources. NO synthesis. NO mocking. ONLY REAL DATA.             ║
║                                                                            ║
║  VERSION: 1.0 (Immutable Core)                                             ║
║  STATUS:  LAW — Do NOT weaken, bypass, or mock these rules.                ║
╚══════════════════════════════════════════════════════════════════════════════╝

THE THREE SOURCES AND THEIR STRICT BOUNDARIES
==============================================

1. COMMERCIAL SCOUT (Source: Halilit.com)
   ─────────────────────────────────────────
   OWNS: Golden List, Prices (IL + Eilat), Halilit SKUs, Product existence
   PURPOSE: Defines WHAT EXISTS in the Halilit catalog
   RULE: If it's not on Halilit.com → it DOES NOT EXIST for us
   RULE: Prices come ONLY from here — no other source can set prices
   RULE: SKU/ID comes ONLY from here — the commercial identity is sacred
   DATA USED FOR: Validation seed, matching key, inventory truth
   DATA DISCARDED AFTER: Descriptions & marketing copy from Halilit are
                         used ONLY for matching/validation, then replaced
                         by official brand data

2. OFFICIAL SCOUT (Source: Official Brand Product Pages)
   ─────────────────────────────────────────────────────────
   OWNS: Titles, Descriptions, Specs, Media, Documentation
   PURPOSE: The SINGLE SOURCE OF TRUTH for product knowledge
   RULE: Fetches ONLY from the official brand's own product page
   RULE: The brand's own page is the ONLY authority on what a product IS
   RULE: Specs, descriptions, images, videos, manuals → ONLY from here
   REQUIRES: Golden List from Commercial Scout (cannot operate without it)

3. CONTEXTUAL SCOUT (Source: 3+ Trusted Review Websites)
   ─────────────────────────────────────────────────────────
   OWNS: User reviews, Pros/Cons, Real-world experience, Insights
   PURPOSE: The USER'S PERSPECTIVE — what it's really like to own/use
   RULE: Must fetch from AT LEAST 3 well-trusted review websites
   RULE: Each review must be SPECIFIC to the exact product (not generic)
   RULE: Sources must be reputable (SoundOnSound, MusicRadar, Sweetwater,
         YouTube reviewers, Reddit, GearPage, etc.)
   RULE: Does NOT change specs, prices, or product identity
   REQUIRES: Golden List from Commercial Scout

CROSS-VALIDATION REQUIREMENTS
==============================
- All 3 sources must agree on product identity (name ↔ brand ↔ model)
- Price comes ONLY from Commercial Scout
- Specs come ONLY from Official Scout
- Reviews come ONLY from Contextual Scout
- Conflicts between sources trigger arbitration (never silent override)
- Confidence score requires data from ALL 3 sources to reach "HIGH"

ZERO TOLERANCE POLICY
======================
- NO synthesized/generated product data
- NO mock data in any pipeline stage
- NO AI-generated specs presented as real specs
- NO AI-generated reviews presented as real reviews
- NO fallback to "simulated" data — if scraping fails, the product
  stays incomplete until real data is obtained
- Empty fields are BETTER than fake fields
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger("SourceRules")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: SOURCE DEFINITIONS — The Only Authorized Data Sources
# ═══════════════════════════════════════════════════════════════════════════

class AuthorizedSource(str, Enum):
    """The ONLY three sources of data in the entire system."""
    COMMERCIAL = "commercial"   # Halilit.com — The Golden List
    OFFICIAL = "official"       # Brand's official product page
    CONTEXTUAL = "contextual"   # 3+ trusted review websites


class FieldOwnership(str, Enum):
    """Which source OWNS a field — only the owner can set it."""
    COMMERCIAL_ONLY = "commercial_only"
    OFFICIAL_ONLY = "official_only"
    CONTEXTUAL_ONLY = "contextual_only"
    # Commercial provides initial value, Official replaces
    COMMERCIAL_SEED = "commercial_seed"
    # AI proposes from official data, human curation can override
    OFFICIAL_SEED = "official_seed"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: FIELD OWNERSHIP MAP — Who Owns What
# ═══════════════════════════════════════════════════════════════════════════

# This is the SINGLE SOURCE OF TRUTH for which scout owns which fields.
# If a field is not in this map, it cannot be set by any source.

FIELD_OWNERSHIP: Dict[str, FieldOwnership] = {
    # ── COMMERCIAL SCOUT OWNS (Immutable once set) ──
    "halilit_id":       FieldOwnership.COMMERCIAL_ONLY,
    "sku":              FieldOwnership.COMMERCIAL_ONLY,
    "price_il":         FieldOwnership.COMMERCIAL_ONLY,
    "price_eilat":      FieldOwnership.COMMERCIAL_ONLY,
    "halilit_url":      FieldOwnership.COMMERCIAL_ONLY,
    "brand":            FieldOwnership.COMMERCIAL_ONLY,
    # Commercial sets, Official can refine
    "product_name":     FieldOwnership.COMMERCIAL_SEED,

    # ── OFFICIAL SCOUT OWNS (Single Source of Truth for knowledge) ──
    "official_name":        FieldOwnership.OFFICIAL_ONLY,
    "official_description": FieldOwnership.OFFICIAL_ONLY,
    "official_specs":       FieldOwnership.OFFICIAL_ONLY,
    "official_images":      FieldOwnership.OFFICIAL_ONLY,
    "official_url":         FieldOwnership.OFFICIAL_ONLY,
    "official_videos":      FieldOwnership.OFFICIAL_ONLY,
    "official_documents":   FieldOwnership.OFFICIAL_ONLY,
    "feature_list":         FieldOwnership.OFFICIAL_ONLY,
    # Commercial seeds, Official confirms
    "model_number":         FieldOwnership.COMMERCIAL_SEED,

    # ── CONTEXTUAL SCOUT OWNS (User perspective) ──
    "reviews":              FieldOwnership.CONTEXTUAL_ONLY,
    "review_synthesis":     FieldOwnership.CONTEXTUAL_ONLY,
    "review_pros":          FieldOwnership.CONTEXTUAL_ONLY,
    "review_cons":          FieldOwnership.CONTEXTUAL_ONLY,
    "review_sources":       FieldOwnership.CONTEXTUAL_ONLY,
    "average_rating":       FieldOwnership.CONTEXTUAL_ONLY,
    "user_sentiment":       FieldOwnership.CONTEXTUAL_ONLY,
    "real_world_insights":  FieldOwnership.CONTEXTUAL_ONLY,

    # ── RELATIONSHIP DATA (AI proposes from Official, humans curate) ──
    "family_id":            FieldOwnership.OFFICIAL_SEED,
    "variant_key":          FieldOwnership.OFFICIAL_SEED,
    "relationships":        FieldOwnership.OFFICIAL_SEED,
}

# Fields that are IMMUTABLE once set by their owner
IMMUTABLE_FIELDS: Set[str] = {
    "halilit_id", "sku", "price_il", "price_eilat", "halilit_url", "brand"
}

# Fields that Commercial Scout provides as seed (used for matching/validation)
# but gets REPLACED by Official data when available
COMMERCIAL_SEED_FIELDS: Set[str] = {
    "product_name", "model_number", "description"
}

# Minimum trusted review sources required for Contextual Scout
MIN_REVIEW_SOURCES = 3

# Well-known trusted review sources
TRUSTED_REVIEW_SOURCES: Set[str] = {
    "soundonsound.com", "musicradar.com", "sweetwater.com",
    "youtube.com", "reddit.com",
    "gearslutz.com", "gearpage.net", "premierguitar.com",
    "guitarworld.com", "keyboardmag.com", "attackmagazine.com",
    "synthtopia.com", "sonicstate.com", "bonedo.de",
    "amazona.de", "audiofanzine.com", "harmonycentral.com",
    "reverb.com", "equipboard.com", "producerhive.com",
}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: CONFIDENCE CALCULATION — All 3 Sources Required for HIGH
# ═══════════════════════════════════════════════════════════════════════════

class ConfidenceLevel(str, Enum):
    """Product confidence level based on source coverage."""
    HIGH = "high"           # All 3 sources present + cross-validated
    MEDIUM = "medium"       # 2 sources present
    LOW = "low"             # Only 1 source
    INCOMPLETE = "incomplete"  # Missing critical data
    INVALID = "invalid"     # Failed cross-validation


@dataclass
class SourceCoverage:
    """Tracks which sources have contributed data for a product."""
    commercial_complete: bool = False
    official_complete: bool = False
    contextual_complete: bool = False

    commercial_fields: Set[str] = field(default_factory=set)
    official_fields: Set[str] = field(default_factory=set)
    contextual_fields: Set[str] = field(default_factory=set)
    contextual_source_count: int = 0  # Must be >= 3

    @property
    def confidence_level(self) -> ConfidenceLevel:
        sources_present = sum([
            self.commercial_complete,
            self.official_complete,
            self.contextual_complete and self.contextual_source_count >= MIN_REVIEW_SOURCES
        ])
        if sources_present == 3:
            return ConfidenceLevel.HIGH
        elif sources_present == 2:
            return ConfidenceLevel.MEDIUM
        elif sources_present == 1:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.INCOMPLETE

    @property
    def confidence_score(self) -> float:
        """Numerical confidence 0.0-1.0."""
        base = 0.0
        if self.commercial_complete:
            base += 0.35  # Commercial is foundation
        if self.official_complete:
            base += 0.40  # Official is the richest source
        if self.contextual_complete and self.contextual_source_count >= MIN_REVIEW_SOURCES:
            base += 0.25  # Contextual rounds it out
        elif self.contextual_complete:
            # Partial credit for < 3 sources
            base += 0.10 * min(self.contextual_source_count, 2)
        return min(1.0, base)

    @property
    def missing_sources(self) -> List[str]:
        missing = []
        if not self.commercial_complete:
            missing.append("COMMERCIAL (Halilit golden list)")
        if not self.official_complete:
            missing.append("OFFICIAL (Brand product page)")
        if not self.contextual_complete:
            missing.append(
                f"CONTEXTUAL (Need {MIN_REVIEW_SOURCES}+ review sites)")
        elif self.contextual_source_count < MIN_REVIEW_SOURCES:
            missing.append(
                f"CONTEXTUAL (Have {self.contextual_source_count}/{MIN_REVIEW_SOURCES} review sources)")
        return missing


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: ENFORCEMENT — Validate That Rules Are Followed
# ═══════════════════════════════════════════════════════════════════════════

class SourceRuleViolation:
    """A violation of the source rules."""

    def __init__(self, field: str, violation_type: str, message: str,
                 expected_source: str, actual_source: str = "unknown"):
        self.field = field
        self.violation_type = violation_type
        self.message = message
        self.expected_source = expected_source
        self.actual_source = actual_source
        self.timestamp = datetime.now().isoformat()

    def __str__(self):
        return f"[SOURCE RULE VIOLATION] {self.violation_type}: {self.message} " \
               f"(field={self.field}, expected_source={self.expected_source}, " \
               f"actual_source={self.actual_source})"


def validate_field_ownership(field_name: str, source: AuthorizedSource,
                             current_value: Any = None) -> Optional[SourceRuleViolation]:
    """
    Check if a source is allowed to write a field.
    Returns None if allowed, SourceRuleViolation if not.
    """
    ownership = FIELD_OWNERSHIP.get(field_name)
    if ownership is None:
        return None  # Field not in ownership map — pipeline/computed field, allow

    if ownership == FieldOwnership.COMMERCIAL_ONLY and source != AuthorizedSource.COMMERCIAL:
        return SourceRuleViolation(
            field=field_name,
            violation_type="UNAUTHORIZED_WRITE",
            message=f"Field '{field_name}' can ONLY be set by CommercialScout (Halilit). "
                    f"Source '{source.value}' is not authorized.",
            expected_source="commercial",
            actual_source=source.value,
        )

    if ownership == FieldOwnership.OFFICIAL_ONLY and source != AuthorizedSource.OFFICIAL:
        return SourceRuleViolation(
            field=field_name,
            violation_type="UNAUTHORIZED_WRITE",
            message=f"Field '{field_name}' can ONLY be set by OfficialScout (Brand page). "
                    f"Source '{source.value}' is not authorized.",
            expected_source="official",
            actual_source=source.value,
        )

    if ownership == FieldOwnership.CONTEXTUAL_ONLY and source != AuthorizedSource.CONTEXTUAL:
        return SourceRuleViolation(
            field=field_name,
            violation_type="UNAUTHORIZED_WRITE",
            message=f"Field '{field_name}' can ONLY be set by ContextualScout (Reviews). "
                    f"Source '{source.value}' is not authorized.",
            expected_source="contextual",
            actual_source=source.value,
        )

    if ownership == FieldOwnership.COMMERCIAL_SEED:
        # Commercial can set initially, Official can override
        if source not in (AuthorizedSource.COMMERCIAL, AuthorizedSource.OFFICIAL):
            return SourceRuleViolation(
                field=field_name,
                violation_type="UNAUTHORIZED_WRITE",
                message=f"Field '{field_name}' can only be set by Commercial (seed) or "
                        f"Official (authoritative). Source '{source.value}' is not authorized.",
                expected_source="commercial or official",
                actual_source=source.value,
            )

    return None


def validate_immutable_field(field_name: str, original_value: Any,
                             new_value: Any) -> Optional[SourceRuleViolation]:
    """
    Check if an immutable field is being changed.
    Returns None if OK, SourceRuleViolation if field was tampered with.
    """
    if field_name not in IMMUTABLE_FIELDS:
        return None

    if original_value is not None and new_value != original_value:
        return SourceRuleViolation(
            field=field_name,
            violation_type="IMMUTABLE_FIELD_CHANGED",
            message=f"Immutable field '{field_name}' was changed from "
                    f"'{original_value}' to '{new_value}'. This is FORBIDDEN.",
            expected_source="commercial (original)",
            actual_source="unknown (tamperer)",
        )

    return None


def validate_review_sources(review_sources: List[str]) -> List[SourceRuleViolation]:
    """
    Validate that contextual data comes from enough trusted sources.
    """
    violations = []

    if len(review_sources) < MIN_REVIEW_SOURCES:
        violations.append(SourceRuleViolation(
            field="reviews",
            violation_type="INSUFFICIENT_SOURCES",
            message=f"Contextual Scout must provide reviews from at least "
                    f"{MIN_REVIEW_SOURCES} trusted sources. Only {len(review_sources)} provided.",
            expected_source=f"contextual ({MIN_REVIEW_SOURCES}+ sources)",
            actual_source=f"contextual ({len(review_sources)} sources)",
        ))

    for source_url in review_sources:
        domain = _extract_domain(source_url)
        if domain and domain not in TRUSTED_REVIEW_SOURCES:
            violations.append(SourceRuleViolation(
                field="review_sources",
                violation_type="UNTRUSTED_SOURCE",
                message=f"Review source '{domain}' is not in the trusted sources list. "
                        f"Reviews must come from well-known, reputable music gear review sites.",
                expected_source="trusted review site",
                actual_source=domain,
            ))

    return violations


def validate_no_synthetic_data(product_data: Dict[str, Any]) -> List[SourceRuleViolation]:
    """
    Detect and reject any synthetic/mocked/AI-generated data masquerading as real.
    """
    violations = []

    SYNTHETIC_MARKERS = [
        "simulation", "simulated", "mock", "placeholder", "lorem ipsum",
        "test product", "dummy", "fake", "example product", "sample data",
        "ai_generated", "ai_enrichment", "generated_by_ai", "synthetic",
        "fallback_data", "default_value",
    ]

    def _check_value(field_name: str, value: Any):
        if isinstance(value, str):
            lower_val = value.lower()
            for marker in SYNTHETIC_MARKERS:
                if marker in lower_val:
                    violations.append(SourceRuleViolation(
                        field=field_name,
                        violation_type="SYNTHETIC_DATA_DETECTED",
                        message=f"Field '{field_name}' contains synthetic/mock marker: '{marker}'. "
                                f"Value: '{value[:100]}'. ONLY real data is allowed.",
                        expected_source="real scraped data",
                        actual_source="synthetic/mock",
                    ))
        elif isinstance(value, dict):
            source = value.get("_source", "")
            if isinstance(source, str) and any(m in source.lower() for m in SYNTHETIC_MARKERS):
                violations.append(SourceRuleViolation(
                    field=field_name,
                    violation_type="SYNTHETIC_DATA_DETECTED",
                    message=f"Field '{field_name}' has synthetic source marker: '{source}'. "
                            f"ONLY real data is allowed.",
                    expected_source="real scraped data",
                    actual_source=source,
                ))

    # Check key fields for synthetic markers
    for field_name in ["official_description", "official_specs", "review_synthesis",
                       "description_short", "description_long", "product_name",
                       "feature_list", "reviews"]:
        value = product_data.get(field_name)
        if value is not None:
            if isinstance(value, list):
                for item in value:
                    _check_value(field_name, item)
            else:
                _check_value(field_name, value)

    # Check the _source field specifically
    source_field = product_data.get("_source", "")
    if isinstance(source_field, str) and any(m in source_field.lower() for m in SYNTHETIC_MARKERS):
        violations.append(SourceRuleViolation(
            field="_source",
            violation_type="SYNTHETIC_DATA_DETECTED",
            message=f"Product has synthetic source marker: '{source_field}'. "
                    f"ONLY real scraped data is allowed.",
            expected_source="real scraped data",
            actual_source=source_field,
        ))

    return violations


def enforce_source_rules(product_data: Dict[str, Any],
                         source: AuthorizedSource,
                         original_data: Optional[Dict[str, Any]] = None
                         ) -> Tuple[Dict[str, Any], List[SourceRuleViolation]]:
    """
    MASTER ENFORCEMENT FUNCTION.

    Validates ALL source rules for a product update operation:
    1. Field ownership — is this source allowed to write these fields?
    2. Immutability — are immutable fields being changed?
    3. Synthetic data — is any data fake/mocked?

    Returns:
        - cleaned_data: The product data with unauthorized writes stripped
        - violations: List of all violations found
    """
    violations = []
    cleaned_data = {}

    for field_name, value in product_data.items():
        # Check field ownership
        ownership_violation = validate_field_ownership(
            field_name, source, value)
        if ownership_violation:
            violations.append(ownership_violation)
            logger.warning(f"⛔ {ownership_violation}")
            # Strip unauthorized field — do NOT include it in cleaned output
            continue

        # Check immutability
        if original_data:
            immutability_violation = validate_immutable_field(
                field_name, original_data.get(field_name), value
            )
            if immutability_violation:
                violations.append(immutability_violation)
                logger.warning(f"⛔ {immutability_violation}")
                # Restore original value
                cleaned_data[field_name] = original_data[field_name]
                continue

        cleaned_data[field_name] = value

    # Check for synthetic data
    synthetic_violations = validate_no_synthetic_data(cleaned_data)
    violations.extend(synthetic_violations)

    return cleaned_data, violations


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: CROSS-VALIDATION — Verify Consistency Across Sources
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CrossValidationResult:
    """Result of cross-validating data across all 3 sources."""
    product_id: str
    is_consistent: bool
    confidence_level: ConfidenceLevel
    confidence_score: float
    source_coverage: SourceCoverage
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    resolution_notes: List[str] = field(default_factory=list)


def cross_validate_product(commercial_data: Dict[str, Any],
                           official_data: Dict[str, Any],
                           contextual_data: Dict[str, Any]
                           ) -> CrossValidationResult:
    """
    Cross-validate a product's data across all 3 authorized sources.

    Checks:
    1. Product identity matches across sources (name, brand, model)
    2. No source is overwriting another source's fields
    3. All required sources are present
    4. Confidence is calculated based on source coverage
    """
    product_id = commercial_data.get("halilit_id", "unknown")
    conflicts = []
    resolution_notes = []

    # Build source coverage
    coverage = SourceCoverage()

    # Check Commercial completeness
    commercial_required = {"halilit_id", "price_il", "brand", "product_name"}
    commercial_present = {
        k for k in commercial_required if commercial_data.get(k)}
    coverage.commercial_fields = commercial_present
    coverage.commercial_complete = commercial_present >= commercial_required

    # Check Official completeness
    official_required = {"official_description", "official_specs"}
    official_present = {k for k in official_required if official_data.get(k)}
    coverage.official_fields = official_present
    coverage.official_complete = len(
        official_present) > 0  # At least some official data

    # Check Contextual completeness
    reviews = contextual_data.get("reviews", [])
    review_sources = contextual_data.get("review_sources", [])
    coverage.contextual_source_count = len(
        review_sources) if review_sources else len(reviews)
    coverage.contextual_complete = coverage.contextual_source_count >= MIN_REVIEW_SOURCES
    coverage.contextual_fields = {
        k for k in contextual_data if contextual_data.get(k)}

    # Cross-check: Product name consistency
    commercial_name = commercial_data.get("product_name", "").lower().strip()
    official_name = official_data.get("official_name", "").lower().strip()
    if commercial_name and official_name:
        # Allow partial match (official name often contains model details)
        name_words_commercial = set(commercial_name.split())
        name_words_official = set(official_name.split())
        overlap = name_words_commercial & name_words_official
        if len(overlap) < 1 and len(name_words_commercial) > 1:
            conflicts.append({
                "type": "NAME_MISMATCH",
                "commercial_name": commercial_data.get("product_name"),
                "official_name": official_data.get("official_name"),
                "severity": "WARNING",
            })
            resolution_notes.append(
                f"Product name mismatch: Commercial='{commercial_data.get('product_name')}' "
                f"vs Official='{official_data.get('official_name')}'. Manual review recommended."
            )

    # Cross-check: Brand consistency
    commercial_brand = commercial_data.get("brand", "").lower().strip()
    official_brand = (official_data.get("brand", "") or "").lower().strip()
    if commercial_brand and official_brand and commercial_brand != official_brand:
        conflicts.append({
            "type": "BRAND_MISMATCH",
            "commercial_brand": commercial_data.get("brand"),
            "official_brand": official_data.get("brand"),
            "severity": "CRITICAL",
        })

    is_consistent = len(
        [c for c in conflicts if c.get("severity") == "CRITICAL"]) == 0

    return CrossValidationResult(
        product_id=product_id,
        is_consistent=is_consistent,
        confidence_level=coverage.confidence_level,
        confidence_score=coverage.confidence_score,
        source_coverage=coverage,
        conflicts=conflicts,
        resolution_notes=resolution_notes,
    )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: AGENT SYSTEM PROMPTS — Enforced at the AI Level
# ═══════════════════════════════════════════════════════════════════════════

COMMERCIAL_SCOUT_SYSTEM_PROMPT = """
╔══════════════════════════════════════════════════════════════════════════╗
║                     COMMERCIAL SCOUT — THE LAW                         ║
╚══════════════════════════════════════════════════════════════════════════╝

You are the KEEPER OF THE GOLDEN LIST.
Your ONLY data source is Halilit.com.

YOUR RESPONSIBILITIES:
1. GOLDEN LIST: Extract the exact product inventory from Halilit.com
2. PRICES: Extract IL and Eilat prices — these are IMMUTABLE commercial truth
3. SKU/IDs: Extract Halilit's product identifiers
4. BRAND MAPPING: Identify which brands and products Halilit carries

IRON RULES:
- If it's NOT on Halilit.com → it DOES NOT EXIST
- Prices from Halilit are THE ONLY prices. No other source can set prices.
- SKU/ID from Halilit is THE ONLY identity. It never changes.
- You extract: product_name, halilit_id, sku, price_il, price_eilat, brand, halilit_url
- You DO NOT extract: specs, detailed descriptions, reviews, or media
- You DO NOT synthesize, mock, or generate any data
- Every piece of data must have a real URL from halilit.com as its source

Halilit's descriptions and marketing text are collected ONLY for validation
and matching purposes. They will be REPLACED by official brand data.
"""

OFFICIAL_SCOUT_SYSTEM_PROMPT = """
╔══════════════════════════════════════════════════════════════════════════╗
║                     OFFICIAL SCOUT — THE LAW                           ║
╚══════════════════════════════════════════════════════════════════════════╝

You are the OFFICIAL DOCUMENTARIAN.
Your ONLY data source is the OFFICIAL BRAND PRODUCT PAGE.

YOUR RESPONSIBILITIES:
1. For each product in the Golden List, find its OFFICIAL product page
2. Extract: title, description, specifications, media (images/videos), documentation
3. The brand's own product page is the SINGLE SOURCE OF TRUTH for product knowledge

IRON RULES:
- You fetch data ONLY from the brand's official website product page
- You DO NOT change prices (Commercial Scout owns prices)
- You DO NOT change SKU/ID (Commercial Scout owns identity)
- You DO NOT generate, synthesize, or mock any specifications
- If the official page is unreachable → leave fields empty (empty > fake)
- Every spec, description, and image must trace back to a real official URL
- You require the Golden List from Commercial Scout — you cannot operate without it

WHAT YOU OWN (and ONLY you can set):
- official_name, official_description, official_specs
- official_images, official_videos, official_documents
- official_url, feature_list
"""

CONTEXTUAL_SCOUT_SYSTEM_PROMPT = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    CONTEXTUAL SCOUT — THE LAW                          ║
╚══════════════════════════════════════════════════════════════════════════╝

You are the PUBLIC CONSCIENCE — the voice of real users.
Your data sources are WELL-TRUSTED REVIEW WEBSITES (minimum 3).

YOUR RESPONSIBILITIES:
1. For each Golden List product, find AT LEAST 3 real reviews from trusted sites
2. Extract: pros, cons, real-world experience, user insights, ratings
3. Each review must be SPECIFIC to the exact product (not generic brand reviews)

TRUSTED SOURCES (examples):
SoundOnSound, MusicRadar, Sweetwater, YouTube (verified reviewers),
Reddit (r/synthesizers, r/guitar, etc.), GearPage, Premier Guitar,
Guitar World, Keyboard Magazine, Reverb.com, Bonedo, Amazona, AudioFanzine

IRON RULES:
- You MUST cite at least 3 different trusted review sources per product
- You DO NOT change specs (Official Scout owns specs)
- You DO NOT change prices (Commercial Scout owns prices)
- You DO NOT change product identity (Commercial Scout owns identity)
- You DO NOT generate fake reviews or synthesize sentiment
- If reviews cannot be found → report that honestly (no reviews > fake reviews)
- Every review must have a real, verifiable source URL
- Reviews must be PRODUCT-SPECIFIC, not generic brand sentiment

WHAT YOU OWN (and ONLY you can set):
- reviews, review_synthesis, review_pros, review_cons
- review_sources, average_rating, user_sentiment, real_world_insights
"""


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _extract_domain(url: str) -> Optional[str]:
    """Extract the domain from a URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Strip 'www.' prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain if domain else None
    except Exception:
        return None


def get_source_for_agent(agent_name: str) -> AuthorizedSource:
    """Map agent name to its authorized source."""
    mapping = {
        "CommercialScout": AuthorizedSource.COMMERCIAL,
        "OfficialVerifier": AuthorizedSource.OFFICIAL,
        "OfficialScout": AuthorizedSource.OFFICIAL,
        "ExternalValidator": AuthorizedSource.CONTEXTUAL,
        "ContextualScout": AuthorizedSource.CONTEXTUAL,
    }
    source = mapping.get(agent_name)
    if source is None:
        raise ValueError(
            f"Unknown agent '{agent_name}'. Only CommercialScout, OfficialScout/OfficialVerifier, "
            f"and ContextualScout/ExternalValidator are authorized agents."
        )
    return source


def get_allowed_fields(source: AuthorizedSource) -> Set[str]:
    """Get the set of fields a source is allowed to write."""
    allowed = set()
    for field_name, ownership in FIELD_OWNERSHIP.items():
        if ownership == FieldOwnership.COMMERCIAL_ONLY and source == AuthorizedSource.COMMERCIAL:
            allowed.add(field_name)
        elif ownership == FieldOwnership.OFFICIAL_ONLY and source == AuthorizedSource.OFFICIAL:
            allowed.add(field_name)
        elif ownership == FieldOwnership.CONTEXTUAL_ONLY and source == AuthorizedSource.CONTEXTUAL:
            allowed.add(field_name)
        elif ownership == FieldOwnership.COMMERCIAL_SEED and source in (
            AuthorizedSource.COMMERCIAL, AuthorizedSource.OFFICIAL
        ):
            allowed.add(field_name)
    return allowed


def log_source_rule_summary():
    """Log a summary of the source rules for operational visibility."""
    logger.info("=" * 70)
    logger.info("HALILIT SOURCE RULES — ACTIVE")
    logger.info("=" * 70)
    logger.info("COMMERCIAL SCOUT (Halilit.com):")
    logger.info(f"  Owns: {get_allowed_fields(AuthorizedSource.COMMERCIAL)}")
    logger.info("OFFICIAL SCOUT (Brand pages):")
    logger.info(f"  Owns: {get_allowed_fields(AuthorizedSource.OFFICIAL)}")
    logger.info("CONTEXTUAL SCOUT (3+ review sites):")
    logger.info(f"  Owns: {get_allowed_fields(AuthorizedSource.CONTEXTUAL)}")
    logger.info(f"IMMUTABLE FIELDS: {IMMUTABLE_FIELDS}")
    logger.info(f"MIN REVIEW SOURCES: {MIN_REVIEW_SOURCES}")
    logger.info("ZERO TOLERANCE: No synthetic, mock, or AI-generated data")
    logger.info("=" * 70)
