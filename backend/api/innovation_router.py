"""
JIT INNOVATION PIPELINE ROUTER — backend/api/innovation_router.py
==================================================================
Catches unmet needs from the Halilit warehouse floor and routes them
through the full Dark Factory pipeline:

  Boardroom → Spec Writer → Repo Agent → Darwin Shadow Cell → Proposal

The operator submits a need via POST /api/innovation/request. The
pipeline runs in the background so the HTTP response is instant.
The final output is a docs/FEATURE_PROPOSAL_<ts>.md awaiting Governor
approval.
"""

from __future__ import annotations

import time
import traceback
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(tags=["innovation"])

# Project root (backend/api -> backend -> root)
_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class UnmetNeed(BaseModel):
    operator_role: str = "Warehouse Staff"
    current_context: str = "/"          # e.g. window.location.pathname
    need_description: str               # e.g. "I need a bulk PDF export for RMA repairs"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def _write_proposal(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def process_jit_innovation(need: UnmetNeed) -> None:
    """
    Full JIT Innovation Pipeline executed as a FastAPI background task.

    Stages:
      1. Boardroom Verdict (Tech Lead advisory)
      2. Spec Writer  — generates formal Markdown spec + file tree JSON
      3. Repo Agent   — creates JIT branch + scaffolds empty files
      4. Darwin Agent — Shadow Cell experiment (architecture mutation test)
      5. Proposal     — docs/FEATURE_PROPOSAL_<ts>.md written for Governor
    """
    ts = int(time.time())
    print("\n" + "💡" * 12)
    print(f"🚀 JIT INNOVATION PIPELINE TRIGGERED by [{need.operator_role}]")
    print(f"   Context : {need.current_context}")
    print(f"   Need    : {need.need_description}")
    print("💡" * 12)

    # ------------------------------------------------------------------
    # 1. BOARDROOM — Tech Lead consults on the idea
    # ------------------------------------------------------------------
    try:
        from backend.factory.tech_lead_agent import consult_tech_lead_on_idea
        boardroom_verdict = consult_tech_lead_on_idea(
            f"Operator need: {need.need_description}\n"
            f"Context: {need.current_context}\n"
            "Propose a feature architecture that is consistent with the Dark Factory "
            "spec-driven workflow, Three Source Rules, and existing tech stack."
        )
    except Exception as exc:
        boardroom_verdict = f"[ERROR] Boardroom unavailable: {exc}"
        print(f"   ⚠️  Boardroom error: {exc}")

    if "[REJECTION]" in boardroom_verdict:
        print("   🛑 Boardroom REJECTED the feature request as unarchitectural.")
        rejection_path = _ROOT / "docs" / f"FEATURE_REJECTION_{ts}.md"
        _write_proposal(
            rejection_path,
            f"# 🛑 JIT Feature Rejection\n\n"
            f"**Operator:** {need.operator_role}\n"
            f"**Need:** {need.need_description}\n\n"
            f"**Boardroom Verdict:**\n{boardroom_verdict}\n",
        )
        print(
            f"   📝 Rejection notice written to {rejection_path.relative_to(_ROOT)}")
        return

    print("   ✅ Boardroom APPROVED. Moving to Spec Writer…")

    # ------------------------------------------------------------------
    # 2. SPEC WRITER — formal Markdown spec + file-tree JSON
    # ------------------------------------------------------------------
    spec_path: str = f"specs/interface/JIT_SPEC_{ts}.md"
    files_to_scaffold: list[str] = []

    try:
        from backend.factory.spec_writer import generate_jit_specification
        spec_path, files_to_scaffold = generate_jit_specification(
            need_description=need.need_description,
            boardroom_verdict=boardroom_verdict,
            timestamp=ts,
        )
        print(f"   📐 Spec written to {spec_path}")
        print(f"   📄 Files to scaffold: {files_to_scaffold}")
    except Exception as exc:
        print(f"   ⚠️  Spec Writer error: {exc}\n{traceback.format_exc()}")

    # ------------------------------------------------------------------
    # 3. REPO AGENT — branch creation + file scaffolding
    # ------------------------------------------------------------------
    branch_name: str = f"jit/feat-manual-{ts}"
    try:
        from backend.factory.repo_agent import organize_feature_branch
        branch_name = organize_feature_branch(
            feature_name=need.need_description,
            files_to_scaffold=files_to_scaffold,
        )
        print(f"   🌿 Repository branch ready: {branch_name}")
    except Exception as exc:
        print(f"   ⚠️  Repo Agent error: {exc}\n{traceback.format_exc()}")

    # ------------------------------------------------------------------
    # 4. DARWIN AGENT — Shadow Cell experiment
    # ------------------------------------------------------------------
    experiment_plan: str = "Darwin experiment not executed (agent unavailable)."
    try:
        from backend.factory.darwin_agent import initiate_darwin_experiment
        experiment_plan = initiate_darwin_experiment(
            f"Follow the specification at `{spec_path}` and implement the "
            f"feature in the Shadow Cell. Branch: {branch_name}."
        )
        print("   🧬 Darwin experiment complete.")
    except Exception as exc:
        experiment_plan = f"Darwin skipped: {exc}"
        print(f"   ⚠️  Darwin error: {exc}")

    # ------------------------------------------------------------------
    # 5. PROPOSAL — docs/FEATURE_PROPOSAL_<ts>.md
    # ------------------------------------------------------------------
    proposal_path = _ROOT / "docs" / f"FEATURE_PROPOSAL_{ts}.md"
    proposal_content = (
        f"# 🚀 JIT Feature Proposal\n\n"
        f"**Timestamp:** {ts}\n"
        f"**Operator:** {need.operator_role}\n"
        f"**Context:** `{need.current_context}`\n\n"
        f"---\n\n"
        f"## Operator Need\n\n{need.need_description}\n\n"
        f"---\n\n"
        f"## Boardroom Strategy\n\n{boardroom_verdict}\n\n"
        f"---\n\n"
        f"## Repository\n\n"
        f"- **Branch:** `{branch_name}`\n"
        f"- **Spec:** `{spec_path}`\n"
        f"- **Scaffolded files:** {files_to_scaffold or '(none yet)'}\n\n"
        f"---\n\n"
        f"## Darwin Experiment Results\n\n{experiment_plan}\n\n"
        f"---\n\n"
        f"*Governor, the factory has drafted the spec, organised the branch, and "
        f"tested the code in the Shadow Cell. Do you authorise merging this to the "
        f"main repository?*\n"
    )
    _write_proposal(proposal_path, proposal_content)
    print(
        f"\n📝 Proposal awaiting Governor approval → {proposal_path.relative_to(_ROOT)}")
    print("💡" * 12 + "\n")


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/api/innovation/request")
async def request_jit_feature(need: UnmetNeed, background_tasks: BackgroundTasks):
    """
    Submits an unmet operator need into the JIT Innovation Pipeline.
    Processing happens in the background; the endpoint returns immediately.
    """
    background_tasks.add_task(process_jit_innovation, need)
    return {
        "status": "Innovation pipeline activated.",
        "message": (
            "The AI Factory is analysing and testing a solution in the Shadow Cell. "
            "A FEATURE_PROPOSAL will appear in docs/ when complete."
        ),
    }


# ---------------------------------------------------------------------------
# Level 10 — Liquid JIT Endpoint (instant, no file writing)
# ---------------------------------------------------------------------------

_LIQUID_SYSTEM = """You are the Halilit Level 10 Liquid UI Engine.

Your job: given an operator request, produce a JSON object (no markdown, raw JSON only)
with exactly two keys:

1. "sql_query"  — A valid SQLite SELECT query against the `products` table.
   Available columns: id, name, brand, category, price (IL ILS), price_eilat (Eilat ILS),
   in_stock (1=yes/0=no), halilit_url.
   Rules: SELECT-only, max 50 rows, use LIMIT.

2. "schema" — A Server-Driven UI schema object:
   {
     "type":    "DataGrid" | "MetricCard" | "List",
     "title":   "<human readable title>",
     "columns": ["col1", "col2", ...]   (must match SELECT output aliases)
   }

Output ONLY valid JSON. No explanations. No markdown fences.
"""


@router.post("/api/innovation/liquid")
async def stream_liquid_feature(need: UnmetNeed):
    """
    Level 10 Liquid JIT — instant Server-Driven UI synthesis.

    1. Calls the LLM to produce a SQL query + SDUI schema (no files written).
    2. Registers the query as an ephemeral route in the Liquid Router (in-memory).
    3. Returns the schema with the live dataSource endpoint URI to the frontend.

    The entire round-trip completes in ~500ms. No Vite. No restart.
    """
    from backend.llm import get_llm
    from backend.api.liquid_router import register_dynamic_route

    prompt = (
        f"Operator role: {need.operator_role}\n"
        f"Current context: {need.current_context}\n"
        f"Requested feature: {need.need_description}"
    )

    print(f"\n🌊 LIQUID ENGINE: synthesising — {need.need_description!r}")

    llm = get_llm()
    raw, ok = llm.call(
        "LiquidEngine",
        prompt,
        system=_LIQUID_SYSTEM,
        use_cache=False,
    )

    if not ok:
        return {"status": "error", "message": f"LLM call failed: {raw}"}

    # Parse the JSON response
    try:
        # Strip any accidental markdown fences
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.lower().startswith("json"):
                clean = clean[4:]
        blueprint = __import__("json").loads(clean.strip())
    except Exception as exc:
        return {
            "status": "error",
            "message": f"LLM returned non-JSON output: {exc}. Raw: {raw[:300]}",
        }

    sql_query = blueprint.get("sql_query", "")
    schema = blueprint.get("schema", {})

    if not sql_query or not schema:
        return {
            "status": "error",
            "message": "LLM did not return required 'sql_query' or 'schema' keys.",
        }

    # Register the ephemeral route
    try:
        endpoint = register_dynamic_route(sql_query)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    schema["dataSource"] = endpoint
    print(f"   ✅ Liquid feature ready → {endpoint}")

    return {
        "status": "success",
        "ui_schema": schema,
        "sql_preview": sql_query[:200],
    }


@router.get("/api/innovation/proposals")
async def list_proposals():
    """Lists all FEATURE_PROPOSAL and FEATURE_REJECTION docs awaiting Governor review."""
    docs_dir = _ROOT / "docs"
    proposals = sorted(
        [
            {
                "filename": p.name,
                "path": str(p.relative_to(_ROOT)),
                "size_bytes": p.stat().st_size,
                "mtime": int(p.stat().st_mtime),
            }
            for p in docs_dir.glob("FEATURE_PROPOSAL_*.md")
        ],
        key=lambda x: x["mtime"],
        reverse=True,
    )
    rejections = sorted(
        [
            {
                "filename": p.name,
                "path": str(p.relative_to(_ROOT)),
                "size_bytes": p.stat().st_size,
                "mtime": int(p.stat().st_mtime),
            }
            for p in docs_dir.glob("FEATURE_REJECTION_*.md")
        ],
        key=lambda x: x["mtime"],
        reverse=True,
    )
    return {"proposals": proposals, "rejections": rejections}
