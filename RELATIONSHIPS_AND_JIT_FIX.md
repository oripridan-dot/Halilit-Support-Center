# Product Relationships & JIT Intelligence — Issues & Fixes

## Issue 1: Product Relationships Not Fully Implemented

### Current State
- ✅ Graph snapshot exists: `backend/data/graph/product_graph.json` (44MB, 32,462 relationships from Feb 16)
- ✅ Relationships are loaded from snapshot during catalog build
- ⚠️ **Problem**: Relationships may not be properly indexed in catalog `indexes.relationships`

### Root Cause
The relationships are loaded from the snapshot and added to the graph, but:
1. `graph.to_catalog_indexes()` creates the relationships index
2. The index is only added to catalog if `combined_relationships` is not empty
3. If graph indexes are empty or relationships aren't serialized correctly, they won't appear in the catalog

### Fix Required
Ensure relationships are always included in catalog indexes, even if empty:

```python
# In product_normalizer.py build_catalog(), around line 1468:
if combined_relationships:
    all_indexes["relationships"] = combined_relationships
else:
    # Always include relationships index, even if empty
    all_indexes["relationships"] = graph_indexes.get("relationships", {})
```

### Verification
Check catalog response includes relationships:
```bash
curl http://localhost:8000/api/conductor/catalog | jq '.indexes.relationships | keys | length'
# Should return > 0 if relationships are indexed
```

---

## Issue 2: JIT Intelligence Not Working Properly

### Current State
- ✅ JIT endpoint exists: `POST /api/jit/product/{product_id}` (SSE stream)
- ⚠️ **Problem**: Requires `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- ⚠️ If missing, JIT skips AI analysis and returns minimal data

### Root Cause
1. JIT agent uses Gemini 2.0 Flash for AI analysis
2. Requires API key from https://aistudio.google.com/app/apikey
3. If key is missing, it logs warning and skips AI phase
4. Frontend may show "Analyzing product data…" indefinitely

### Fix Required

#### Option A: Set Environment Variable
```bash
# In .env file or shell:
export GOOGLE_API_KEY="your-api-key-here"
# OR
export GEMINI_API_KEY="your-api-key-here"
```

#### Option B: Add Better Error Handling
Update `jit_agent.py` to return clear error events when API key is missing:

```python
# In stream_product_intelligence(), around line 606:
if not api_key:
    yield f"event: error\n"
    yield f"data: {json.dumps({'error': 'GOOGLE_API_KEY not set. Get key from https://aistudio.google.com/app/apikey'})}\n\n"
    yield f"event: complete\n"
    yield f"data: {json.dumps({'cached': False})}\n\n"
    return
```

### Verification
Test JIT endpoint:
```bash
curl -N -X POST http://localhost:8000/api/jit/product/roland-fantom-ex
# Should stream SSE events: status, snap, official_specs, verdict, complete
```

---

## Quick Fixes

### 1. Ensure Relationships Are Always Indexed

**File**: `backend/product_normalizer.py` (around line 1468)

```python
# Replace:
if combined_relationships:
    all_indexes["relationships"] = combined_relationships

# With:
if combined_relationships:
    all_indexes["relationships"] = combined_relationships
elif graph_indexes and graph_indexes.get("relationships"):
    # Fallback to graph indexes if no OpenClaw hints
    all_indexes["relationships"] = graph_indexes["relationships"]
else:
    # Always include relationships index (even if empty)
    all_indexes["relationships"] = {}
```

### 2. Add JIT API Key Check & Better Errors

**File**: `backend/jit_agent.py` (around line 606)

```python
# After checking for api_key, add:
if not api_key:
    async def error_stream():
        yield f"event: error\n"
        yield f"data: {json.dumps({'error': 'GOOGLE_API_KEY not configured. Set GOOGLE_API_KEY or GEMINI_API_KEY in environment or .env file. Get key from https://aistudio.google.com/app/apikey'})}\n\n"
        yield f"event: complete\n"
        yield f"data: {json.dumps({'cached': False, 'error': True})}\n\n"
    return error_stream()
```

### 3. Update IngestionStatusView to Show JIT Status

Add a section showing JIT configuration status (API key present/absent).

---

## Testing

1. **Test Relationships**:
   ```bash
   # Rebuild catalog
   PYTHONPATH=. python backend/conductor_main.py rebuild-catalog
   
   # Check relationships in catalog
   curl http://localhost:8000/api/conductor/catalog | jq '.indexes.relationships | keys | length'
   ```

2. **Test JIT**:
   ```bash
   # Set API key
   export GOOGLE_API_KEY="your-key"
   
   # Test JIT endpoint
   curl -N -X POST http://localhost:8000/api/jit/product/roland-fantom-ex
   ```

---

## Summary

- **Relationships**: Ensure `indexes.relationships` is always included in catalog, even if empty
- **JIT**: Add clear error messages when API key is missing; document requirement in UI
