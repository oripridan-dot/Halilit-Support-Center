# Spec: Trie-Based Search Index Builder

**Target:** data_pipeline/trie_search_index.py

## Overview
This script constructs a trie-based search index from Halilit product data sourced from the Halilit API and stores it in a JSON file.  This index will be used by the support center's search functionality to provide fast, prefix-based searching for products and their associated documentation. The script ensures data integrity by validating the API response against a Pydantic model.

## Requirements
- Must fetch product data from the Halilit Product API. The base URL is assumed to be defined in a configuration file (`config.py`).
- Must validate the API response against a Pydantic model representing the expected product data structure.
- Must construct a trie data structure in memory.
- Each node in the trie should store a list of product IDs that match the prefix represented by the path to that node.
- Must serialize the trie data structure to a JSON file (`data/product_index.json`).
- Must handle API errors gracefully and log any errors encountered during data fetching or processing.
- Must be idempotent: re-running the script should produce the same index given the same source data.
- Must only include "active" products in the search index. An active product is defined as a product where the `is_active` field in the Halilit API response is `True`.

## Data Contract

**Halilit Product API Response:**

```json
[
  {
    "product_id": "string",
    "name": "string",
    "description": "string",
    "is_active": boolean,
    "documentation_url": "string"
  },
  ...
]
```

**Pydantic Model (data_pipeline/models.py):**

```python
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    is_active: bool
    documentation_url: Optional[HttpUrl] = None  # Documentation URL can be null
```

**Serialized Trie Data (data/product_index.json):**

```json
{
  "a": {
    "p": {
      "i": {
        "d": {
          "product_id_1": {},
          "product_id_2": {}
        }
      }
    }
  },
  "b": {
    "e": {
      "l": {
        "l": {
          "product_id_3": {}
        }
      }
    }
  },
  ...
}
```

Each key in the JSON object represents a character in a product name.  The value is either another nested object representing the next character in the prefix or an empty object associated with a product ID if the current path represents the complete product name. A given `product_id` should appear under all of its prefixes. For example, if a product's name is "bell", then `product_id_3` should appear under "b", "be", "bel", and "bell" prefixes.

## Behavior Scenarios

- **Scenario: Successful Index Creation**
  - Input: Halilit API returns a list of products, including active and inactive products.
  - Outcome: `data/product_index.json` is created, containing a trie index of only the active products.

- **Scenario: API Returns Empty List**
  - Input: Halilit API returns an empty list.
  - Outcome: `data/product_index.json` is created, containing an empty trie (`{}`).

- **Scenario: API Returns Invalid Data**
  - Input: Halilit API returns data that does not conform to the Pydantic `Product` model.
  - Outcome: The script logs an error message indicating the validation failure and exits. The existing `data/product_index.json` (if any) remains untouched.

- **Scenario: API Returns Product With `documentation_url` as Null**
  - Input: Halilit API returns a product where `documentation_url` is `null`.
  - Outcome: The script successfully parses the data into the `Product` model without raising an exception and includes the product in the search index.

- **Scenario: API Request Fails**
  - Input: Halilit API returns an error (e.g., 500 Internal Server Error, network timeout).
  - Outcome: The script logs an error message indicating the API failure and exits. The existing `data/product_index.json` (if any) remains untouched.

## Out of Scope
- Real-time updates to the index. This script is intended to be run periodically (e.g., daily) to refresh the index.
- Authorization or authentication with the Halilit API. It's assumed that any necessary API keys or credentials are provided through environment variables or configuration.
- Deployment or scheduling of the script. This is assumed to be handled by a separate system (e.g., a cron job, Airflow).
- Fine-grained error recovery; in case of a validation or API error the script exits and leaves the existing `data/product_index.json` as is.
