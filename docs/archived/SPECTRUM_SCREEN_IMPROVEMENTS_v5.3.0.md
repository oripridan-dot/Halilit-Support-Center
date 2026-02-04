"""
Spectrum Data Integration Guide (v5.3.0)

This document describes the complete improvement pipeline for the Spectrum Screen's
data scraping, validation, and enrichment processes.
"""

# ============================================================================

# ARCHITECTURE OVERVIEW

# ============================================================================

## Enhanced Spectrum Data Pipeline

The improved Spectrum Screen now uses a sophisticated multi-stage pipeline:

```
PHASE 1: Scrape Halilit (Primary Source)
├── Product IDs (halilit_id)
├── Names
├── Prices (IL mainland + Eilat)
└── Stock status

    ↓

PHASE 2: Organize by Price Spectrum
├── Entry Tier (0-500₪)
├── Mid Tier (500-1500₪)
├── Pro Tier (1500-4000₪)
└── Flagship Tier (4000+₪)

    ↓

PHASE 3: Enrich with Official Sources
├── Manufacturer specs (polyphony, connectivity, power)
├── Official images
├── Warranty information
└── Product families

    ↓

PHASE 4: Enrich with Trusted Reviews
├── Thomann (EU/International)
├── Sweetwater (US/International)
├── Reverb (Community marketplace)
├── Aggregate ratings & sentiment
└── Pros/Cons analysis

    ↓

PHASE 5: Build Brand Hierarchy
├── Organize products by brand
├── Track data provenance
└── Attach quality metrics

    ↓

VALIDATION & GATES
├── Price consistency checks
├── Data completeness validation
├── Source credibility scoring
└── Quality report generation
```

# ============================================================================

# DATA STRUCTURE

# ============================================================================

## Spectrum Track (Price-Based)

```typescript
interface SpectrumTrack {
  tier: "entry" | "mid" | "pro" | "flagship";
  tier_label: string;
  price_range: [min: number, max: number];
  products: SpecProduct[];
}
```

## Spectrum Product (Enhanced)

```typescript
interface SpecProduct {
  // Halilit Direct (Primary Source)
  halilit_id: string; // Product number from Halilit
  name: string;
  brand: string;
  price_il: number; // Israeli mainland price
  price_eilat: number; // Eilat discount price

  // Official Enrichment
  official_specs?: {
    polyphony: number;
    voices?: number;
    oscillators?: number;
    filters?: number;
    connectivity: string[];
    interfaces: string[];
    power_supply: string;
    dimensions?: string;
    weight?: number;
    warranty: {
      standard_years: number;
      coverage: string;
      region: string;
    };
  };

  official_images?: Array<{
    type: "hero" | "detail" | "gallery";
    url: string;
    source: string;
  }>;

  // Review Enrichment
  review_data?: {
    sources: string[]; // ['thomann', 'sweetwater', 'reverb']
    aggregate_rating: number; // 0-5
    total_reviews: number;
    rating_distribution: {
      "5": number;
      "4": number;
      "3": number;
      "2": number;
      "1": number;
    };
    pros_and_cons: {
      pros: string[];
      cons: string[];
      verdict: string;
    };
  };

  // Provenance Tracking
  data_provenance: {
    halilit: {
      id: string;
      price: number;
      source_url: string;
      confidence: number; // 0-1
    };
    official: {
      specs: any;
      image_url?: string;
    };
    reviews: {
      data: any;
      sources: string[];
    };
  };

  sources: string[]; // ['halilit_direct', 'official_specs', 'trusted_reviews']
  quality_score: number; // 0-100
  validation_status: "APPROVED" | "REVIEW_PENDING" | "REJECTED";
}
```

# ============================================================================

# BACKEND ENDPOINTS

# ============================================================================

## GET /api/spectrum/data/{brand}

**Purpose**: Fetch complete spectrum data for a brand

**Query Parameters**:

- `include_enrichment=true` - Include official specs and reviews
- `force_refresh=false` - Skip cache and refresh all data

**Response**:

```json
{
  "brand": "Nord",
  "timestamp": "2024-02-04T12:00:00Z",
  "total_products": 12,
  "tracks": [
    {
      "tier": "entry",
      "tier_label": "Entry",
      "price_range": [0, 500],
      "products": [...]
    },
    ...
  ],
  "metadata": {
    "pipeline_version": "5.3.0",
    "processed_at": "2024-02-04T12:00:00Z",
    "data_sources": {
      "halilit_direct": "Primary source for prices and product numbers",
      "official_specs": "Manufacturer specifications",
      "trusted_reviews": "Aggregated reviews from Thomann, Sweetwater, etc."
    }
  }
}
```

## GET /api/spectrum/product/{product_id}

**Purpose**: Get detailed information for a specific product

**Response**: Single SpecProduct object with all enrichment data

## GET /api/spectrum/quality-report/{brand}

**Purpose**: Get data quality report for a brand

**Response**:

```json
{
  "brand": "Nord",
  "generated_at": "2024-02-04T12:00:00Z",
  "overall_quality_score": 95.5,
  "total_products": 12,
  "approved_products": 11,
  "rejected_products": 1,
  "critical_errors": [...],
  "warnings": [...],
  "recommendations": [...]
}
```

## GET /api/spectrum/sources/{brand}

**Purpose**: Get information about all data sources for a brand's products

**Response**:

```json
{
  "halilit": [
    {
      "source_name": "Halilit Commerce API",
      "confidence": 0.98,
      "url": "https://halilit.com"
    }
  ],
  "official": [
    {
      "source_name": "Manufacturer Official Site",
      "confidence": 0.95,
      "url": "https://official.nord.com"
    }
  ],
  "trusted_reviews": [
    {
      "source_name": "Thomann",
      "confidence": 0.90,
      "url": "https://thomann.de"
    },
    ...
  ]
}
```

## POST /api/spectrum/rebuild/{brand}

**Purpose**: Rebuild and refresh spectrum data for a brand

**Query Parameters**:

- `deep_refresh=false` - Force deep refresh of all sources

**Response**:

```json
{
  "status": "success",
  "brand": "Nord",
  "total_products": 12,
  "quality_score": 95.5,
  "validation_passed": true,
  "timestamp": "2024-02-04T12:00:00Z"
}
```

# ============================================================================

# VALIDATION RULES

# ============================================================================

## Critical Rules (Must Pass)

1. **Halilit Price Required**
   - Every product MUST have a price_il
   - Severity: CRITICAL
   - Weight: 1.0

2. **Product Name Quality**
   - Name must be > 3 characters
   - No garbage values like "Untitled", "Product", "Item A"
   - Severity: CRITICAL
   - Weight: 1.0

3. **Brand Consistency**
   - Brand must be in official taxonomy
   - Severity: HIGH
   - Weight: 0.8

## Warning Rules (Should Pass)

4. **Price Consistency**
   - Eilat price should be 75-95% of IL price
   - Deviation suggests data error
   - Severity: HIGH
   - Weight: 0.8

5. **Source Credibility**
   - At least one credible source must be present
   - Credible = halilit_direct or official_specs
   - Severity: MEDIUM
   - Weight: 0.6

6. **Data Provenance**
   - All data must have provenance tracking
   - Users can see source of each field
   - Severity: MEDIUM
   - Weight: 0.5

## Quality Score Calculation

```
quality_score = 100
quality_score -= (products_with_critical_errors * 10)
quality_score -= (products_with_warnings * 3-5)
quality_score = clamp(0, 100)
```

# ============================================================================

# FRONTEND INTEGRATION

# ============================================================================

## useSpectrumData Hook

```typescript
const { data, loading, error, retry } = useSpectrumData(brand, {
  include_enrichment: true,
  force_refresh: false,
});

// data.tracks: PriceTrack[]
// data.metadata: SpectrumMetadata
```

## EnrichmentPanel Component

Displays enrichment data in the Spectrum Module's middle panel:

```tsx
<EnrichmentPanel product={hoveredProduct} />
```

Shows:

- Official specs (with icons)
- Review ratings and sentiment
- Data source badges
- Confidence indicators

## DataSourcesBadge Component

Visual badges showing where data comes from:

- 🇮🇱 Halilit (Blue) - Price and product number
- ✓ Official (Green) - Manufacturer specifications
- ★ Reviews (Amber) - Trusted review sites

# ============================================================================

# SKILLS & VALIDATION PIPELINE

# ============================================================================

## Core Skills

### 1. SpectrumDataPipeline

**File**: `backend/skills/spectrum_data_pipeline.py`

Orchestrates the 5-phase data aggregation:

- Scrapes Halilit data
- Organizes by price spectrum
- Enriches with official sources
- Enriches with reviews
- Builds brand hierarchy
- Attaches provenance

### 2. SpectrumValidator

**File**: `backend/skills/spectrum_validator.py`

Validates spectrum data against rules:

- Checks critical fields
- Validates price consistency
- Scores source credibility
- Generates quality reports

### 3. OfficialSpecsEnricher

**File**: `backend/skills/spectrum_enrichment.py`

Fetches manufacturer specifications:

- Connects to official APIs
- Extracts technical specs
- Fetches official images
- Caches results

### 4. TrustedReviewAggregator

**File**: `backend/skills/spectrum_enrichment.py`

Aggregates reviews from trusted sources:

- Thomann (35% weight)
- Sweetwater (35% weight)
- Reverb (20% weight)
- Gearspace (10% weight)

Calculates:

- Weighted average rating
- Sentiment analysis
- Pros/Cons aggregation

### 5. SpecificationNormalizer

**File**: `backend/skills/spectrum_enrichment.py`

Normalizes specs across sources:

- Unit conversions (cm, kg, etc.)
- Standardized field names
- Data type consistency
- Category-specific specs

# ============================================================================

# DATA SOURCES & CONFIDENCE

# ============================================================================

## Source Priority & Confidence Scores

| Source              | Priority | Confidence | Used For                          |
| ------------------- | -------- | ---------- | --------------------------------- |
| Halilit Direct      | 100      | 0.98       | Price, Product ID, Name           |
| Official Specs      | 80       | 0.95       | Technical specs, Warranty, Images |
| Thomann Reviews     | 70       | 0.90       | Ratings, Reviews, Pros/Cons       |
| Sweetwater Reviews  | 70       | 0.90       | Ratings, Reviews, Pros/Cons       |
| Reverb Reviews      | 70       | 0.85       | Community feedback                |
| Gearspace Community | 60       | 0.80       | User discussions                  |
| Cache/Legacy        | 10       | 0.50       | Fallback only                     |

## Conflict Resolution Strategy

When data conflicts between sources:

1. Use highest priority source
2. If same priority, use highest confidence
3. If same confidence, use most recent update
4. Flag conflicts for manual review

# ============================================================================

# USAGE EXAMPLES

# ============================================================================

## Fetch Spectrum Data in Frontend

```typescript
import { useSpectrumData } from '../../hooks/useSpectrumData';

export const MyComponent = ({ brand }) => {
  const { data, loading, error } = useSpectrumData(brand, {
    include_enrichment: true
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data.tracks.map(track => (
        <div key={track.tier}>
          <h3>{track.tier_label}</h3>
          {track.products.map(product => (
            <div key={product.halilit_id}>
              <h4>{product.name}</h4>
              <p>Price: {product.price_il}₪</p>
              {product.review_data && (
                <p>Rating: {product.review_data.aggregate_rating}/5</p>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
```

## Validate and Generate Report in Backend

```python
from backend.skills.spectrum_data_pipeline import SpectrumDataPipeline
from backend.skills.spectrum_validator import SpectrumValidator, QualityReportGenerator

# Phase 1: Pipeline
pipeline = SpectrumDataPipeline()
success, payload = pipeline.execute({
    'brand': 'Nord',
    'include_enrichment': True
})

# Phase 2: Validate
validator = SpectrumValidator()
valid, results = validator.execute({
    'payload': payload,
    'brand_taxonomy': ['Nord', 'Moog', 'Roland', ...]
})

# Phase 3: Generate Report
generator = QualityReportGenerator()
report_success, report = generator.execute({
    'validation_results': results,
    'brand': 'Nord'
})

print(f"Quality Score: {report['summary']['overall_quality']}")
print(f"Recommendations: {report['recommendations']}")
```

# ============================================================================

# PERFORMANCE CONSIDERATIONS

# ============================================================================

## Caching Strategy

- **Halilit data**: Cache for 1 hour (frequent changes)
- **Official specs**: Cache for 24 hours (rarely change)
- **Reviews**: Cache for 6 hours (updated regularly)
- **Processed tracks**: Cache for 30 minutes

## Parallel Processing

The pipeline uses parallel skill execution where possible:

- Official specs and reviews fetched in parallel
- Multiple brands processed concurrently
- Validation done incrementally

## Optimization

- Lazy-load images (use thumbnail URLs)
- Pagination for large product lists
- Compression for API responses
- Progressive enrichment (show Halilit data first, enrich as data arrives)

# ============================================================================

# TROUBLESHOOTING

# ============================================================================

## Common Issues

### Low Quality Scores

**Symptoms**: Quality score < 80

**Causes**:

- Missing Halilit prices
- Inconsistent price ratios (IL vs Eilat)
- Missing product names or descriptions

**Solution**:

1. Check Halilit data scraping
2. Validate price formatting
3. Review data source quality

### Missing Enrichment Data

**Symptoms**: No official specs or reviews showing

**Causes**:

- Official API unavailable
- Product not found in trusted sources
- API rate limiting

**Solution**:

1. Check manufacturer API status
2. Verify product name matching
3. Monitor API quotas
4. Use fallback data

### Validation Failures

**Symptoms**: Products rejected with errors

**Causes**:

- Critical field missing
- Invalid price data
- Unknown brand

**Solution**:

1. Review validation rules
2. Fix source data
3. Update brand taxonomy
4. Adjust confidence thresholds

# ============================================================================

# FUTURE ENHANCEMENTS

# ============================================================================

- [ ] Real-time data streaming from Halilit
- [ ] ML-based price outlier detection
- [ ] Automatic competitor price tracking
- [ ] Sentiment analysis from user comments
- [ ] Predictive stock management
- [ ] Dynamic tier boundaries based on market
- [ ] A/B testing for data presentation
- [ ] Integration with inventory systems

"""
