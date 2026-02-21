# Spec: Trie-Based Search Endpoint

**Target:** `backend/app/api/endpoints/search.py`

## Overview
This specification details the implementation of a FastAPI endpoint that provides search functionality based on a Trie data structure. The endpoint receives a search query as input and returns a list of possible completions based on the pre-populated Trie. This Trie will be populated with product names retrieved from the Product Catalog service.

## Requirements
- The endpoint should accept a search query string as input.
- The endpoint should utilize a pre-populated Trie data structure for efficient prefix-based search.
- The Trie should be initialized with product names fetched from the Product Catalog Service.
- The endpoint should return a JSON array of strings representing the search completions.
- The search completions should be ranked based on frequency of appearance in the product catalog (if available, otherwise lexicographically).
- The endpoint should handle empty search queries gracefully, returning an empty list.
- The endpoint should be implemented using FastAPI and Pydantic.
- The endpoint should have appropriate error handling and logging.
- The endpoint must respect the Three Source Rule; It must fetch the list of product names from the Product Catalog.

## Data Contract

**Request:**

```json
{
  "query": "string"
}
```

**Response:**

```json
{
  "completions": ["string", "string", ...]
}
```

**Pydantic Models:**

```python
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    completions: list[str]
```

## Behavior Scenarios

- **Scenario:** Valid Search Query
  - Input: `{"query": "hal"}`
  - Outcome: The endpoint should return a JSON array of strings containing product names that start with "hal", sorted by frequency of appearance (if available) or lexicographically. For example: `{"completions": ["halibut", "halifax", "hall"]}`

- **Scenario:** Empty Search Query
  - Input: `{"query": ""}`
  - Outcome: The endpoint should return an empty JSON array: `{"completions": []}`

- **Scenario:** No Matching Results
  - Input: `{"query": "xyz"}`
  - Outcome: The endpoint should return an empty JSON array: `{"completions": []}`

- **Scenario:** Case-Insensitive Search
  - Input: `{"query": "HAL"}`
  - Outcome: The endpoint should return results regardless of the case of the query. For example: `{"completions": ["halibut", "halifax", "hall"]}`

- **Scenario:** Special Characters in Query
  - Input: `{"query": "hal-i"}`
  - Outcome: The endpoint should treat special characters as part of the search string.  It will likely not return any results unless such a product exists. If product "hal-i" is in the catalog, the response is: `{"completions": ["hal-i"]}`

## Out of Scope
- Specific implementation details of the Trie data structure (assumed to be available).
- The implementation of the Product Catalog Service (assumed to be available).
- Authentication/Authorization for the endpoint.
- Deployment and scaling of the endpoint.
