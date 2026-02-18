# Verify Changes — Operator Console v9.6.0

If the app looks "exactly the same", follow these steps to ensure all changes are applied:

## Step 1: Clear All Caches

```bash
./clear_all_caches.sh
```

This clears:
- Frontend build cache (`.vite`, `dist`)
- Backend catalog cache (`catalog_cache.json.gz`)
- Python caches (`__pycache__`)
- Log files

## Step 2: Stop All Running Servers

```bash
# Kill any running processes
pkill -f "uvicorn server:app" || true
pkill -f "vite" || true
pkill -f "npm run dev" || true
```

## Step 3: Hard Refresh Browser

**Chrome/Edge:**
- Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Or: Open DevTools (F12) → Right-click refresh → "Empty Cache and Hard Reload"

**Firefox:**
- Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Or: Settings → Privacy → Clear Data → Check "Cached Web Content" → Clear

**Safari:**
- Press `Cmd+Option+R`
- Or: Safari → Preferences → Advanced → Check "Show Develop menu" → Develop → Empty Caches

## Step 4: Restart Servers Fresh

```bash
./start_console.sh
```

Wait for:
- ✅ Backend is ready!
- ✅ Frontend dev server running

## Step 5: Verify Changes

### Check 1: GlobalSearch Uses API
1. Open browser DevTools (F12) → Network tab
2. Type in GlobalSearch (Cmd+K)
3. Look for request to `/api/products/search?q=...`
4. ✅ Should see API request, NOT `/data/search_index.json`

### Check 2: Inventory Uses API
1. Go to Inventory Master
2. Check Network tab for `/api/conductor/catalog`
3. ✅ Should see API request with products array

### Check 3: No Old Components
1. Check browser console for errors
2. ✅ Should NOT see imports for GalaxyDashboard, SpectrumModule, ProductPage

### Check 4: Navigation Works
1. Type in GlobalSearch → Press Enter
2. ✅ Should navigate to Inventory with filter applied
3. Click product → ✅ Should show Product Detail view

## Step 6: Verify Backend Changes

```bash
# Check server.py has image mounts
grep -A 5 "Mount images directory" backend/server.py

# Check catalog endpoint
curl http://localhost:8000/api/conductor/catalog | jq '.metadata.total_products'

# Check search endpoint
curl "http://localhost:8000/api/products/search?q=roland" | jq '.products | length'
```

## Step 7: Check Git Status

```bash
git status
# Should show: "nothing to commit, working tree clean"

git log --oneline -5
# Should see recent commits:
# - Fix: Complete Operator Console integration
# - Polish: Code quality improvements
# - Add: Comprehensive pipeline validation
```

## Troubleshooting

### Issue: Still seeing old UI
**Solution:**
1. Clear browser cache completely (see Step 3)
2. Close all browser tabs
3. Restart browser
4. Open fresh: http://localhost:5173

### Issue: "No detailed specifications ingested"
**This is EXPECTED** if:
- Product hasn't been enriched yet (run `python backend/conductor_main.py enrich`)
- JIT agent hasn't run yet (specs load when you open product)
- Product doesn't have official specs available

**To populate specs:**
```bash
# Enrich all products
python backend/conductor_main.py enrich

# Or enrich specific brand
python backend/conductor_main.py enrich "Roland"
```

### Issue: Search doesn't work
**Check:**
1. Backend is running: `curl http://localhost:8000/api/health`
2. Search endpoint exists: `curl "http://localhost:8000/api/products/search?q=test"`
3. Browser console shows API request (not 404)

### Issue: Images don't load
**Check:**
1. Backend serves images: `curl http://localhost:8000/images/test.jpg` (should 404, not connection error)
2. Product has `image_url` in catalog
3. Browser console shows image load errors

## Expected Behavior After Changes

### Before (Old):
- GlobalSearch used Web Worker + static JSON
- Inventory read from `/data/catalog.json`
- Navigation had camera/zoom logic
- Galaxy/Spectrum views existed

### After (New):
- ✅ GlobalSearch uses `/api/products/search`
- ✅ Inventory uses `/api/conductor/catalog` via hook
- ✅ Navigation is clean 4-state machine
- ✅ No Galaxy/Spectrum views (removed)
- ✅ All data comes from unified API

## Verification Checklist

- [ ] Caches cleared (`./clear_all_caches.sh`)
- [ ] Servers restarted (`./start_console.sh`)
- [ ] Browser cache cleared (hard refresh)
- [ ] GlobalSearch shows API requests in Network tab
- [ ] Inventory shows API requests in Network tab
- [ ] No console errors about missing components
- [ ] Navigation works (search → inventory → product)
- [ ] No references to Galaxy/Spectrum in console

---

**If still seeing issues after all steps, check:**
1. Are you on the correct branch? (`git branch` should show `v9.6-ui`)
2. Are changes committed? (`git log` should show recent commits)
3. Is frontend rebuilt? (check `frontend/dist` timestamp if using production build)
