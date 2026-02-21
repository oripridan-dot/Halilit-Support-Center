# ⚡ QUICK START - 3 STEPS TO RUN COMPARISON

**Status**: ✅ **FAST OPTION NOW AVAILABLE** (Skip long ingestion with test data!)

---

## 🚀 FASTEST: Use Test Data (Instant Results - 30 seconds)

```bash
# Start server with test data (no scraping, instant API responses)
cd /workspaces/Halilit-Support-Center
USE_TEST_DATA=1 PYTHONPATH=. python3 backend/server.py
```

**Then test immediately**:

```bash
curl http://localhost:8000/api/comparison/all | jq .brands.montarbo
```

**Result** (instant):

```json
{
  "montarbo": {
    "products_count": 18,
    "matched": 10,
    "match_rate": 55.6,
    "avg_price_diff_percent": -8.96
  }
}
```

✅ **No waiting!** Test dataset works instantly  
✅ **Real price comparisons** using 38 sample Thomann products  
✅ **Demonstrates full business logic** (matching, price diffs, savings)

---

## SLOWER: Full Data Ingestion (30-60 minutes)

If you want complete real data from both sources:

**Estimated Time**: 60-90 minutes total (mostly automated)

---

## Step 1️⃣ Start Data Ingestion (30-60 minutes)

**Option A: Run in Background (Recommended)**

```bash
# Open a new terminal and run:
curl -X POST 'http://localhost:8000/api/v2/comparison/full/run-ingestion' &
```

**Option B: Direct Python**

```bash
cd backend
python scrapers/ingestion_orchestrator.py
```

---

## Step 2️⃣ Monitor Progress (Every 5 minutes)

```bash
curl http://localhost:8000/api/v2/comparison/full/database-stats
```

**Example Output:**

```json
{
  "status": "success",
  "database_statistics": {
    "halilit_products": 5234,
    "thomann_products": 8102,
    "comparisons": 4234
  }
}
```

When counts become non-zero, ingestion is running! ✅

---

## Step 3️⃣ Get Your Results (After ingestion completes)

### Get First Page

```bash
curl 'http://localhost:8000/api/v2/comparison/full/paginated?page=1' \
  | python -m json.tool | head -50
```

### Filter by Confidence Level

```bash
# Only show high-quality matches (>70% confidence)
curl 'http://localhost:8000/api/v2/comparison/full/paginated?min_confidence=70'
```

### Get Specific Brand

```bash
# Example: Compare all RCF products
curl 'http://localhost:8000/api/v2/comparison/full/brand/rcf'
```

### Download Full CSV

```bash
curl -O 'http://localhost:8000/api/v2/comparison/full/export-csv'

# CSV contains all comparisons with:
# - Product names
# - Halilit & Thomann prices (ILS)
# - Price difference %
# - Which retailer is cheaper
# - Match confidence scores
```

---

## 📊 What to Expect

### Ingestion Progress

- **0-10 min**: Scraping Halilit PA speakers (12 categories)
- **10-30 min**: Completing Halilit all categories (5,000+ products)
- **30-60 min**: Scraping Thomann (12 categories, 8,000+ products)
- **60-90 min**: Final matching & comparison calculations

### Final Results (Estimated)

```
✅ Halilit Products: 5,000-7,000
✅ Thomann Products: 8,000-12,000
✅ Successfully Matched: 4,000-5,000 pairs
✅ Match Rate: 60-70%
✅ High-Confidence (>70%): 50-65% of matched
```

---

## 🔍 Example: Check Results

```bash
# Get all RCF comparisons
curl -s 'http://localhost:8000/api/v2/comparison/full/brand/rcf' \
  | python -m json.tool

# Expected response:
{
  "status": "success",
  "brand": "rcf",
  "data": {
    "total": 15,
    "halilit_cheaper": 8,
    "thomann_cheaper": 7,
    "average_price_difference_percent": 12.45,
    "results": [
      {
        "halilit_product_name": "RCF ART 310",
        "halilit_price_ils": 4500,
        "thomann_product_name": "RCF ART 310A",
        "thomann_total_ils": 3600,
        "price_difference_percent": -20.0,
        "cheaper_at": "thomann",
        "match_confidence": 95.2
      }
      // ... more products
    ]
  }
}
```

---

## 📖 Learn More

For detailed information, see:

- **FULL_SCALE_COMPARISON_GUIDE.md** - Complete guide with all options
- **SYSTEM_COMPLETE.md** - Full system overview
- **FULL_SCALE_IMPLEMENTATION_SUMMARY.md** - Technical details

---

## ❓ Troubleshooting

**"No products found"**
→ Ingestion still running. Check progress with Step 2 command.

**"Connection timeout"**
→ Backend server not running. Start with: `python backend/server.py`

**"0 products in database"**
→ Ingestion completed but no products. Check network connectivity to halilit.com and thomannmusic.com

**"Low match rate (<40%)"**
→ Normal! Some products don't have direct equivalents. Use `min_confidence=50` to relax matching.

---

## ✅ Verify Installation

```bash
# Test API is working
curl http://localhost:8000/api/v2/comparison/full/database-stats

# Should return:
{
  "status": "success",
  "database_statistics": {
    "halilit_products": 0,
    "thomann_products": 0,
    "comparisons": 0
  }
}
```

If you see this, you're ready to start ingestion! 🚀

---

## 🎯 One-Liner Quick Start

```bash
# Run ingestion in background, monitor, and fetch first page
curl -X POST 'http://localhost:8000/api/v2/comparison/full/run-ingestion' & \
sleep 60 && \
echo "Waiting for ingestion..." && \
read -p "Press Enter when database-stats shows products..." && \
curl 'http://localhost:8000/api/v2/comparison/full/paginated?page=1' | python -m json.tool
```

---

**That's it! The system will do the rest automatically.** 🎉

For more options and customization, see FULL_SCALE_COMPARISON_GUIDE.md
