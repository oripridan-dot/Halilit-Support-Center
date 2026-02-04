# Spectrum Screen v5.3.0 - Quick Reference Guide

## 🚀 Quick Start

### Backend Setup

```bash
# The spectrum router is already integrated into server.py
# Just run the server:
cd /workspaces/Halilit-Support-Center
PYTHONPATH=. python backend/server.py
```

### Test Data Pipeline

```bash
# Run the conductor to verify all data
python backend/conductor_spectrum.py verify

# Verify specific brand
python backend/conductor_spectrum.py verify Nord

# Rebuild brand data
python backend/conductor_spectrum.py rebuild Nord --deep
```

### Frontend Integration

```typescript
import { useSpectrumData } from "../../hooks/useSpectrumData";

const { data, loading, error } = useSpectrumData("Nord", {
  include_enrichment: true,
  force_refresh: false,
});
```

## 📊 API Endpoints

### Get Spectrum Data

```
GET /api/spectrum/data/{brand}
?include_enrichment=true
&force_refresh=false

Example:
GET /api/spectrum/data/Nord?include_enrichment=true
```

### Get Quality Report

```
GET /api/spectrum/quality-report/{brand}

Example:
GET /api/spectrum/quality-report/Nord
```

### Get Data Sources

```
GET /api/spectrum/sources/{brand}

Example:
GET /api/spectrum/sources/Nord
```

### Rebuild Data

```
POST /api/spectrum/rebuild/{brand}
?deep_refresh=false

Example:
POST /api/spectrum/rebuild/Nord?deep_refresh=true
```

## 🎯 Data Structure

### Product Object

```typescript
{
  // From Halilit
  halilit_id: string;        // Product number
  price_il: number;          // Israeli price
  price_eilat: number;       // Eilat discount

  // From Official Sources
  official_specs: {
    polyphony: number;
    connectivity: string[];
    power_supply: string;
    // ... more fields
  };

  // From Reviews
  review_data: {
    aggregate_rating: number;
    total_reviews: number;
    pros_and_cons: {
      pros: string[];
      cons: string[];
    };
  };

  // Tracking
  sources: string[];         // ['halilit_direct', 'official_specs', 'trusted_reviews']
  quality_score: number;     // 0-100
  validation_status: string; // 'APPROVED', 'REVIEW_PENDING', 'REJECTED'
}
```

## 🔍 Validation Rules

### Critical (Must Pass)

- ✅ Halilit price is required
- ✅ Product name > 3 characters
- ✅ Brand is in taxonomy

### Warnings (Should Pass)

- ⚠️ Price consistency (Eilat 75-95% of IL)
- ⚠️ At least one credible source
- ⚠️ Data provenance present

## 📈 Quality Score Calculation

```
Base: 100
- Critical errors: -10 each
- Warnings: -3 to -5 each
Final: clamp(0, 100)

Score Interpretation:
90-100: Excellent
80-89:  Good
70-79:  Acceptable
60-69:  Needs Attention
<60:    Poor
```

## 🎨 Frontend Components

### DataSourcesBadge

Shows visual indicators of data sources:

- 🇮🇱 Halilit (Blue)
- ✓ Official (Green)
- ★ Reviews (Amber)

### EnrichmentPanel

Displays enrichment data in spec viewer:

- Official specifications
- Review ratings and sentiment
- Data provenance information

### SpectrumModule

Enhanced to show:

- Products organized by price tier
- Enrichment data on hover
- Source attribution
- Quality metrics

## 🔄 Data Pipeline Phases

```
1. SCRAPE HALILIT
   ↓ (prices, IDs)

2. ORGANIZE BY PRICE
   ↓ (entry/mid/pro/flagship)

3. ENRICH OFFICIAL
   ↓ (specs, images)

4. ENRICH REVIEWS
   ↓ (ratings, sentiment)

5. BUILD HIERARCHY
   ↓ (by brand)

6. VALIDATE & REPORT
   ↓ (quality checks)
```

## 🔗 Data Sources & Confidence

| Source     | Confidence | Used For        |
| ---------- | ---------- | --------------- |
| Halilit    | 0.98       | Price, ID, Name |
| Official   | 0.95       | Specs, Images   |
| Thomann    | 0.90       | Reviews         |
| Sweetwater | 0.90       | Reviews         |
| Reverb     | 0.85       | Reviews         |

## 📁 Key Files

**Backend Skills**:

- `backend/skills/spectrum_data_pipeline.py` - Main pipeline
- `backend/skills/spectrum_validator.py` - Validation & reporting
- `backend/skills/spectrum_enrichment.py` - Enrichment sources

**Backend API**:

- `backend/spectrum_data_provider.py` - FastAPI routes

**Frontend**:

- `frontend/src/hooks/useSpectrumData.ts` - Data fetching
- `frontend/src/components/views/SpectrumModule.tsx` - UI component

**Tools**:

- `backend/conductor_spectrum.py` - Verification & testing

## 🧪 Testing

### Test Pipeline Execution

```bash
python -c "
from backend.skills.spectrum_data_pipeline import SpectrumDataPipeline
pipeline = SpectrumDataPipeline()
success, result = pipeline.execute({
    'brand': 'Nord',
    'include_enrichment': True,
    'force_refresh': False
})
print(f'Success: {success}')
print(f'Products: {result.get(\"total_products\")}')
"
```

### Test Validation

```bash
python -c "
from backend.skills.spectrum_validator import SpectrumValidator
validator = SpectrumValidator()
valid, results = validator.execute({
    'payload': {...},
    'brand_taxonomy': ['Nord', 'Moog', 'Roland']
})
print(f'Quality Score: {results.get(\"quality_score\")}')
"
```

### Test Quality Report

```bash
python -c "
from backend.skills.spectrum_validator import QualityReportGenerator
generator = QualityReportGenerator()
success, report = generator.execute({
    'validation_results': {...},
    'brand': 'Nord'
})
print(f'Recommendations: {report[\"recommendations\"]}')
"
```

## 🎯 Common Tasks

### Refresh Product Data

```bash
# Rebuild Nord data
curl -X POST http://localhost:8000/api/spectrum/rebuild/Nord

# Deep refresh (skip cache)
curl -X POST 'http://localhost:8000/api/spectrum/rebuild/Nord?deep_refresh=true'
```

### Get Quality Report

```bash
curl http://localhost:8000/api/spectrum/quality-report/Nord | python -m json.tool
```

### Fetch Spectrum Data

```bash
curl 'http://localhost:8000/api/spectrum/data/Nord?include_enrichment=true' | python -m json.tool
```

### Check Data Sources

```bash
curl http://localhost:8000/api/spectrum/sources/Nord | python -m json.tool
```

## 💡 Tips & Tricks

### Add New Brand

1. Add to `brand_taxonomy` in validation
2. Ensure Halilit data exists
3. Run `conductor_spectrum.py verify Brand`
4. Check quality report

### Improve Quality Score

1. Fix critical errors first (prices, names)
2. Add more data sources
3. Run enrichment against official APIs
4. Validate against taxonomy

### Debug Data Issues

1. Check `/api/spectrum/quality-report/{brand}`
2. Review validation errors
3. Check data provenance
4. Verify source data in Halilit

## 🚨 Troubleshooting

### Low Quality Scores?

- Check Halilit data is complete
- Verify price formatting
- Ensure brand names match taxonomy
- Run deep refresh: `rebuild Nord --deep`

### Missing Enrichment?

- Official APIs might be down
- Check network connectivity
- Review API keys/credentials
- Check rate limiting

### Validation Failures?

- Review validation rules
- Fix source data
- Update taxonomy
- Adjust thresholds if needed

## 📚 Documentation

**Full Documentation**:

- `SPECTRUM_SCREEN_IMPROVEMENTS_v5.3.0.md` - Complete architecture guide
- `SPECTRUM_IMPLEMENTATION_COMPLETE_v5.3.0.md` - Implementation summary

**In Code**:

- Docstrings in all skill classes
- Inline comments explaining logic
- Type hints for all functions

## 🔄 Version History

**v5.3.0** (Current)

- Complete pipeline redesign
- Multi-source enrichment
- Advanced validation
- Quality reporting

**v5.2.x**

- Basic spectrum functionality
- Limited data sources
- Simple validation

## 📞 Support

For issues or questions:

1. Check quality report: `GET /api/spectrum/quality-report/{brand}`
2. Review validation details
3. Check conductor output: `python backend/conductor_spectrum.py verify`
4. Review logs in conductor HTML report
