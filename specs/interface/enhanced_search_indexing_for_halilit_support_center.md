# Spec: Enhanced Search Indexing for Halilit Support Center

**Target:** data_pipeline/scripts/enhanced_search_indexing.py

## Overview
This script enhances the search indexing process for the Halilit Support Center by incorporating stemming, stop word removal, and synonym expansion to improve search result relevance and accuracy. This will lead to improved customer satisfaction by enabling them to find the information they need more quickly and easily.

## Requirements
- [x] Implement stemming using the NLTK library to reduce words to their root form.
- [x] Implement stop word removal using the NLTK library to eliminate common words that do not contribute to search meaning.
- [x] Implement synonym expansion using a pre-defined synonym dictionary or a more advanced technique like WordNet (NLTK).
- [x] The script should connect to the Halilit Support Center's existing data sources (e.g., database, knowledge base articles, chat logs) via configured credentials and API endpoints.
- [x] The script must index all relevant data, including article titles, content, keywords, chat logs, and forum posts.
- [x] The script should integrate with the existing search engine (specify Elasticsearch, including version).
- [x] The script should be configurable via environment variables for settings like data source credentials, search engine host, index name, and synonym dictionary path.
- [x] Implement logging to track the indexing progress and any errors encountered.
- [x] The script must be idempotent: running it multiple times should not create duplicate entries or corrupt the index.
- [x] The script should be able to perform a full re-index or an incremental index based on a timestamp of the last update.

## Data Contract

**Input:**

*   **Environment Variables:**
    *   `DATABASE_URL`: (string) Connection string to the Halilit Support Center database.
    *   `ELASTICSEARCH_HOST`: (string) Hostname/IP address of the Elasticsearch server.
    *   `ELASTICSEARCH_PORT`: (integer) Port number of the Elasticsearch server.
    *   `ELASTICSEARCH_INDEX_NAME`: (string) Name of the Elasticsearch index to use.
    *   `SYNONYM_DICTIONARY_PATH`: (string, optional) Path to a JSON file containing synonym mappings.
    *   `LAST_INDEXED_TIMESTAMP`: (string, optional, ISO 8601 format)  Timestamp to use for incremental indexing. If not provided, a full re-index will be performed.

*   **Synonym Dictionary (Optional JSON File):**
    ```json
    {
        "customer": ["client", "user", "consumer"],
        "issue": ["problem", "error", "bug", "fault"],
        "shipping": ["delivery", "transport", "dispatch"]
    }
    ```

**Output:**

*   No direct output to stdout.
*   Data indexed in Elasticsearch.
*   Logs indicating progress and any errors encountered.

## Behavior Scenarios

- **Scenario: Full Re-Index**
  - Input: Script is executed with `LAST_INDEXED_TIMESTAMP` environment variable not set.
  - Outcome: All relevant data sources are read, processed (stemming, stop word removal, synonym expansion), and indexed into Elasticsearch.  Existing index is either deleted and recreated, or all documents are deleted and re-indexed.

- **Scenario: Incremental Index**
  - Input: Script is executed with `LAST_INDEXED_TIMESTAMP` environment variable set to "2024-01-01T00:00:00Z".
  - Outcome: Only data modified or created since "2024-01-01T00:00:00Z" in the relevant data sources are read, processed, and indexed into Elasticsearch.

- **Scenario: Synonym Expansion**
  - Input: A document containing the word "customer" is processed, with a synonym dictionary defined as in the Data Contract.
  - Outcome: The indexed document in Elasticsearch contains not only "customer" but also "client", "user", and "consumer" (or a combined term like "customer client user consumer") in the relevant field(s).

- **Scenario: Stop Word Removal**
  - Input: A document containing the sentence "This is a test document" is processed.
  - Outcome: The indexed document in Elasticsearch contains only "test" and "document" (assuming "this", "is", and "a" are in the NLTK stop word list).

- **Scenario: Indexing Failure (Database Connection)**
  - Input: Script is executed with an invalid `DATABASE_URL`.
  - Outcome: Script logs an error message indicating database connection failure and exits with a non-zero exit code.

- **Scenario: Indexing Failure (Elasticsearch Connection)**
    - Input: Script is executed with an invalid `ELASTICSEARCH_HOST`.
    - Outcome: Script logs an error message indicating Elasticsearch connection failure and exits with a non-zero exit code.

## Out of Scope
- UI for monitoring indexing progress.
- Automated deployment of the script.
- Real-time indexing.
- Implementing a custom stop word list beyond the NLTK default.
- Implementing custom stemming algorithms.
-  Handling data source schema changes. This assumes a stable data model.
