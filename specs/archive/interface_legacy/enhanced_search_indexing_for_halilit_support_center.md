# Spec: Enhanced Search Indexing for Halilit Support Center

**Target:** backend/services/search_indexing.py

## Overview
This service enhances the search indexing capabilities of the Halilit Support Center's knowledge base. It consumes data about support tickets and documentation updates from existing internal systems, preprocesses the text, and updates a search index to improve search result relevance and speed. The service will use an asynchronous architecture to avoid blocking other operations.

## Requirements
- The service must subscribe to events indicating new or updated support tickets (identified by ticket ID and last updated timestamp) from the Ticketing System.
- The service must subscribe to events indicating new or updated documentation articles (identified by article ID and last updated timestamp) from the Documentation Management System.
- The service must retrieve the full content of updated tickets and documentation articles from their respective systems via internal APIs.
- The service must preprocess the retrieved text content by:
    - Removing HTML tags.
    - Converting to lowercase.
    - Removing punctuation.
    - Removing stop words (using a predefined list).
- The service must use an external search index (e.g., Elasticsearch, Algolia) to store and manage the indexed data. We'll refer to this as the "Search Index Provider."
- The service must handle errors gracefully, logging errors and retrying failed indexing attempts up to 3 times with exponential backoff (1s, 4s, 16s).
- The service must expose a health check endpoint that returns a 200 status code if the service is running and can connect to the Search Index Provider and internal APIs.
- The service should prioritize indexing documentation articles before support tickets.
- The service should be idempotent: re-indexing the same document should not create duplicates in the search index. The ticket ID or article ID will be used as the document ID in the search index.

## Data Contract

**Event Payloads (Ticketing System and Documentation Management System):**

```python
from pydantic import BaseModel
from datetime import datetime

class UpdateEvent(BaseModel):
    id: str # Ticket ID or Article ID
    last_updated: datetime
```

**Ticketing System API (Internal):**

Request: `GET /api/tickets/{ticket_id}`

Response:

```python
class Ticket(BaseModel):
    ticket_id: str
    subject: str
    body: str
    created_at: datetime
    updated_at: datetime
    customer_id: str
    agent_id: str | None
```

**Documentation Management System API (Internal):**

Request: `GET /api/articles/{article_id}`

Response:

```python
class Article(BaseModel):
    article_id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    category: str
```

**Search Index Data (Elasticsearch Example):**

```json
{
  "document_id": "ticket-123" or "article-456", # Use ticket_id or article_id
  "type": "ticket" or "article",
  "title": "Ticket Subject or Article Title",
  "content": "Preprocessed Ticket Body or Article Content",
  "created_at": "ISO 8601 Timestamp",
  "updated_at": "ISO 8601 Timestamp",
  "customer_id": "Customer ID (only for tickets)",
  "agent_id": "Agent ID (only for tickets)",
  "category": "Article Category (only for articles)"
}
```

## Behavior Scenarios

- **Scenario:** New Ticket Created
  - Input: Ticketing System emits `UpdateEvent(id="ticket-123", last_updated=2024-01-01T10:00:00Z)`
  - Outcome: Service retrieves ticket "ticket-123" via API, preprocesses its subject and body, and adds a new document to the Search Index with `document_id="ticket-123"` and `type="ticket"`.

- **Scenario:** Existing Documentation Article Updated
  - Input: Documentation Management System emits `UpdateEvent(id="article-456", last_updated=2024-01-02T12:00:00Z)`
  - Outcome: Service retrieves article "article-456" via API, preprocesses its title and content, and updates the corresponding document in the Search Index with `document_id="article-456"` and `type="article"`. The `updated_at` field in the search index is updated to 2024-01-02T12:00:00Z.

- **Scenario:** Indexing Fails Temporarily
  - Input: Ticketing System emits `UpdateEvent(id="ticket-789", last_updated=2024-01-03T14:00:00Z)`, but the Search Index Provider is temporarily unavailable.
  - Outcome: Service logs the error, retries indexing "ticket-789" after 1 second, 4 seconds, and 16 seconds. If all retries fail, the error is logged again, and the indexing is abandoned for that event.

- **Scenario:** Health Check Request
  - Input: `GET /health` endpoint is called.
  - Outcome: Service returns a 200 status code if it's running and can connect to the Search Index Provider and internal APIs. Otherwise, it returns a 500 status code with a descriptive error message.

- **Scenario:** Documentation Article is indexed before a Ticket.
  - Input: Ticketing System emits `UpdateEvent(id="ticket-999", last_updated=2024-03-01T00:00:00Z)` and Documentation Management System emits `UpdateEvent(id="article-888", last_updated=2024-02-29T00:00:00Z)`. The service receives both events within a short timeframe.
  - Outcome:  The service prioritizes processing the Documentation Article (`article-888`) first, indexing its content before proceeding with the ticket (`ticket-999`).  This is achieved via a priority queue or similar mechanism within the service.

## Out of Scope

- UI for searching the index.
- Defining the specific Search Index Provider (e.g., Elasticsearch cluster details). This is configuration.
- User authentication and authorization.
- Detailed monitoring and alerting setup. This will be handled by a separate monitoring service.
- Creation of the Ticketing System API or Documentation Management System API.
- Schema definition within the Search Index Provider. The service only needs to write, update, and delete documents based on the provided schema.
