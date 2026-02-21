# Spec: Trie-Based Prefix Search Index
**Source:** 2026-02-23_proposal_trie_search_index.md
**Created:** 2026-02-21
**Status:** BUILT ✅

---

## Problem

`UnifiedDataService._matches_search()` runs a full linear scan through every product
on every query: `query in search_text`. With 1 000+ products this is O(n) on every
keystroke. Users notice the lag on partial SKU and brand prefix searches.

## Proposed Solution

Add a `TrieSearchIndex` class to `backend/unified_data_service.py` that is:

1. **Built once** when the catalog loads (`_build_trie_index()`).
2. **Queried first** by `_matches_search()` for prefix matching.
3. **Falls back** to the existing substring check when the query contains a space
   (phrase search) or is > 1 word.

### Implementation Constraints

- **Pure Python stdlib** — no new pip packages. Use nested `dict` for nodes.
- **Zero config changes** — no new settings, environment variables, or API keys.
- **Three Source Rules** — index only built from catalog product data (name,
  brand, SKU); never from AI-generated content.
- **Thread-safe read** — index is rebuilt on catalog reload, immutable in-flight.

### Algorithm

```
TrieNode  = dict[str, TrieNode]
           + leaf key "$$ids" = set[str]   (product IDs matched at this prefix)

Build:
  for each product:
    tokens = [each word in product_name, brand, sku/id]
    for each token:
      insert token.lower() into trie, storing product_id at EVERY prefix node
      (so "gibson" stores product_id at g, gi, gib, gibs, gibso, gibson)

Query (prefix_search(query)):
  walk trie one char at a time
  if prefix found → return all ids stored at that node
  if prefix not in trie → return None  (signals: fall back to substring scan)
```

### Files to Touch

| File | Change |
|---|---|
| `backend/unified_data_service.py` | Add `TrieSearchIndex` class + `_build_trie_index()` + integrate in `_matches_search()` |

Do NOT touch any other file. No frontend changes.

### Integration Points

1. In `UnifiedDataService.__init__` add `self._trie: TrieSearchIndex | None = None`.
2. Add `_build_trie_index(self)` that reads `self._catalog.get("products", [])` and
   builds `self._trie = TrieSearchIndex(products)`.
3. Call `_build_trie_index()` after any catalog update (wherever `self._catalog` is set).
4. Replace `_matches_search` body with:

```python
def _matches_search(self, product: Dict[str, Any], query: str) -> bool:
    q = query.strip().lower()
    if self._trie and " " not in q:          # single-token → trie fast path
        ids = self._trie.prefix_search(q)
        if ids is not None:
            return product.get("id") in ids
    # multi-word or trie miss → original substring fallback
    searchable = [
        product.get("product_name", "").lower(),
        product.get("brand", "").lower(),
        product.get("taxonomy", {}).get("canonical_category", "").lower(),
        product.get("description_short", "").lower(),
    ]
    return q in " ".join(searchable)
```

## Expected Impact

- **+40% faster search** for single-token prefix queries (>80% of real queries)
- No regression on multi-word or phrase searches (fallback preserved)
- Memory: ~1–4 MB for 1 000 products

## Acceptance Criteria

- [x] `TrieSearchIndex` class exists in `backend/unified_data_service.py`
- [x] `prefix_search("gib")` returns a set of product IDs for Gibson products
- [x] `prefix_search("xyz_nomatch")` returns `None` (no crash, no empty set)
- [x] `_matches_search` still returns correct results for "yamaha psr" (phrase → fallback)
- [x] `PYTHONPATH=. python -c "from backend.unified_data_service import UnifiedDataService; print('OK')"` exits 0
- [x] No new imports outside Python stdlib
- [x] Three Source Rules: no synthetic data introduced
