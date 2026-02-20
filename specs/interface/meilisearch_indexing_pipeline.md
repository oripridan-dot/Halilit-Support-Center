# Spec: MeiliSearch Indexing Pipeline

**Target:** data_pipeline/meilisearch_integration.py

## Overview
This data pipeline script automates the indexing of support tickets in MeiliSearch to enable fast and relevant search capabilities within the Halilit Support Center. It retrieves ticket data from the existing database (assumed to exist), transforms it into a suitable format for MeiliSearch, and uploads it to the MeiliSearch index. The script will be designed to run periodically to keep the index up-to-date with new and modified tickets.

## Requirements
- The script must connect to the existing Halilit Support Center database (connection details configured via environment variables).
- The script must fetch all support tickets from the `support_tickets` table (or equivalent table holding ticket data).
- The script must transform the ticket data into a format suitable for MeiliSearch indexing. Specifically, each ticket should include fields for: `id`, `subject`, `body`, `status`, `priority`, `created_at`, `updated_at`, `customer_id`, and `agent_id`.
- The script must connect to a MeiliSearch instance (connection details configured via environment variables).
- The script must index the transformed ticket data into a MeiliSearch index named 'support_tickets'.
- The script must configure MeiliSearch to use `id` as the primary key.
- The script must configure MeiliSearch to use `subject` and `body` as searchable attributes.
- The script must configure MeiliSearch to use `status`, `priority`, `created_at`, and `updated_at` as filterable attributes.
- The script must implement error handling and logging.  Specifically, connection errors to the database or MeiliSearch should be logged, and individual indexing errors should be logged without halting the entire process.
- The script should be designed to be run as a scheduled task (e.g., using cron or a similar scheduler).
- The script must be idempotent. Running the script multiple times without changes to the database should not result in duplicate entries in MeiliSearch.
- The script must handle large numbers of tickets efficiently, potentially using batch indexing.
- Credentials must be read from ENV variables.

## Data Contract

**Input (from `support_tickets` database table - example assumed schema):**

```python
# Assumed database schema (adapt to actual schema)
class SupportTicket(Base):  # Assuming SQLAlchemy or similar
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str]
    body: Mapped[str]
    status: Mapped[str]
    priority: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    customer_id: Mapped[int]
    agent_id: Mapped[int]

```

**Output (to MeiliSearch):**

```python
from typing import TypedDict

class MeiliSearchTicket(TypedDict):
    id: int
    subject: str
    body: str
    status: str
    priority: str
    created_at: str # ISO 8601 format
    updated_at: str # ISO 8601 format
    customer_id: int
    agent_id: int
```

## Behavior Scenarios

- **Scenario:** Initial Indexing
  - Input: Empty MeiliSearch index, `support_tickets` table contains 100 tickets.
  - Outcome: MeiliSearch index 'support_tickets' contains 100 documents, each representing a ticket from the database.  The settings are correctly configured (primary key, searchable attributes, filterable attributes).

- **Scenario:** New Ticket Created
  - Input: `support_tickets` table contains 101 tickets (one new ticket added since the last run).  The MeiliSearch index 'support_tickets' contains 100 documents.
  - Outcome: MeiliSearch index 'support_tickets' contains 101 documents, including the newly added ticket.

- **Scenario:** Ticket Updated
  - Input: A ticket in the `support_tickets` table is updated (e.g., status changes).  The MeiliSearch index contains the old version of the ticket.
  - Outcome: The MeiliSearch index is updated to reflect the changes made to the ticket.

- **Scenario:** Database Connection Failure
  - Input: The database is temporarily unavailable.
  - Outcome: The script logs an error message indicating the database connection failure and exits gracefully. MeiliSearch index remains unchanged.

- **Scenario:** MeiliSearch Connection Failure
  - Input: The MeiliSearch instance is temporarily unavailable.
  - Outcome: The script logs an error message indicating the MeiliSearch connection failure and exits gracefully. The database remains unchanged.

- **Scenario:** Invalid Data in `support_tickets`
  - Input: A ticket in `support_tickets` table has a `created_at` date that is incorrectly formatted.
  - Outcome: The script logs an error with the specific ticket ID and continues to index the remaining valid tickets. The malformed record is skipped.

## Out of Scope
- User interface for managing the indexing process.
- Real-time indexing (this is a batch process).
- Complex data transformations beyond the specified format.
- Alerting on indexing failures (beyond logging).
- Authentication to the Database (credentials are assumed to be valid)

```python
# data_pipeline/meilisearch_integration.py
import os
import asyncio
import logging
from datetime import datetime

import httpx
from meilisearch import Client
from meilisearch.errors import MeilisearchCommunicationError
from pydantic import BaseModel, Field

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration (replace with your actual settings)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")  # Example SQLite URL
MEILISEARCH_HOST = os.environ.get("MEILISEARCH_HOST", "http://localhost:7700")
MEILISEARCH_API_KEY = os.environ.get("MEILISEARCH_API_KEY", "masterKey")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Ticket Model (adjust to match your database schema)
class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str]
    body: Mapped[str]
    status: Mapped[str]
    priority: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    customer_id: Mapped[int]
    agent_id: Mapped[int]

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "body": self.body,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "customer_id": self.customer_id,
            "agent_id": self.agent_id,
        }



async def index_tickets():
    """
    Fetches tickets from the database, transforms them, and indexes them in MeiliSearch.
    """
    try:
        # Connect to MeiliSearch
        client = Client(MEILISEARCH_HOST, MEILISEARCH_API_KEY)
        logging.info(f"Connected to MeiliSearch at {MEILISEARCH_HOST}")
    except MeilisearchCommunicationError as e:
        logging.error(f"Failed to connect to MeiliSearch: {e}")
        return

    try:
        # Connect to the database
        db = SessionLocal()
        logging.info("Connected to the database")

        # Fetch tickets
        tickets = db.query(SupportTicket).all()
        logging.info(f"Fetched {len(tickets)} tickets from the database")

        # Transform tickets
        documents = [ticket.to_dict() for ticket in tickets]

    except Exception as e:
        logging.error(f"Failed to fetch or transform ticket data: {e}")
        db.close()
        return
    finally:
        db.close()


    try:
        # Index tickets in MeiliSearch
        index = client.index('support_tickets')

        # Set settings (only if index doesn't exist or settings need updating)
        settings = {
            'primaryKey': 'id',
            'searchableAttributes': ['subject', 'body'],
            'filterableAttributes': ['status', 'priority', 'created_at', 'updated_at']
        }
        await index.update_settings(settings)


        # Batch add documents
        batch_size = 100 # adjust based on performance
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                task = await index.add_documents(batch)
                logging.info(f"Added a batch of {len(batch)} documents to MeiliSearch. Task UID: {task.task_uid}")
            except httpx.HTTPStatusError as e:
                 logging.error(f"Failed to add documents to MeiliSearch: {e.response.status_code} - {e.response.json()}")
            except Exception as e:
                 logging.error(f"General error during MeiliSearch document addition: {e}")

        logging.info("Finished indexing tickets in MeiliSearch")

    except MeilisearchCommunicationError as e:
        logging.error(f"Failed to communicate with MeiliSearch during indexing: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during indexing: {e}")


async def main():
    await index_tickets()

if __name__ == "__main__":
    asyncio.run(main())
```