# Spec: Trie-based Search Index Generation
**Target:** data_pipeline/trie_search_index.py

## Overview
This script generates a trie-based search index from a dataset of Halilit product information. The index will be serialized to a JSON file for efficient retrieval and fuzzy search capabilities in the Halilit Support Center. This ensures fast and relevant search results for users seeking help with specific products.

## Requirements
- The script must read Halilit product data from a JSON file located at `data/halilit_products.json`.
- The script must construct a trie data structure in memory.
- Each product name should be tokenized into individual words before being added to the trie.
- The script must serialize the trie data structure into a JSON file named `data/search_index.json`.
- The script must handle potential errors during file I/O gracefully, logging appropriate messages.
- The script must be idempotent: repeated runs with the same product data should produce the same search index.
- The script should use type hints for all function signatures and variable declarations.

## Data Contract

### Input: `data/halilit_products.json`
```json
[
  {
    "product_id": "HL101",
    "product_name": "Halilit Baby Maraca",
    "product_description": "A fun and engaging musical toy for babies."
  },
  {
    "product_id": "HL202",
    "product_name": "Halilit Egg Shaker",
    "product_description": "A classic percussion instrument for early childhood development."
  }
]
```
(This file is assumed to exist and conform to this structure. Its generation is out of scope.)

### Output: `data/search_index.json`
```json
{
  "": {  // Root node represents the empty string
    "h": {
      "halilit": {
        "baby": {
          "maraca": {
            "": {
              "product_ids": ["HL101"]
            }
          }
        },
        "egg": {
          "shaker": {
            "": {
              "product_ids": ["HL202"]
            }
          }
        },
        "": {
          "product_ids": ["HL101", "HL202"] // All products that START with "halilit"
        }
      }
    },
    "b": {
      "baby": {
          "maraca": {
            "": {
              "product_ids": ["HL101"]
            }
          }
        }
    },
    "e": {
      "egg": {
          "shaker": {
            "": {
              "product_ids": ["HL202"]
            }
          }
        }
    },
    "m": {
      "maraca": {
        "": {
          "product_ids": ["HL101"]
        }
      }
    },
    "s": {
      "shaker": {
          "": {
              "product_ids": ["HL202"]
          }
        }
    }
  }
}
```

## Behavior Scenarios

- **Scenario:**  Initial Index Creation
  - Input: `data/halilit_products.json` contains product data (as shown above). `data/search_index.json` does not exist.
  - Outcome: `data/search_index.json` is created, containing the trie representation of the product names and product IDs, following the Data Contract specification.
- **Scenario:**  Idempotent Index Creation
  - Input: `data/halilit_products.json` contains the same product data as the previous run. `data/search_index.json` already exists with a trie generated from this data.
  - Outcome: `data/search_index.json` remains unchanged.
- **Scenario:** Update Product Data
  - Input: `data/halilit_products.json` is modified to include a new product: `{"product_id": "HL303", "product_name": "Halilit Clip Clop", "product_description": "A colourful clip clop."}`. `data/search_index.json` contains the previous trie.
  - Outcome: `data/search_index.json` is updated to include "Halilit Clip Clop" with `HL303` in the corresponding trie nodes.
- **Scenario:** Missing Product Data File
  - Input: `data/halilit_products.json` does not exist.
  - Outcome: An error message is logged indicating that the product data file could not be found, and the script exits gracefully. `data/search_index.json` is not created or modified.
- **Scenario:** Empty Product Data File
  - Input: `data/halilit_products.json` exists but is empty (`[]`).
  - Outcome: `data/search_index.json` is created and contains an empty trie (`{"": {}}`).

## Out of Scope
- Fuzzy search implementation. The script only builds the index.
- Real-time updates to the index. This script is intended for batch processing.
- Data validation of the `data/halilit_products.json` file beyond checking for its existence.
- Deployment and scheduling of the script.
- User interface for triggering the index generation.
