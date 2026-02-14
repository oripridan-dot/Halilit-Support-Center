import re
import logging
from typing import List, Optional
from backend.ingestion.data_models import IngestionProductDraft

logger = logging.getLogger("Guardrails")


def verify_critical_facts(draft: IngestionProductDraft) -> List[str]:
    """
    Deterministic "Critic" layer that runs after AI but before saving.
    Uses non-AI logic (Regex, exact matching) to verify critical facts.
    Returns a list of error messages (empty if valid).
    """
    errors = []

    # Ensure raw snapshot exists
    raw_data = draft.raw_snapshot or {}

    # 1. Price Safety Check
    # We trust 'price_il' in the draft (from golden list/harvest phase)
    # But we double check against any raw text if available to ensure no drift occurred during "enrichment"
    # if it was mutable. In the current pipeline, 'price_il' is marked IMMUTABLE in harvest phase.
    # However, let's verify if the draft price matches the raw data price if clearly present.

    raw_price_val = raw_data.get('price') or raw_data.get('price_il')
    if raw_price_val is not None:
        try:
            # Normalize raw price to float
            raw_float = float(str(raw_price_val).replace(
                ',', '').replace('₪', '').strip())

            # Allow for minor floating point differences, but strict equality for business logic
            if abs(raw_float - draft.price_il) > 1.0:
                errors.append(
                    f"CRITICAL: Price mismatch! Raw: {raw_float}, Draft: {draft.price_il}")
        except ValueError:
            pass  # Raw price might be "Call for price" or complex string, skip regex check if specific key fails parsing

    # 2. SKU/ID Integrity Check
    raw_id = raw_data.get('halilit_id') or raw_data.get('sku')
    if raw_id:
        if str(raw_id).strip() != str(draft.halilit_id).strip():
            errors.append(
                f"CRITICAL: ID Mismatch! Raw: {raw_id}, Draft: {draft.halilit_id}")

    # 3. Hallucination Check - Product Name
    # The name in the draft should bear significant resemblance to raw name
    raw_name = raw_data.get('name') or raw_data.get('title')
    if raw_name:
        # Simple containment check (case insensitive)
        # If the draft name doesn't contain the raw name (or vice versa), flag it.
        # This is a loose check because AI might clean up the name.
        d_name = draft.product_name.lower()
        r_name = str(raw_name).lower()

        # Split into tokens to check overlap
        d_tokens = set(re.findall(r'\w+', d_name))
        r_tokens = set(re.findall(r'\w+', r_name))

        common = d_tokens.intersection(r_tokens)
        if len(common) < len(r_tokens) * 0.5:  # If less than 50% of raw words are in draft
            logger.warning(
                f"Potential hallucination or heavy rename: Raw '{raw_name}' -> Draft '{draft.product_name}'")
            # We might not want to hard fail on name cleanup, but log it.
            # If strictly required: errors.append(...)

    return errors


def regex_extract_price(text: str) -> Optional[float]:
    """
    Extract price from text using Regex.
    """
    if not text:
        return None
    # Pattern for NIS price
    match = re.search(r'₪?([\d,]+\.?\d*)', text)
    if match:
        try:
            return float(match.group(1).replace(',', ''))
        except ValueError:
            return None
    return None
