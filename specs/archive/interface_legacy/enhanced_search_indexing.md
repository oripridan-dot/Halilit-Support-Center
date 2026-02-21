# Spec: Enhanced Search Indexing

**Target:** data_pipeline/scripts/enhanced_search_indexing.py

## Overview
This script enhances the search indexing process for the Halilit Support Center's "Dark Factory" knowledge base. It enriches existing content with supplementary data, optimizes the indexing schema for faster and more relevant search results, and ensures the index remains up-to-date with minimal disruption to the factory operations.

## Requirements
- The script must read raw data from the existing data warehouse (assumed to be accessible via SQL).
- The script must connect to the existing search index (assumed to be Elasticsearch) to update/create new indices.
- The script must enrich the raw data with relevant metadata. This includes:
    - Adding related terms/synonyms based on a pre-existing taxonomy file (JSON format).
    - Calculating document importance based on link analysis of internal documents (PageRank algorithm).
- The script must optimize the search index schema for the following search features:
    - Keyword search
    - Fuzzy search (edit distance <= 2)
    - Phrase search
    - Exact match search
- The script must implement a locking mechanism to prevent concurrent index updates.
- The script must log all indexing activities, including errors and warnings, to a file.
- The script must be configurable via environment variables or a configuration file (TOML format).
- The script must handle incremental updates, processing only documents that have been modified since the last indexing run.
- The script must support full re-indexing when necessary.
- The script must be idempotent: running it multiple times with the same data should produce the same index.
- The script must conform to the Three Source Rule for all data access (i.e., no hardcoded constants).

## Data Contract

**Input (from Data Warehouse - assumed SQL database):**

Raw document data is retrieved from a SQL database (credentials provided via environment variables).  The assumed schema for the `documents` table is as follows:

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    last_modified TIMESTAMP NOT NULL,
    category TEXT,
    tags TEXT
);
```

**Input (Taxonomy file - JSON):**

```json
{
  "machine_maintenance": ["preventative maintenance", "breakdown repair", "lubrication"],
  "quality_control": ["inspection", "testing", "calibration"],
  "robotics": ["automation", "programming", "sensors"]
}
```

**Output (to Elasticsearch):**

The script updates or creates documents in the Elasticsearch index.  The document structure sent to Elasticsearch is:

```json
{
  "id": "integer",
  "title": "string",
  "content": "string",
  "last_modified": "string (ISO 8601 format)",
  "category": "string",
  "tags": "array of strings",
  "related_terms": "array of strings",
  "importance_score": "float"
}
```

**Configuration (TOML):**

```toml
[database]
host = "db.example.com"
port = 5432
user = "dbuser"
password = "dbpassword"
database_name = "halilit_data"

[elasticsearch]
host = "es.example.com"
port = 9200
index_name = "halilit_knowledge_base"

[taxonomy]
file_path = "data/taxonomy.json"

[indexing]
batch_size = 1000
page_rank_damping_factor = 0.85
```

## Behavior Scenarios

- **Scenario:** Initial Indexing
  - Input: Empty Elasticsearch index, populated `documents` table in the SQL database.
  - Outcome: All documents from the SQL database are indexed into Elasticsearch, including `related_terms` from the taxonomy file and `importance_score` calculated via PageRank.  The index is created with optimized mappings.

- **Scenario:** Incremental Indexing
  - Input: Elasticsearch index exists. The `documents` table has been updated with a new document and an existing document has been modified (different `last_modified` timestamp).
  - Outcome: Only the new and modified documents are indexed. The existing documents in the index are updated accordingly.

- **Scenario:** Re-indexing
  - Input: Request to trigger a full re-indexing (command-line argument or environment variable).
  - Outcome: The Elasticsearch index is cleared (or a new index is created and then aliased). All documents are re-indexed from the SQL database, including calculating the PageRank scores from scratch.

- **Scenario:** Database Connection Failure
  - Input: The SQL database is unavailable.
  - Outcome: The script logs an error message and exits gracefully. It does *not* modify the Elasticsearch index.

- **Scenario:** Elasticsearch Connection Failure
  - Input: Elasticsearch is unavailable.
  - Outcome: The script logs an error message and exits gracefully. It does *not* modify the SQL database.

- **Scenario:** Taxonomy File Not Found
    - Input: The taxonomy file specified in the configuration is not found.
    - Outcome: The script logs an error message indicating the missing file and exits gracefully. It does *not* modify the Elasticsearch index.

- **Scenario:** Concurrent Execution
  - Input: The script is launched while another instance is already running.
  - Outcome: The second instance detects the existing lock, logs a message indicating the conflict, and exits gracefully. The first instance continues its indexing process uninterrupted.

## Out of Scope
- Defining the exact PageRank implementation algorithm (it's assumed to be available as a library or module).
- Detailed specification of Elasticsearch mappings (the script should infer them from the data).
- Monitoring of the data pipeline performance or health.
- Implementing a user interface for managing the indexing process.
- Automated deployment of the script.
