# 🗑️ Remove Old Search Index Files

## Issue

Old search index files exist in `frontend/public/data/`:
- `search_index_min.json` - Old search index (may contain 8595 items)
- `index.json` - Old index file

These files are **NOT used** by the current codebase (all search goes through `/api/products/search`), but browsers might cache them.

## Solution

**Option 1: Delete Old Files (Recommended)**

```bash
# Remove old search index files (not used anymore)
rm frontend/public/data/search_index_min.json
rm frontend/public/data/index.json  # Keep if needed for other purposes
```

**Option 2: Keep for Reference**

If you want to keep them for reference, rename them:

```bash
mv frontend/public/data/search_index_min.json frontend/public/data/search_index_min.json.old
mv frontend/public/data/index.json frontend/public/data/index.json.old
```

## Why This Matters

The "SearchWorker Initialized with 8595 items" console message is likely from:
1. **Old cached JavaScript** loading these files
2. **Service Worker** caching old code
3. **Browser cache** serving old static files

After clearing browser cache AND removing these files, the SearchWorker message should disappear.

## Verification

After removing files and clearing cache:

1. **Hard refresh browser** (`Cmd+Shift+R`)
2. **Check console** - Should NOT see "SearchWorker Initialized"
3. **Check Network tab** - Should NOT see requests to `search_index_min.json`
4. **Verify search works** - Should use `/api/products/search` endpoint
