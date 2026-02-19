"""
FACTORY SCRIBE — Living Documentation Agent
Halilit Support Center v9.6.1 Dark Factory

Reads the actual codebase and regenerates docs/ARCHITECTURE.md to reflect
the real current state of the application.

Usage:
    python backend/factory/scribe_agent.py
    # OR via factory.py:
    python factory.py doc
"""
from pathlib import Path

try:
    from agent_core import query_llm, save_artifact
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

SYSTEM_PROMPT = """
You are the FACTORY SCRIBE — a technical writer agent.
You read real source code and produce accurate, concise living documentation.

OUTPUT RULES:
- Write valid Markdown only.
- Be factual — only describe what you can see in the code provided.
- Do NOT invent features, endpoints, or components that are not in the code.
- Use ## headings, bullet lists, and inline code ticks liberally.
- Keep it under 400 lines — this is a reference document, not a novel.
"""

# Files the Scribe reads (relative to project root, first N chars each)
READ_PLAN: list[tuple[str, int]] = [
    # Frontend views
    ("frontend/src/components/views/DashboardView.tsx", 1200),
    ("frontend/src/components/views/InventoryView.tsx", 1200),
    ("frontend/src/components/views/ProductDetailView.tsx", 1200),
    # Hooks
    ("frontend/src/hooks/useConductorCatalog.ts", 800),
    ("frontend/src/hooks/useJITIntelligence.ts", 800),
    # Store
    ("frontend/src/store/navigationStore.ts", 600),
    # Backend core
    ("backend/server.py", 1200),
    ("backend/jit_agent.py", 800),
    ("backend/product_normalizer.py", 600),
    # Factory agents
    ("backend/factory/builder_agent.py", 600),
    ("backend/factory/steerer_agent.py", 600),
    ("backend/factory/scribe_agent.py", 300),
    ("backend/factory/spec_writer.py", 300),
    # Config
    ("factory.py", 600),
    ("backend/source_rules.py", 600),
]


def _read_snapshot() -> str:
    """Build a trimmed snapshot of the codebase."""
    parts: list[str] = []
    for rel_path, max_chars in READ_PLAN:
        full = PROJECT_ROOT / rel_path
        if not full.exists():
            parts.append(f"\n### {rel_path}\n_(file not found)_\n")
            continue
        content = full.read_text(encoding="utf-8", errors="replace")
        truncated = content[:max_chars]
        suffix = "\n… [truncated]" if len(content) > max_chars else ""
        parts.append(f"\n### {rel_path}\n```\n{truncated}{suffix}\n```\n")
    return "\n".join(parts)


def update_docs() -> None:
    print("📚  Scribe is reading the codebase…")
    snapshot = _read_snapshot()

    prompt = f"""
CODEBASE SNAPSHOT (real source files):
{snapshot}

TASK:
Rewrite `docs/ARCHITECTURE.md` to accurately describe the current application.

Structure the document as:
1. **Overview** — one paragraph about what the app is and does.
2. **Frontend Views** — for each view: component name, route/state, and what it renders.
3. **Hooks & State** — list each hook and store with its purpose and return shape.
4. **Backend API** — list the key FastAPI endpoints (method, path, what it returns).
5. **Data Pipeline** — describe the flow: scraper → normalizer → catalog → frontend.
6. **Factory Agents** — list each agent in backend/factory/ with one-line description.
7. **Key Conventions** — imports, naming, Tailwind theme tokens, source rules.

Base everything strictly on the code snapshot above. Be accurate. Be concise.
"""

    print("✍️   Generating updated ARCHITECTURE.md…")
    # Summarising code into docs is perfect for the fast/cheap tier
    new_docs = query_llm(SYSTEM_PROMPT, prompt,
                         temperature=0.2, model_tier="fast")

    if not new_docs:
        print("❌  Scribe received no response.")
        return

    out_path = DOCS_DIR / "ARCHITECTURE.md"
    save_artifact(str(out_path), new_docs)
    print(f"✅  Documentation synced → {out_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    update_docs()
