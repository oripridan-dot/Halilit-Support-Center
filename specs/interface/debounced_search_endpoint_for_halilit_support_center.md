# Spec: Debounced Search Endpoint for Halilit Support Center

**Target:** backend/app/api/endpoints/search.py

## Overview
This specification defines a debounced search endpoint for the Halilit Support Center's "Dark Factory" application. The endpoint will accept a search query and return relevant results from the Halilit knowledge base, incorporating a debouncing mechanism to prevent excessive API calls and optimize performance.

## Requirements
- The API endpoint must be implemented using Python 3.11+, FastAPI, and Pydantic v2.
- The endpoint must accept a `query` string parameter via a GET request.
- The endpoint must incorporate a debouncing mechanism with a delay of 300ms.  Only the last search query received within the debounce window will be processed.
- The endpoint must return a JSON response containing a list of search results. Each result should include a `title` and `content_preview`.
- The search functionality should leverage the existing Halilit knowledge base data (adhering to Three Source Rules).  Assume a function `search_knowledge_base(query: str) -> list[dict]` exists, which takes a query string and returns a list of dictionaries, where each dictionary represents a search result with keys "title" and "content".
- The `content` field from the `search_knowledge_base` function must be truncated to the first 150 characters and assigned to the `content_preview` field in the API response.
- The endpoint should return a 200 OK status code for successful requests.
- The endpoint should handle edge cases where the `query` is empty or `None` by returning an empty list of results.

## Data Contract

**Request:**

*   Method: `GET`
*   Path: `/api/search`
*   Query Parameters:
    *   `query` (string, optional): The search query string.

**Response:**

```json
[
  {
    "title": "Understanding Robotic Arm Calibration",
    "content_preview": "Robotic arm calibration is crucial for ensuring accurate and reliable performance in automated manufacturing processes. This involves identifying and correcting..."
  },
  {
    "title": "Troubleshooting Sensor Malfunctions",
    "content_preview": "Sensor malfunctions can disrupt production and lead to inaccurate data. This document outlines common sensor issues and troubleshooting steps to identify and resolve..."
  }
]
```

**Pydantic Models:**

```python
from pydantic import BaseModel

class SearchResult(BaseModel):
    title: str
    content_preview: str
```

## Behavior Scenarios

- **Scenario:** Valid Search Query
  - Input: `/api/search?query=robotic+arm`
  - Outcome: Returns a JSON list of search results from the Halilit knowledge base, filtered by the query "robotic arm", with each result containing a `title` and a `content_preview` (truncated to 150 characters).

- **Scenario:** Empty Search Query
  - Input: `/api/search?query=`
  - Outcome: Returns an empty JSON list (`[]`).

- **Scenario:** Null Search Query
  - Input: `/api/search?query=None`
  - Outcome: Returns an empty JSON list (`[]`). Note: FastAPI automatically converts "None" string to None.

- **Scenario:** Rapid Successive Queries (Debouncing)
  - Input:
    1.  `/api/search?query=sensor` (Request 1)
    2.  `/api/search?query=robotic` (Request 2 - received 100ms after Request 1)
    3.  `/api/search?query=calibration` (Request 3 - received 200ms after Request 2)
  - Outcome: Only Request 3 (`/api/search?query=calibration`) is processed after 300ms from Request 3.  Requests 1 and 2 are effectively ignored/canceled by the debouncing mechanism. The API returns a JSON list of search results for "calibration".

## Out of Scope

- This spec does not cover the implementation details of the `search_knowledge_base` function. It is assumed to exist and be accessible.
- This spec does not include error handling beyond returning an empty list for empty/null queries. Specific error codes (e.g., 500 for server errors) are not defined.
- Authentication and authorization are not covered in this spec.
- Detailed logging and monitoring are not covered.
