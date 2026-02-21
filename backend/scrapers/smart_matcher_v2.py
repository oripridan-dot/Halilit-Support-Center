#!/usr/bin/env python3
import csv
import json
import re
import logging
from pathlib import Path
from difflib import SequenceMatcher

# Configuration
VAT_RATE = 0.17  # Official Israel VAT is 17%. User said "without 18% VAT"
VAT_DIVISOR = 1.18
IMPORT_VAT_RATE = 0.18  # Use consistent 18% as requested

SHIPPING_COST_USD = 50.0  # Estimated flat rate for pro audio gear to Israel
USD_ILS_RATE = 3.65

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


def clean_thomann_name(raw_name):
    """
    Clean the dirty Thomann names like '40RCFArt 715-A MK V$619'
    Target: 'Art 715-A MK V'
    """
    # Remove price at end ($...)
    name = re.sub(r'\$[\d,.]+$', '', raw_name)
    # Remove leading numbers/rank
    name = re.sub(r'^\d+', '', name)
    # Fix glued brand names (generic)
    name = re.sub(r'(RCF|Mackie)([A-Za-z0-9])',
                  r'\1 \2', name, flags=re.IGNORECASE)
    return name.strip()


def extract_signature(name):
    """
    Create a set of significant tokens for matching.
    """
    clean = name.lower()

    # Normalize versions
    clean = clean.replace('mk v', 'mk5').replace(
        'gen 3', 'gen3').replace('mk 5', 'mk5')
    clean = clean.replace('v3', 'v3').replace('mk3', 'mk3')

    # Remove Brand names to avoid matching just on "Mackie"
    clean = re.sub(r'\b(rcf|mackie)\b', '', clean)

    # Normalize hyphens/slashes to spaces
    clean = clean.replace('-', ' ').replace('/', ' ')

    # Extract alphanumeric tokens
    tokens = re.findall(r'[a-z0-9\-\.]+', clean)

    # Filter stopwords - generic terms that cause false positives
    stopwords = {
        'active', 'passive', 'speaker', 'monitor', 'studio', 'usb',
        'pro', 'pair', 'system', 'subwoofer', 'mixer', 'analog',
        'digital', 'cover', 'bag', 'case', 'protection', 'compact',
        'professional', 'audio', 'black', 'white', 'channel', 'ch',
        'kit', 'cart', 'line', 'array', 'series', 'module', 'bundle'
    }

    significant = {t for t in tokens if t not in stopwords and len(t) > 1}

    # Extract isolated numbers (very important for model numbers)
    # Distinguish "Big Numbers" (Model IDs like 710, 715) from "Small Numbers" (Versions like 3, 5)
    all_nums = re.findall(r'\d+', clean)
    primary_nums = {n for n in all_nums if len(
        n) >= 3}  # e.g. 710, 715, 912, 215
    version_nums = {n for n in all_nums if len(n) < 3}  # e.g. 3, 4, 5, 10, 12

    return significant, primary_nums, version_nums


def calculate_match_score(halilit_name, thomann_name):
    """
    Strict scoring:
    - Primary Model Numbers (>=3 digits) MUST match exactly if present.
    - If one has '710' and other '715', Match = 0.
    """
    h_toks, h_prim, h_ver = extract_signature(halilit_name)
    t_toks, t_prim, t_ver = extract_signature(thomann_name)

    # CRITICAL: Primary Number Logic (Strict)
    if h_prim or t_prim:
        # If both have primary numbers, they must match exactly
        if h_prim and t_prim:
            if not h_prim.intersection(t_prim):
                return 0  # Mismatch (e.g. 710 vs 715)

        # If one has primary numbers and the other doesn't?
        # e.g. "ART 715" vs "ART Speaker" -> Unlikely match.
        if (h_prim and not t_prim) or (t_prim and not h_prim):
            return 0.2

    # Token Overlap
    if not h_toks or not t_toks:
        return 0

    intersection = h_toks.intersection(t_toks)
    union = h_toks.union(t_toks)
    jaccard = len(intersection) / len(union)

    # Penalize heavily if "Cover" or "Bag" status mismatches (Keyword Guardrails)
    h_acc = any(x in halilit_name.lower()
                for x in ['cover', 'bag', 'case', 'cart', 'stand', 'kit'])
    t_acc = any(x in thomann_name.lower()
                for x in ['cover', 'bag', 'case', 'cart', 'stand', 'kit'])

    if h_acc != t_acc:
        return 0  # Immediate disqualification

    return jaccard


def main():
    base_path = Path('/workspaces/Halilit-Support-Center/backend')

    # 1. Load Halilit Data (Source of Truth for Catalog)
    halilit_products = []

    input_csv = base_path / 'reports/HALILIT_THOMANN_WITH_PRICES.csv'
    if not input_csv.exists():
        print("Error: Input CSV not found.")
        return

    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            halilit_products.append(row)

    print(f"Loaded {len(halilit_products)} source products from Halilit.")

    # 2. Load Thomann Catalog
    thomann_catalog = []
    for brand in ['rcf', 'mackie']:
        json_path = base_path / f'scrapers/thomann_{brand}_full.json'
        try:
            with open(json_path, 'r') as f:
                items = json.load(f)
                for item in items:
                    if item.get('price', 0) > 0:
                        item['clean_name'] = clean_thomann_name(item['name'])
                        thomann_catalog.append(item)
        except Exception:
            pass

    print(f"Loaded {len(thomann_catalog)} Thomann products for matching.")

    # 3. Match and Calculate
    results = []

    for h_item in halilit_products:
        h_name = h_item['Halilit_Product']
        # Parse Price
        h_price_str = str(h_item.get('Halilit_Price_ILS', '')).replace(
            '₪', '').replace(',', '').strip()
        try:
            h_price_ils = float(
                h_price_str) if 'TBD' not in h_price_str and h_price_str else 0
        except:
            h_price_ils = 0

        best_match = None
        best_score = 0

        for t_item in thomann_catalog:
            # Brand Filter
            if 'Mackie' in h_name and 'Mackie' not in t_item['name']:
                continue
            if 'RCF' in h_name and 'RCF' not in t_item['name']:
                continue

            score = calculate_match_score(h_name, t_item['clean_name'])

            if score > best_score:
                best_score = score
                best_match = t_item

        # High Threshold for Strictness
        if best_score < 0.6:
            best_match = None

        # Pricing Calculations
        # user asked for "prices with and without 18% VAT"
        h_price_ex_vat = h_price_ils / VAT_DIVISOR

        if best_match:
            t_price_usd = float(best_match['price'])
            t_shipping_usd = SHIPPING_COST_USD

            # Thomann landed scheme:
            # Price + Shipping
            # + 18% VAT on total
            base_usd = t_price_usd + t_shipping_usd
            vat_usd = base_usd * IMPORT_VAT_RATE
            total_usd = base_usd + vat_usd
            total_ils = total_usd * USD_ILS_RATE

            gap = h_price_ils - total_ils
            margin_pct = (gap / total_ils * 100) if total_ils > 0 else 0

            t_name = best_match['clean_name']
            t_url = best_match.get('url', '')
            match_status = "Match"
        else:
            t_price_usd = 0
            t_shipping_usd = 0
            vat_usd = 0
            total_ils = 0
            gap = 0
            margin_pct = 0
            t_name = "N/A"
            t_url = ""
            match_status = "No Match"

        # Format Outputs
        results.append({
            'Brand': h_item['Brand'],
            'Halilit_Name': h_name,
            'Halilit_Price_ILS_IncVAT': f"₪{int(h_price_ils)}",
            'Halilit_Price_ILS_ExVAT': f"₪{int(h_price_ex_vat)}",

            'Thomann_Name': t_name,
            'Match_Score': f"{int(best_score * 100)}%",
            'Thomann_Price_USD': f"${int(t_price_usd)}" if best_match else "N/A",
            'Thomann_Shipping_USD': f"${int(t_shipping_usd)}" if best_match else "N/A",
            'Thomann_VAT_USD': f"${int(vat_usd)}" if best_match else "N/A",
            'Thomann_Total_Landed_ILS': f"₪{int(total_ils)}" if best_match else "N/A",

            'Price_Gap_ILS': f"₪{int(gap)}" if best_match else "N/A",
            'Margin_Pct': f"{int(margin_pct)}%" if best_match else "N/A",
            'Thomann_URL': t_url
        })

    # 4. Write CSV
    output_path = base_path / 'reports/SMART_COMPARISON_v2.csv'
    fieldnames = [
        'Brand', 'Halilit_Name', 'Halilit_Price_ILS_IncVAT', 'Halilit_Price_ILS_ExVAT',
        'Thomann_Name', 'Match_Score',
        'Thomann_Price_USD', 'Thomann_Shipping_USD', 'Thomann_VAT_USD', 'Thomann_Total_Landed_ILS',
        'Price_Gap_ILS', 'Margin_Pct', 'Thomann_URL'
    ]

    with open(output_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Success! Smart report generated at: {output_path}")


if __name__ == "__main__":
    main()
