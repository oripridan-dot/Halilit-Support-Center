# Spec: Trie-Based Search Index Builder

**Target:** data_pipeline/trie_search_index.py

## Overview
This script builds a Trie-based search index from the Halilit Support Center's knowledge base articles, optimized for fast prefix-based search. The index will be serialized to a file for later use by the search service. The knowledge base articles are sourced from the main database.

## Requirements
- The script must connect to the Halilit Support Center's database.
- The script must fetch all knowledge base articles from the `knowledge_base_articles` table.
- The script must construct a Trie data structure using the article titles as keys.
- The Trie must support prefix-based search, returning a list of article IDs matching the prefix.
- The script must serialize the Trie to a file.
- The script must handle database connection errors gracefully.
- The script must be idempotent, meaning running it multiple times should produce the same serialized Trie if the underlying data hasn't changed.
- The script must log its progress and any errors encountered.
- The script should use an environment variable `DATABASE_URL` to configure the database connection string.
- The script should use an environment variable `TRIE_INDEX_PATH` to specify where the trie will be saved.

## Data Contract
- **Input:** Knowledge base articles from the database, structured as follows:

  ```python
  from pydantic import BaseModel
  from typing import Optional

  class Article(BaseModel):
      id: int
      title: str
      content: str
      created_at: datetime
      updated_at: Optional[datetime] = None
  ```
- **Output:** A serialized Trie data structure, saved to the file specified by `TRIE_INDEX_PATH`. The Trie stores a mapping between article titles and article IDs. The serialized format should allow for efficient deserialization.  Consider `pickle` or `json` for initial implementation, but `protobuf` or other binary format can be considered if performance becomes a bottleneck.

## Behavior Scenarios
- **Scenario:** Initial Trie Creation
  - Input: Empty Trie index file, 1000 knowledge base articles in the database.
  - Outcome: A new Trie index file is created, containing all 1000 articles. The script logs the number of articles processed.
- **Scenario:** Trie Update with New Articles
  - Input: Existing Trie index file, 10 new knowledge base articles added to the database.
  - Outcome: The existing Trie index file is updated to include the 10 new articles. The script logs the number of articles processed (should be 10).
- **Scenario:** Database Connection Failure
  - Input: Invalid database connection string in `DATABASE_URL`.
  - Outcome: The script logs an error message indicating the database connection failure and exits gracefully, without modifying the existing Trie file.
- **Scenario:** Existing Trie Corrupted
    - Input: Existing TRIE index file is corrupted and cannot be deserialized.
    - Outcome: The script logs a warning that the Trie file is corrupted, rebuilds the trie from scratch, and saves a new Trie index file.
- **Scenario:** Trie already up to date
    - Input: Existing Trie index file, no changes to the `knowledge_base_articles` table since last run.
    - Outcome: The script does nothing.

## Out of Scope
- Real-time updates to the Trie index as articles are created or updated.
- Advanced text processing techniques (e.g., stemming, lemmatization).
- Complex ranking or scoring of search results.
- GUI for manually triggering index creation.
- Authentication/Authorization.

```python
import os
import logging
import pickle
from typing import List
from datetime import datetime

import psycopg2
from psycopg2 import OperationalError
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Article(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime | None = None

class TrieNode:
    def __init__(self):
        self.children = {}
        self.article_ids = [] # Store a list of article IDs for each prefix


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, title: str, article_id: int):
        node = self.root
        for char in title.lower():  # Consistent case
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.article_ids.append(article_id) # Store the article ID at each prefix level

    def search(self, prefix: str) -> List[int]:
        node = self.root
        for char in prefix.lower(): # Consistent case
            if char not in node.children:
                return []  # Prefix not found
            node = node.children[char]
        return node.article_ids

def create_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set.")

    try:
        conn = psycopg2.connect(db_url)
        return conn
    except OperationalError as e:
        logging.error(f"Database connection error: {e}")
        raise

def fetch_articles(conn) -> List[Article]:
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, content, created_at, updated_at FROM knowledge_base_articles")
            articles_data = cur.fetchall()
            articles = [Article(id=row[0], title=row[1], content=row[2], created_at=row[3], updated_at=row[4]) for row in articles_data]
            return articles
    except Exception as e:
        logging.error(f"Error fetching articles: {e}")
        raise

def build_trie(articles: List[Article]) -> Trie:
    trie = Trie()
    for article in articles:
        trie.insert(article.title, article.id)
    return trie

def serialize_trie(trie: Trie, filepath: str):
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(trie, f)
        logging.info(f"Trie serialized to {filepath}")
    except Exception as e:
        logging.error(f"Error serializing trie: {e}")
        raise

def deserialize_trie(filepath: str) -> Trie | None:
    try:
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        logging.warning(f"Trie file not found at {filepath}. Building from scratch.")
        return None
    except Exception as e:
        logging.warning(f"Error deserializing trie from {filepath}: {e}. Building from scratch.")
        return None



def main():
    trie_index_path = os.environ.get("TRIE_INDEX_PATH")
    if not trie_index_path:
        logging.error("TRIE_INDEX_PATH environment variable not set.")
        return

    try:
        conn = create_db_connection()
        articles = fetch_articles(conn)
        conn.close()

        existing_trie = deserialize_trie(trie_index_path)

        if existing_trie:
            # Check if the existing Trie contains all the articles.  A simple way to do this is to compare the length of the serialized
            # article IDs versus the total articles.  If they're equal, it means no update is needed.  A more robust and efficient approach would
            # be to store a hash of the articles when building the Trie, and comparing it to a newly generated hash.
            all_article_ids = []
            for article in articles:
                all_article_ids.append(article.id)

            num_articles_in_trie = 0
            for char, node in existing_trie.root.children.items():
                num_articles_in_trie += len(node.article_ids)

            if len(articles) == num_articles_in_trie:
                logging.info("Trie is already up to date. Skipping rebuild.")
                return # Trie already up to date.
            else:
                logging.info("Trie needs to be updated.")
        else:
            logging.info("No Trie found.  Building a new one.")



        trie = build_trie(articles)
        serialize_trie(trie, trie_index_path)
        logging.info("Trie index creation complete.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
```
