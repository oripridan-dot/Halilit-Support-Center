"""
HIPPOCAMPUS — backend/factory/hippocampus.py
============================================
The Swarm's long-term vector memory engine.

Prevents "Context Collapse" by embedding every deployed file's intent into a
local ChromaDB vector database.  Agents query the Hippocampus instead of
brute-force-scanning the full repository, reducing prompt sizes by ~90%.

Architecture role: Gap 1 — Vector Memory (Level 6.5)

Public API
----------
    hippocampus.embed_code(filepath, description, ast_content)
    hippocampus.recall(intent_query, n_results=2) -> list[dict]
    swarm_memory  — singleton shared across the Swarm

ChromaDB storage location: backend/data/vector_db/
"""
from __future__ import annotations

import os
from pathlib import Path

import chromadb

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "backend" / "data" / "vector_db"


class Hippocampus:
    """Local vector database that stores and retrieves code by semantic intent."""

    def __init__(self) -> None:
        """Initializes the physical neural pathways (Local Vector DB)."""
        DB_PATH.mkdir(parents=True, exist_ok=True)

        # Persistent local ChromaDB client — survives process restarts
        self.client = chromadb.PersistentClient(path=str(DB_PATH))

        # One collection per codebase; cosine similarity for code intent matching
        self.collection = self.client.get_or_create_collection(
            name="factory_ast_memory",
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def embed_code(self, filepath: str, description: str, ast_content: str) -> None:
        """
        Stores a file's intent and physical code in long-term memory.

        Called by the Scribe/Builder agents after a successful deployment so
        every launched module is permanently searchable by semantic intent.

        Args:
            filepath:    Repo-relative (or absolute) path to the deployed file.
            description: One-sentence human-readable purpose of the file.
            ast_content: The actual code content (AST or full source) to embed.
        """
        key = str(filepath)
        print(f"🧠 Hippocampus: Embedding memory for {key}...")
        self.collection.upsert(
            documents=[ast_content],
            metadatas=[{"filepath": key, "description": description}],
            ids=[key],
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def recall(self, intent_query: str, n_results: int = 2) -> list[dict]:
        """
        Retrieves the exact AST nodes needed based on a semantic query.

        Prevents Context Collapse by returning only the N most relevant code
        fragments rather than forcing agents to load the entire repository.

        Args:
            intent_query: Natural-language description of the feature/component needed.
            n_results:    Number of memory fragments to return (default 2).

        Returns:
            List of dicts with keys: filepath, description, content.
        """
        print(f"💭 Hippocampus: Recalling memory for '{intent_query}'...")

        # Guard: collection may be empty on first run
        collection_count = self.collection.count()
        if collection_count == 0:
            print("   ⚠️  Hippocampus is empty — no memories encoded yet.")
            return []

        actual_n = min(n_results, collection_count)
        results = self.collection.query(
            query_texts=[intent_query],
            n_results=actual_n,
        )

        memory_fragments: list[dict] = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                memory_fragments.append(
                    {
                        "filepath": results["metadatas"][0][i]["filepath"],
                        "description": results["metadatas"][0][i]["description"],
                        "content": results["documents"][0][i],
                    }
                )

        return memory_fragments

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def forget(self, filepath: str) -> None:
        """Remove a specific file's memory (e.g. after deletion/rename)."""
        try:
            self.collection.delete(ids=[str(filepath)])
            print(f"🧹 Hippocampus: Forgot {filepath}")
        except Exception as exc:
            print(f"   ⚠️  Could not forget {filepath}: {exc}")

    def count(self) -> int:
        """Return the number of memories currently stored."""
        return self.collection.count()

    def status(self) -> str:
        """One-line status string for health checks."""
        n = self.count()
        return f"Hippocampus: {n} memory fragment(s) stored at {DB_PATH}"


# ---------------------------------------------------------------------------
# Singleton — shared across the entire Swarm
# ---------------------------------------------------------------------------
try:
    swarm_memory = Hippocampus()
except Exception as _init_err:  # noqa: BLE001
    # Fail gracefully so imports don't crash agents that don't use memory
    import logging as _logging
    _logging.warning("Hippocampus could not initialise: %s", _init_err)

    class _NullHippocampus:
        """Drop-in no-op replacement when ChromaDB is unavailable."""

        def embed_code(self, *_args: object, **_kw: object) -> None:
            pass

        def recall(self, *_args: object, **_kw: object) -> list:
            return []

        def forget(self, *_args: object, **_kw: object) -> None:
            pass

        def count(self) -> int:
            return 0

        def status(self) -> str:
            return "Hippocampus: OFFLINE (ChromaDB unavailable)"

    swarm_memory = _NullHippocampus()  # type: ignore[assignment]
