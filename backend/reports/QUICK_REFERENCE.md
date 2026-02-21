# Quick Command Reference

## 🚀 Run the Matcher

```bash
cd /workspaces/Halilit-Support-Center
python backend/scrapers/advanced_product_matcher.py
```

**Output:**

- ✓ rcf_comparison_ils.csv (25 products)
- ✓ mackie_comparison_ils.csv (25 products)
- ✓ comparison_summary_advanced.json

## 📊 View Results

### See All RCF Comparisons (Formatted)

```bash
python backend/reports/view_comparison.py rcf
```

### See All Mackie Comparisons (Formatted)

```bash
python backend/reports/view_comparison.py mackie
```

### Quick Stats

```bash
echo "RCF Products:"
wc -l backend/reports/rcf_comparison_ils.csv

echo "Mackie Products:"
wc -l backend/reports/mackie_comparison_ils.csv

echo "Combined:"
cat backend/reports/comparison_summary_advanced.json | python -m json.tool
```

### High-Confidence Matches Only

```bash
# RCF
grep -E '9[5-9]%|100%' backend/reports/rcf_comparison_ils.csv

# Mackie
grep -E '9[5-9]%|100%' backend/reports/mackie_comparison_ils.csv
```

### View Prices Only

```bash
# RCF
cut -d, -f2,7 backend/reports/rcf_comparison_ils.csv

# Mackie
cut -d, -f2,7 backend/reports/mackie_comparison_ils.csv
```

## 📋 File Locations

**Main Script:**

```
backend/scrapers/advanced_product_matcher.py
```

**Output Files:**

```
backend/reports/rcf_comparison_ils.csv
backend/reports/mackie_comparison_ils.csv
backend/reports/comparison_summary_advanced.json
```

**Documentation:**

```
backend/reports/DELIVERY_SUMMARY.md
backend/reports/ADVANCED_COMPARISON_REPORT.md
backend/reports/MATCHER_SETUP_GUIDE.md
```

## 🔧 Customize Settings

### Change Exchange Rate

Edit `advanced_product_matcher.py` line ~30:

```python
USD_TO_ILS = 3.70  # Update this
```

### Change Confidence Thresholds

Edit `advanced_product_matcher.py`:

```python
# Line ~300+ in run() method
matches = self.match_all_products(halilit, thomann, brand, threshold=0.60)
                                                                    ↑
                                                          Change this value
```

### Add More Brands

Edit your script to call:

```python
engine = AdvancedProductMatcher()
engine.run(brands=["RCF", "Mackie", "Behringer"])  # Add brand here
```

## 📖 Read the Docs

### For Overview

```bash
cat backend/reports/DELIVERY_SUMMARY.md
```

### For Technical Details

```bash
cat backend/reports/ADVANCED_COMPARISON_REPORT.md
```

### For Setup & Extension

```bash
cat backend/reports/MATCHER_SETUP_GUIDE.md
```

## 🎯 Key Metrics at a Glance

```
COVERAGE              : 100% (50/50 Halilit products matched)
HIGH CONFIDENCE (≥75%): 44% (22 products)
RCF PRICE RANGE      : ₪175 - ₪6,862 ILS
MACKIE PRICE RANGE   : ₪248 - ₪2,515 ILS
EXECUTION TIME       : <1 second
```

## 🔍 Debug / Troubleshoot

### Check if Data Files Exist

```bash
ls -l backend/scrapers/*.json | grep -E "halilit|thomann"
```

### Verify CSV Format

```bash
head -3 backend/reports/rcf_comparison_ils.csv
```

### Check for Errors

```bash
python backend/scrapers/advanced_product_matcher.py 2>&1 | grep -i error
```

### Recount Products

```bash
python << 'EOF'
import json

rcf = json.load(open('backend/scrapers/halilit_rcf_full.json'))
mackie = json.load(open('backend/scrapers/halilit_mackie_full.json'))

print(f"Halilit RCF: {len(rcf)}")
print(f"Halilit Mackie: {len(mackie)}")
print(f"Total: {len(rcf) + len(mackie)}")
EOF
```

## 💡 Common Tasks

### Extract All RCF Prices

```bash
tail -n +2 backend/reports/rcf_comparison_ils.csv | cut -d, -f7
```

### Get Average Price (RCF)

```bash
python << 'EOF'
import csv
import statistics

prices = []
with open('backend/reports/rcf_comparison_ils.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        p = row['Thomann_Price_ILS'].replace('₪', '')
        prices.append(int(p))

print(f"Average: ₪{statistics.mean(prices):.0f}")
print(f"Median: ₪{statistics.median(prices):.0f}")
print(f"Range: ₪{min(prices)} - ₪{max(prices)}")
EOF
```

### Compare RCF vs Mackie

```bash
echo "RCF Count:" && tail -n +2 backend/reports/rcf_comparison_ils.csv | wc -l
echo "Mackie Count:" && tail -n +2 backend/reports/mackie_comparison_ils.csv | wc -l
echo "Total:" && python -c "print(25 + 25)"
```

### Show Match Quality Distribution

```bash
python << 'EOF'
import csv
from collections import Counter

all_confs = []
for fname in ['rcf_comparison_ils.csv', 'mackie_comparison_ils.csv']:
    with open(f'backend/reports/{fname}') as f:
        reader = csv.DictReader(f)
        for row in reader:
            conf = int(row['Match_Confidence'].strip('%'))
            all_confs.append(conf)

high = sum(1 for c in all_confs if c >= 75)
med = sum(1 for c in all_confs if 60 <= c < 75)
low = sum(1 for c in all_confs if c < 60)

print(f"High (≥75%): {high} products")
print(f"Medium (60-75%): {med} products")
print(f"Low (<60%): {low} products")
print(f"Total: {len(all_confs)} products")
EOF
```

## 🔄 Update Workflow

### To refresh with latest Thomann prices:

```bash
# 1. Run matcher (fetches fresh Thomann data)
python backend/scrapers/advanced_product_matcher.py

# 2. Verify output
head -5 backend/reports/rcf_comparison_ils.csv

# 3. Check timestamp
grep "Data Freshness" backend/reports/ADVANCED_COMPARISON_REPORT.md
```

### To update exchange rate:

```bash
# 1. Edit the rate in advanced_product_matcher.py
nano backend/scrapers/advanced_product_matcher.py
# Find: USD_TO_ILS = 3.65
# Change to: USD_TO_ILS = X.XX

# 2. Re-run to regenerate
python backend/scrapers/advanced_product_matcher.py

# 3. Verify new rates
grep "3\.65\|X\.XX" backend/reports/rcf_comparison_ils.csv | head -3
```

## ✅ Verification Checklist

After running the matcher:

- [ ] rcf_comparison_ils.csv exists (3.1+ KB)
- [ ] mackie_comparison_ils.csv exists (3.4+ KB)
- [ ] Both files have 26 lines (1 header + 25 products)
- [ ] All products have Thomann_Price_ILS values
- [ ] Match_Confidence values range 0-100%
- [ ] comparison_summary_advanced.json created

```bash
# Run this to verify
for f in rcf_comparison_ils.csv mackie_comparison_ils.csv; do
  echo "Checking $f..."
  wc -l backend/reports/$f
  head -1 backend/reports/$f
  echo ""
done
```

---

**Last Updated**: February 8, 2026  
**Status**: Ready to use  
**Quick Reference**: Save this file for easy access
