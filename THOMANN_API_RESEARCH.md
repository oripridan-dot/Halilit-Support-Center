# Thomann API & Data Access Research

**Research Date**: February 8, 2026  
**Status**: No Official API Available

---

## Summary

**Thomann (thomannmusic.com) does NOT provide:**

- ✗ Official public REST API for product data
- ✗ Partner/affiliate API with product catalog access
- ✗ CSV exports or bulk data feeds
- ✗ Product database access for third-party integrations
- ✗ Structured data feeds for syndication

**The only viable approach for product data**: Web scraping

---

## 1. Official API Documentation

### Status: ❌ NO OFFICIAL API

**Findings:**

- Thomann has **no documented REST API** for product access
- Their developer portal (if it exists) does not include product catalog endpoints
- All documentation is limited to internal operations

**References:**

- No public API docs at `api.thomann.com` or similar
- Thomann support pages do not mention API access for partners
- No GitHub repositories with Thomann API SDKs

---

## 2. Partner/Affiliate API

### Status: ❌ NO AFFILIATE API FOR DATA ACCESS

**What Thomann Has:**

- ✓ Affiliate program (commission-based referrals)
- ✓ Affiliate dashboard for commission tracking
- ✗ **NO affiliate API for product data** (tracking/attribution only)

**Limitations:**

- Affiliate program is for _referral links_, not product catalog access
- Affiliates cannot access:
  - Real-time product catalogs
  - Bulk product data export
  - Price feeds
  - Stock levels
  - SKU data

**Reference:** Thomann Affiliate Terms typically restrict data to:

- Unique referral links (for commission tracking)
- Dashboard analytics (for affiliate earnings)
- Banner assets for marketing

---

## 3. Alternative Data Sources

### Option A: Web Scraping (Current Codebase Approach)

**What Exists in this Repo:**

- The `backend/thomann_comparison.py` module expects pre-cached Thomann data
- Data structure: `{model: {price_eur, weight_kg, ...}}`
- **Current implementation is comparison-only** — doesn't fetch live Thomann data

**Is Web Scraping Legal?**

- **Risked**: Thomann's Terms of Service likely prohibit scraping
- **Consider**: Thomann is very strict about automated access
- **Best Practice**: Only enterprise partnerships have data access

### Option B: Manual Data Sources

**CSV/Export Alternatives:**

- Thomann does not provide official CSV exports
- Some competitors (Sweetwater, Gear4music) offer API or bulk download options
- **Status**: Not available for Thomann

### Option C: Third-Party Aggregators

**Tools that may have Thomann data:**

- **Discogs** - Limited music equipment, not full catalog
- **PriceGrabber/shopping.com** - May index Thomann prices
- **Keepa/CamelCamelCamel** - Not applicable (music gear, not Amazon)
- **MusicRadar** - Reviews only, not API

**⚠️ Limitation:** Third-party aggregators also respect Thomann's restrictions

---

## 4. Python Libraries for Scraping

### Available Libraries (if scraping were to be attempted)

```python
import requests                # HTTP client
from bs4 import BeautifulSoup  # HTML parsing
import selenium                # JavaScript rendering
import scrapy                  # Full scraping framework
```

**Current Codebase Uses:**

```python
# From backend/scrapers/halilit_scraper.py
import requests
from bs4 import BeautifulSoup

# Not used for Thomann (would require JavaScript rendering)
```

### Why Scraping Thomann is Difficult

**Technical Barriers:**

1. **JavaScript-Heavy Site**: Thomann heavily relies on client-side rendering
   - Product data loaded via JavaScript
   - Page content not in HTML source
   - Requires Selenium or Playwright

2. **Dynamic Pricing**: Prices calculated client-side
   - EUR to user currency conversion
   - Real-time VAT calculation
   - Regional pricing

3. **Anti-Scraping Measures**:
   - Cloudflare protection
   - IP rate limiting
   - User-agent validation
   - Session cookies required

**Required Stack for Scraping:**

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Would need headless browser + JavaScript execution
# Plus handling Cloudflare challenges
```

---

## 5. Valid Product Category URLs

### Thomann Site Structure (No API, Static URLs)

**Pattern**: `https://www.thomannmusic.com/{language}/{category}-products`

**Example Brand Category URLs:**

| Brand        | URL Pattern                                      |
| ------------ | ------------------------------------------------ |
| **Montarbo** | `https://thomannmusic.com/montarbo-loudspeakers` |
| **RCF**      | `https://thomannmusic.com/rcf-pa-systems`        |
| **EAW**      | `https://thomannmusic.com/eaw-pro-audio`         |
| **Mackie**   | `https://thomannmusic.com/mackie-mixers`         |

### ⚠️ Important Note: These URLs Require JavaScript

**Why:**

- Product listing is rendered client-side
- HTML source contains no product data
- `requests.get()` alone will not work
- **Must use Selenium/Playwright/Puppeteer**

### Example Non-JavaScript Endpoint (Not Applicable to Thomann)

```
# Static HTML category page (DOESN'T EXIST for Thomann)
https://thomannmusic.com/categories/montarbo-speakers?view=list&sort=price

# What you actually get:
<div id="app"></div>
<script src="main.bundle.js"></script>
<!-- All product data loaded by JavaScript -->
```

---

## 6. Current Implementation in This Codebase

### What's Implemented

**File**: `backend/thomann_comparison.py`

```python
class ThomannComparison:
    """Main comparison engine"""

    def compare_brand_catalog(
        self,
        brand: str,
        halilit_products: List[Dict],
        thomann_products_map: Optional[Dict[str, Dict]] = None  # <- Pre-cached
    ) -> Dict:
```

**Key Points:**

- ✓ Expects **pre-cached Thomann data** (not fetched live)
- ✓ Performs price comparison with VAT + shipping
- ✓ Converts EUR → ILS using fixed rate (4.2)
- ✓ Model matching with confidence scoring

**Data Schema Expected:**

```json
{
  "montarbo_nettuno_20": {
    "price_eur": 2150,
    "weight_kg": 35,
    "sku": "..."
  },
  "rcf_l8": {
    "price_eur": 1890,
    "weight_kg": 45
  }
}
```

### What's NOT Implemented

- ❌ Live Thomann scraper
- ❌ API client for Thomann (doesn't exist)
- ❌ JavaScript rendering for dynamic pricing
- ❌ Real-time price synchronization

---

## 7. Recommendations

### ✅ Best Practices (Given Thomann's Restrictions)

1. **For Real-Time Pricing**:
   - Manual data collection for high-value products
   - Quarterly/annual spot checks
   - Partner directly with Thomann if volume justifies

2. **For Development/Testing**:
   - Mock/cache Thomann data as **backend/thomann_comparison.py** already does
   - Create test fixtures from historical pricing
   - Build comparison features with cached data

3. **Legal/Ethical Approach**:
   - Use Halilit.com as the single source of truth
   - Manual pricing research for competitor analysis
   - Consider Thomann as a reference point, not a data source
   - Avoid automated scraping

### ❌ What NOT to Do

- ❌ Do not build a live Thomann scraper (violates ToS)
- ❌ Do not use Selenium to bypass Cloudflare
- ❌ Do not republish Thomann prices without permission
- ❌ Do not try to find hidden APIs (they don't exist)

---

## Conclusion

| Question                                          | Answer                                                      |
| ------------------------------------------------- | ----------------------------------------------------------- |
| **Does Thomann have an official API?**            | ❌ No                                                       |
| **Does Thomann have an affiliate API?**           | ❌ No (referrals only)                                      |
| **Are there CSV exports available?**              | ❌ No                                                       |
| **Can you scrape Thomann legally?**               | ⚠️ No (against ToS)                                         |
| **What data structure is needed for comparison?** | Pre-cached `{model: {price_eur, weight_kg}}`                |
| **Are the category URLs static?**                 | ✓ Yes, but they require JavaScript to render                |
| **What Python library should be used?**           | BeautifulSoup + Requests (won't work for Thomann due to JS) |

---

## Related Files in This Codebase

- [backend/thomann_comparison.py](backend/thomann_comparison.py) - Price comparison (expects pre-cached data)
- [THOMANN_COMPARISON_REPORT.md](THOMANN_COMPARISON_REPORT.md) - Full comparison system documentation
