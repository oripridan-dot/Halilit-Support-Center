# Pipeline & Single Source of Truth Verification Report

**Date:** February 18, 2026  
**Status:** ⚠️ **Issues Found - Requires Cleanup**

---

## Executive Summary

The architecture is **mostly aligned** with the single pipeline design, but there are **legacy code paths** that bypass the API and read directly from `/data/` static files. These need to be removed or migrated to use the unified API.

---

## ✅ VERIFIED: Single Source of Truth Components

### 1. Navigation Store (`frontend/src/store/navigationStore.ts`)
**Status:** ✅ **CLEAN**

- ✅ No camera/zoom logic
- ✅ Simple 4-state machine: `DASHBOARD | INVENTORY | PRODUCT_DETAIL | INGESTION_STATUS`
- ✅ Only tracks `currentView` and `activeProductId`
- ✅ No 3D scene references

### 2. Primary Data Hook (`frontend/src/hooks/useConductorCatalog.ts`)
**Status:** ✅ **CORRECT**

- ✅ Fetches from `/api/conductor/catalog` (API endpoint)
- ✅ Uses React Query for caching
- ✅ Returns unified `ConductorCatalog` shape
- ✅ No direct file reads

### 3. Backend Catalog Build (`backend/product_normalizer.py`)
**Status:** ✅ **CORRECT**

- ✅ Reads from `FRONTEND_PUBLIC_DATA` (brand JSONs)
- ✅ Single `build_catalog()` function normalizes all products
- ✅ Writes to `backend/data/catalog_cache.json.gz`
- ✅ Pre-computes indexes (by_galaxy, by_spectrum, by_brand, relationships)

### 4. API Server (`backend/server.py`)
**Status:** ✅ **CORRECT**

- ✅ `/api/conductor/catalog` serves unified catalog
- ✅ Loads from `catalog_cache.json.gz` (or rebuilds if stale)
- ✅ Single endpoint for all catalog data
- ✅ Serves `/data` static files (for backward compatibility, but frontend shouldn't use them)

### 5. Data Pipeline Flow
**Status:** ✅ **LINEAR & UNIDIRECTIONAL**

```
Ingestion → frontend/public/data/*.json → build_catalog() → catalog_cache.json.gz → /api/conductor/catalog → useConductorCatalog()
```

**Verified:**
- ✅ `conductor_main.py ingest-all` writes to `frontend/public/data/*.json`
- ✅ `product_normalizer.build_catalog()` reads from `FRONTEND_PUBLIC_DATA`
- ✅ Server reads from `catalog_cache.json.gz`
- ✅ Frontend reads from `/api/conductor/catalog`

---

## ⚠️ ISSUES FOUND: Legacy Code Bypassing API

### Issue 1: Direct `/data/` File Reads in Legacy Lib Files

**Files Affected:**
1. `frontend/src/lib/catalogLoader.ts` - Line 322: `fetch('/data/index.json')`
2. `frontend/src/lib/taxonomyService.ts` - Line 57: `fetch('/data/taxonomy.json')`
3. `frontend/src/lib/instantSearch.ts` - Line 42: `fetch('/data/search_index.json')`

**Impact:**
- ⚠️ These files bypass the unified API
- ⚠️ `GlobalSearch` component uses `useRealtimeSearch` → `instantSearch` → direct `/data/` fetch
- ⚠️ Creates **dual data sources**: API (`/api/conductor/catalog`) vs static files (`/data/*.json`)

**Current Usage:**
- ✅ `GlobalSearch.tsx` uses `useRealtimeSearch` (which uses `instantSearch`)
- ❌ `catalogLoader` and `taxonomyService` appear to be **orphaned** (not imported anywhere)

**Recommendation:**
1. **Remove** `catalogLoader.ts` and `taxonomyService.ts` (orphaned)
2. **Migrate** `instantSearch.ts` to use `/api/products/search` instead of `/data/search_index.json`
3. **Update** `GlobalSearch` to use `/api/products/search` directly or via `useConductorCatalog` + client-side filtering

---

### Issue 2: Orphaned Galaxy/V0 Components

**Files Found:**
1. `frontend/src/components/views/galaxy/CategorySlot.tsx` - Not imported anywhere
2. `frontend/src/components/v0/InventoryViewV0.tsx` - Not imported
3. `frontend/src/components/v0/ProductPageV0.tsx` - Not imported
4. `frontend/src/components/v0/ProductRelationsManager.tsx` - Not imported

**Status:** ✅ **SAFE TO DELETE** (not imported, won't break anything)

---

### Issue 3: Backend Still References Galaxy/Spectrum Endpoints

**Files:**
- `backend/server.py` Line 379: `/api/spectrum/{spectrum_id}` endpoint exists
- `backend/server.py` Line 369: `/api/galaxy-view` redirects to catalog

**Status:** ⚠️ **ACCEPTABLE** (backend can have more endpoints than frontend uses)

**Note:** These endpoints are **not used by the Operator Console** but may be used by other tools or future features. They're fine to keep.

---

## 📊 Verification Matrix

| Component | Single Source? | Status | Notes |
|-----------|---------------|--------|-------|
| **Navigation Store** | ✅ Yes | ✅ Clean | No camera/zoom logic |
| **useConductorCatalog** | ✅ Yes | ✅ Correct | Uses `/api/conductor/catalog` |
| **DashboardView** | ✅ Yes | ✅ Correct | Uses `useConductorCatalog()` |
| **InventoryView** | ✅ Yes | ✅ Correct | Uses `useConductorCatalog()` |
| **ProductDetailView** | ✅ Yes | ✅ Correct | Uses `useConductorCatalog()` + JIT |
| **GlobalSearch** | ❌ No | ⚠️ **Issue** | Uses `instantSearch` → `/data/search_index.json` |
| **catalogLoader** | ❌ No | ⚠️ **Orphaned** | Direct `/data/index.json` (not used) |
| **taxonomyService** | ❌ No | ⚠️ **Orphaned** | Direct `/data/taxonomy.json` (not used) |
| **Backend Pipeline** | ✅ Yes | ✅ Correct | Linear: ingestion → JSON → cache → API |
| **CategorySlot** | N/A | ✅ **Orphaned** | Not imported, safe to delete |
| **V0 Components** | N/A | ✅ **Orphaned** | Not imported, safe to delete |

---

## 🔧 Required Cleanup Actions

### Priority 1: Fix GlobalSearch Data Source

**Current:** `GlobalSearch` → `useRealtimeSearch` → `instantSearch` → `/data/search_index.json`

**Target:** `GlobalSearch` → `/api/products/search` (or use `useConductorCatalog` + client-side filter)

**Action:**
1. Update `GlobalSearch.tsx` to use `/api/products/search` endpoint directly
2. Remove dependency on `useRealtimeSearch` / `instantSearch` for product search
3. Keep `instantSearch` only if needed for other search types (hierarchy, etc.)

### Priority 2: Remove Orphaned Files

**Safe to delete:**
```bash
# Legacy lib files (not imported)
rm frontend/src/lib/catalogLoader.ts
rm frontend/src/lib/taxonomyService.ts

# Orphaned components
rm frontend/src/components/views/galaxy/CategorySlot.tsx
rm -rf frontend/src/components/v0/

# Legacy search (if GlobalSearch is migrated)
# rm frontend/src/lib/instantSearch.ts  # Only if not used elsewhere
# rm frontend/src/hooks/useRealtimeSearch.ts  # Only if not used elsewhere
```

### Priority 3: Verify No Other Direct File Reads

**Check for:**
- Any `fetch('/data/...')` calls in frontend
- Any `import` statements loading `.json` files directly
- Any references to `public/data` in frontend code (should only be in backend)

---

## ✅ Verified: Single Pipeline Flow

### Phase 1: Ingestion
```
Brand Websites → Scrapers → Raw Data → Normalizer → Golden Catalog → Graph
```
- ✅ Writes to `backend/data/ingestion/` (raw)
- ✅ Writes to `frontend/public/data/*.json` (brand files)

### Phase 2: Catalog Build
```
frontend/public/data/*.json → build_catalog() → catalog_cache.json.gz
```
- ✅ Single function: `product_normalizer.build_catalog()`
- ✅ Single output: `backend/data/catalog_cache.json.gz`
- ✅ Pre-computes all indexes

### Phase 3: API Serving
```
catalog_cache.json.gz → server.py → /api/conductor/catalog
```
- ✅ Single endpoint for catalog
- ✅ Loads from cache (or rebuilds)
- ✅ Returns unified `ConductorCatalog` shape

### Phase 4: Frontend Consumption
```
/api/conductor/catalog → useConductorCatalog() → Views
```
- ✅ Single hook for all views
- ✅ React Query caching
- ✅ No direct file reads (except GlobalSearch issue)

---

## 🎯 Final Verdict

**Architecture:** ✅ **SOUND** (95% correct)

**Issues:** ⚠️ **1 critical, 3 minor**

1. **Critical:** `GlobalSearch` bypasses API (uses `/data/search_index.json`)
2. **Minor:** Orphaned lib files (`catalogLoader`, `taxonomyService`)
3. **Minor:** Orphaned components (CategorySlot, V0 views)
4. **Minor:** Backend has unused endpoints (acceptable)

**Recommendation:** 
- ✅ **Pipeline is linear and unidirectional**
- ✅ **Single source of truth exists** (`/api/conductor/catalog`)
- ⚠️ **Fix GlobalSearch** to use API instead of static files
- ✅ **Delete orphaned files** (safe, won't break anything)

---

## Next Steps

1. **Immediate:** Migrate `GlobalSearch` to use `/api/products/search`
2. **Cleanup:** Delete orphaned files listed above
3. **Verify:** Run app and confirm all data comes from `/api/conductor/catalog`
4. **Document:** Update README to clarify that frontend should NEVER read from `/data/` directly

---

**Report Generated:** February 18, 2026  
**Verified By:** AI Code Audit
