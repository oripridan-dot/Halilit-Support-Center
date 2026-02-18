# 🔄 Force UI Refresh - Clear All Caches

## Problem

**UI not updating** despite:
- ✅ Catalog rebuilt
- ✅ CSP fixed
- ✅ Backend running

**Root Cause:** Multiple layers of caching:
1. Browser cache
2. React Query cache (5 min staleTime)
3. Backend catalog cache (5 min TTL)

## Solution: Clear ALL Caches

### Step 1: Clear Browser Cache (CRITICAL)

**In Browser Console (F12), run:**

```javascript
// Clear ALL caches
localStorage.clear();
sessionStorage.clear();
// Clear React Query cache
if (window.__REACT_QUERY_STATE__) {
  delete window.__REACT_QUERY_STATE__;
}
// Hard reload
location.reload(true);
```

**OR manually:**
1. Open DevTools (F12)
2. Application tab → Storage → Clear site data
3. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

### Step 2: Clear Backend Catalog Cache

```bash
# Delete catalog cache to force rebuild
rm backend/data/catalog_cache.json.gz

# Restart backend (or wait for next API call - it will rebuild)
```

### Step 3: Force React Query Refetch

**In Browser Console, after page loads:**

```javascript
// Force refetch catalog
const queryClient = window.__REACT_QUERY_CLIENT__;
if (queryClient) {
  queryClient.invalidateQueries(['conductor-catalog']);
  queryClient.refetchQueries(['conductor-catalog']);
}
```

**OR trigger manually:**
- Look for a "Refresh" or "Reload" button in the UI
- Or navigate away and back to Inventory Master

### Step 4: Verify Fresh Data

**Check Network Tab:**
1. Filter by "catalog"
2. Look for `/api/conductor/catalog` request
3. Check response headers:
   - `Cache-Control` should show fresh data
   - Response time should be recent

**Check Console:**
- Should see: `✅ Catalog v10: 6139 products...`
- Health score should match backend

---

## Quick Fix Script

**Run this in browser console:**

```javascript
// Complete cache clear + reload
(async () => {
  console.log('🧹 Clearing all caches...');
  localStorage.clear();
  sessionStorage.clear();
  if ('caches' in window) {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames.map(name => caches.delete(name)));
  }
  console.log('✅ Caches cleared. Reloading...');
  setTimeout(() => location.reload(true), 500);
})();
```

---

## Why This Happens

1. **React Query** caches API responses for 5 minutes (`staleTime: 5 * 60 * 1000`)
2. **Browser** caches HTTP responses
3. **Backend** caches catalog for 5 minutes (`CATALOG_CACHE_TTL = 300`)

**Result:** UI shows old data even after backend rebuilds catalog.

---

## Permanent Fix (Optional)

To always see fresh data during development:

**Edit `frontend/src/hooks/useConductorCatalog.ts`:**

```typescript
staleTime: 0,  // Always refetch (dev only)
gcTime: 0,     // Don't cache (dev only)
```

**OR add to `.env`:**
```
VITE_DISABLE_CACHE=true
```

Then check in hook:
```typescript
staleTime: import.meta.env.VITE_DISABLE_CACHE ? 0 : 5 * 60 * 1000,
```

---

## Summary

**Issue:** Multiple cache layers showing old data  
**Fix:** Clear browser cache + React Query cache + backend cache  
**Verify:** Check Network tab for fresh `/api/conductor/catalog` request
