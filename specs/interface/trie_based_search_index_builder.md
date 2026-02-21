# Spec: Trie-Based Search Index Builder

**Target:** data_pipeline/trie_search_index.py

## Overview
This data pipeline script builds a Trie-based search index from the Halilit Support Center's product catalog data. The index allows for efficient prefix-based search queries, crucial for quickly finding products based on partial user input within the support center. This script will fetch data from the product catalog API, transform the data into a Trie structure, and persist the Trie to a file for later retrieval by the search service.

## Requirements
- The script must fetch product catalog data from the Halilit Product Catalog API endpoint: `https://api.halilit.com/products`.
- The script must handle API pagination to retrieve all product data, not just the first page. Assume the API returns data in the format: `{"products": [...], "next_page_token": "..."}`.  If `next_page_token` is null or an empty string, it signifies the end of pagination. Subsequent requests should append `?page_token={next_page_token}` to the URL.
- Each product in the catalog has, at minimum, a `name` (string) and a `product_id` (string) field.  The script must index the `name` field in the Trie.
- The Trie implementation must support storing the `product_id` associated with each indexed product name.
- The Trie must be persisted to a file named `trie.json` in the `/data` directory relative to the script's location.
- The script must use a thread pool to make HTTP requests concurrently. The maximum number of threads must be configurable via the `MAX_THREADS` environment variable. Default to 10 threads if the env var is not set.
- The script must handle potential API errors (e.g., network issues, 500 errors) with appropriate error logging and retry mechanism (up to 3 retries with exponential backoff).
- The script should log progress and any errors encountered during the process.
- The `trie.json` file must be a valid JSON object.
- The script should be idempotent: running it multiple times should produce the same `trie.json` file given the same input data from the API.

## Data Contract

**API Response (Product Catalog):**

```json
{
  "products": [
    {
      "product_id": "string",
      "name": "string",
      "description": "string",
      "image_url": "string",
      // ... other product details
    }
  ],
  "next_page_token": "string | null"
}
```

**Trie Data Structure (in memory):**

```python
class TrieNode:
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.product_ids: Set[str] = set()  # Use a Set to avoid duplicates

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, product_id: str):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.product_ids.add(product_id)

    def search(self, prefix: str) -> Set[str]: # Returns a Set of product_ids
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return set() #Return an empty set
            node = node.children[char]
        return self._collect_product_ids(node)

    def _collect_product_ids(self, node: TrieNode) -> Set[str]:
        product_ids = set(node.product_ids)
        for child in node.children.values():
            product_ids.update(self._collect_product_ids(child))
        return product_ids
```

**JSON Representation (trie.json):**  The trie is serialized to JSON.  The exact format of this serialization is not explicitly defined.  The implementer must choose a reasonable approach that allows for re-constructing the Trie data structure from the JSON. For example:

```json
{
    "root": {
        "h": {
            "a": {
                "l": {
                    "i": {
                        "l": {
                            "product_ids": ["HL123", "HL456"]
                         },
                         "product_ids": []
                    },
                    "product_ids": []
                },
                "product_ids": []
            },
            "product_ids": []
        },
        "b": {
            "a":{
                "n": {
                    "a": {
                        "n": {
                            "a": {
                                "product_ids": ["BN789"]
                            },
                             "product_ids": []
                        },
                        "product_ids": []
                    },
                    "product_ids": []
                },
                 "product_ids": []
            },
            "product_ids": []
        },
        "product_ids": []
    }
}
```

## Behavior Scenarios

- **Scenario:** Initial Run
  - Input: Empty `data/trie.json` file. The Halilit Product Catalog API returns a list of products.
  - Outcome: A `trie.json` file is created in the `/data` directory containing the serialized Trie data structure. The log output shows progress and completion messages.

- **Scenario:** Subsequent Run with Same Data
  - Input: Existing `data/trie.json` file. The Halilit Product Catalog API returns the same list of products as the previous run.
  - Outcome: The `data/trie.json` file is overwritten with the same content. The log output shows progress and completion messages. The modification timestamp of the file might change.

- **Scenario:** API Error
  - Input: The Halilit Product Catalog API returns a 500 error on the first attempt.
  - Outcome: The script retries the API request up to 3 times with exponential backoff. If all retries fail, the script logs an error message and exits.

- **Scenario:** API Pagination
  - Input: The Halilit Product Catalog API returns paginated results, indicated by a `next_page_token`.
  - Outcome: The script correctly fetches all pages of product data, constructs the Trie with the complete dataset, and persists it to `trie.json`.

- **Scenario:** Product with Empty Name
  - Input: One or more products in the Halilit Product Catalog API response have an empty or null `name` field.
  - Outcome: The script skips these products and logs a warning message indicating that the product was skipped due to an empty name. The script continues processing other products.

## Out of Scope
- This spec does not cover the actual search service that will consume the `trie.json` file.
- This spec does not cover deployment or scheduling of the data pipeline script.
- This spec does not cover monitoring of the script's execution.
- This spec does not cover authentication or authorization for accessing the Halilit Product Catalog API (it is assumed to be publicly accessible, though it may require an API key that must be configured separately).
