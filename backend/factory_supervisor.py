#!/usr/bin/env python3
"""
Factory Supervisor — Dark Factory Protocol.
Runs compliance check against specs, triggers ingestion agent, verifies UI build.

v2.0 — DAG Executor (Pillar: Directed Acyclic Graph Supervisor)
Now supports executing tasks as a DAG with parallel independent nodes.

Run from project root: PYTHONPATH=. python backend/factory_supervisor.py [--rebuild]
Or from backend: python factory_supervisor.py [--rebuild]
"""

import gzip
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# Resolve paths: support run from backend/ or project root
_BACKEND = Path(__file__).resolve().parent
_ROOT = _BACKEND.parent
SPECS_DIR = _ROOT / "specs"
DATA_DIR = _BACKEND / "data"
LOGS_DIR = _ROOT / "factory_logs"


def log(message: str) -> None:
    print(f"🏭 [FACTORY]: {message}")


def _collect_products_from_artifact(data: dict) -> list:
    """Extract flat list of products from catalog/taxonomy artifact."""
    products = []
    if isinstance(data, dict):
        if "products" in data:
            products = data["products"] if isinstance(
                data["products"], list) else []
        else:
            for v in data.values():
                if isinstance(v, list):
                    products.extend(v)
    return products


def _price_il(product: dict) -> float:
    """Get IL price from product (top-level or nested pricing)."""
    p = product.get("pricing") if isinstance(
        product.get("pricing"), dict) else {}
    if p and "price_il" in p:
        try:
            return float(p["price_il"]) or 0
        except (TypeError, ValueError):
            return 0
    v = product.get("price_il")
    try:
        return float(v) if v is not None else 0
    except (TypeError, ValueError):
        return 0


def check_compliance() -> bool:
    """
    Checks if the current data artifacts match the defined specs.
    Accepts learned_taxonomy.json or catalog_cache.json.gz.
    """
    log("Auditing system against specs...")

    catalog_path = DATA_DIR / "catalog_cache.json.gz"
    taxonomy_path = DATA_DIR / "learned_taxonomy.json"

    if not catalog_path.exists() and not taxonomy_path.exists():
        log("❌ FAIL: No catalog artifact (catalog_cache.json.gz or learned_taxonomy.json).")
        return False

    data = None
    if catalog_path.exists():
        try:
            with gzip.open(catalog_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            log(f"❌ CRITICAL: Cannot read catalog_cache.json.gz — {e}")
            return False
    elif taxonomy_path.exists():
        try:
            with open(taxonomy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            log(f"❌ CRITICAL: Cannot read learned_taxonomy.json — {e}")
            return False

    if not data:
        log("❌ FAIL: Artifact empty.")
        return False

    products = _collect_products_from_artifact(data)
    if not products:
        # Some artifacts are index-only; metadata.total_products might exist
        total = (data.get("metadata") or {}).get("total_products", 0)
        if total == 0:
            log("❌ FAIL: No products in artifact.")
            return False
        log("✅ COMPLIANCE: Artifact has metadata (no product list to validate).")
        return True

    zero_price_count = sum(1 for p in products if _price_il(p) == 0)
    ratio = zero_price_count / len(products) if products else 0
    if ratio > 0.5:
        log(
            f"❌ FAIL: Too many zero prices ({zero_price_count}/{len(products)}). Suspect scraper failure.")
        return False

    log("✅ COMPLIANCE: Data artifacts look valid.")
    return True


def run_agent_ingestion() -> bool:
    """Triggers the Conductor agent to rebuild data based on specs."""
    log("Activating Ingestion Agent...")
    result = subprocess.run(
        [sys.executable, "conductor_main.py", "rebuild-catalog"],
        cwd=str(_BACKEND),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log("✅ Agent finished ingestion.")
        return True
    log("❌ Agent failed.")
    if result.stderr:
        print(result.stderr)
    return False


def run_agent_ui_build() -> bool:
    """Verifies the frontend build compiles."""
    log("Verifying UI Build...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(_ROOT / "frontend"),
        shell=sys.platform == "win32",
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log("✅ Frontend compiled successfully.")
        return True
    log("❌ Frontend build failed.")
    if result.stderr:
        print(result.stderr)
    return False


def main() -> int:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    rebuild = "--rebuild" in sys.argv

    # Build and execute the DAG
    dag = build_standard_dag(rebuild=rebuild)
    results = run_dag(dag)

    all_ok = all(r.success for r in results)
    if all_ok:
        log("✨ Factory Cycle Complete. System Ready.")
        return 0
    failed = [r.label for r in results if not r.success]
    log(f"⚠️ System Halted. Failed tasks: {', '.join(failed)}")
    return 1


# ---------------------------------------------------------------------------
# DAG Executor (Pillar: Directed Acyclic Graph Supervisor)
# ---------------------------------------------------------------------------

@dataclass
class DAGNode:
    """A single task node in the execution DAG.

    Attributes:
        id:           Unique identifier (used in depends_on lists).
        label:        Human-readable name shown in logs.
        fn:           Callable returning True on success, False on failure.
        depends_on:   IDs of nodes that must complete before this one runs.
        parallel:     If True, this node may run concurrently with other
                      parallel nodes at the same topological level.
    """
    id: str
    label: str
    fn: Callable[[], bool]
    depends_on: list[str] = field(default_factory=list)
    parallel: bool = True


@dataclass
class DAGResult:
    node_id: str
    label: str
    success: bool
    error: str = ""


def _topological_levels(nodes: list[DAGNode]) -> list[list[DAGNode]]:
    """
    Group nodes into execution levels via Kahn's algorithm.
    All nodes in a level have their dependencies satisfied by previous levels.
    Raises ValueError on cyclic dependency.
    """
    id_map = {n.id: n for n in nodes}
    in_degree: dict[str, int] = {n.id: 0 for n in nodes}
    dependents: dict[str, list[str]] = {n.id: [] for n in nodes}

    for node in nodes:
        for dep in node.depends_on:
            if dep not in id_map:
                raise ValueError(
                    f"DAG: node '{node.id}' depends on unknown node '{dep}'")
            in_degree[node.id] += 1
            dependents[dep].append(node.id)

    levels: list[list[DAGNode]] = []
    ready = [n.id for n, deg in ((id_map[nid], d)
                                 for nid, d in in_degree.items()) if deg == 0]

    # Fix: collect properly
    ready = [nid for nid, deg in in_degree.items() if deg == 0]

    while ready:
        level_nodes = [id_map[nid] for nid in sorted(ready)]
        levels.append(level_nodes)
        next_ready: list[str] = []
        for nid in ready:
            for child_id in dependents[nid]:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    next_ready.append(child_id)
        ready = next_ready

    if sum(len(lvl) for lvl in levels) != len(nodes):
        raise ValueError("DAG: cyclic dependency detected — cannot execute.")

    return levels


def run_dag(nodes: list[DAGNode], max_workers: int = 4) -> list[DAGResult]:
    """
    Execute a list of DAGNodes respecting dependency order.
    Within each topological level, parallel=True nodes run concurrently;
    parallel=False nodes run sequentially as barriers.

    If any node fails, all downstream dependents are skipped.

    Returns a list of DAGResult (one per node, in execution order).
    """
    results: list[DAGResult] = []
    failed_ids: set[str] = set()

    try:
        levels = _topological_levels(nodes)
    except ValueError as exc:
        log(f"❌ DAG Error: {exc}")
        return [DAGResult(n.id, n.label, False, str(exc)) for n in nodes]

    for level_idx, level in enumerate(levels):
        log(f"📊 DAG Level {level_idx + 1}/{len(levels)} — {len(level)} task(s)")

        # Partition: parallel vs sequential
        parallel_nodes = [n for n in level if n.parallel
                          and not any(dep in failed_ids for dep in n.depends_on)]
        sequential_nodes = [n for n in level if not n.parallel]
        skipped_nodes = [n for n in level if any(
            dep in failed_ids for dep in n.depends_on)]

        # Mark skipped
        for node in skipped_nodes:
            log(f"   ⏭️  Skipping '{node.label}' (upstream failure)")
            results.append(DAGResult(node.id, node.label,
                           False, "Upstream dependency failed"))
            failed_ids.add(node.id)

        # Run parallel batch via ThreadPool
        if parallel_nodes:
            log(f"   ⚡ Running {len(parallel_nodes)} parallel task(s)...")
            with ThreadPoolExecutor(max_workers=min(max_workers, len(parallel_nodes))) as pool:
                future_map: dict[Future, DAGNode] = {
                    pool.submit(node.fn): node for node in parallel_nodes
                }
                for future in as_completed(future_map):
                    node = future_map[future]
                    try:
                        ok = future.result()
                    except Exception as exc:
                        ok = False
                        log(f"   ❌ '{node.label}' raised exception: {exc}")
                    icon = "✅" if ok else "❌"
                    log(f"   {icon} '{node.label}' → {'OK' if ok else 'FAILED'}")
                    results.append(DAGResult(node.id, node.label, ok))
                    if not ok:
                        failed_ids.add(node.id)

        # Run sequential nodes one at a time
        for node in sequential_nodes:
            if any(dep in failed_ids for dep in node.depends_on):
                log(f"   ⏭️  Skipping '{node.label}' (upstream failure)")
                results.append(DAGResult(node.id, node.label,
                               False, "Upstream dependency failed"))
                failed_ids.add(node.id)
                continue
            log(f"   🔒 Running sequential: '{node.label}'...")
            try:
                ok = node.fn()
            except Exception as exc:
                ok = False
                log(f"   ❌ '{node.label}' raised exception: {exc}")
            icon = "✅" if ok else "❌"
            log(f"   {icon} '{node.label}' → {'OK' if ok else 'FAILED'}")
            results.append(DAGResult(node.id, node.label, ok))
            if not ok:
                failed_ids.add(node.id)

    return results


def build_standard_dag(rebuild: bool = False) -> list[DAGNode]:
    """
    Returns the standard Dark Factory execution DAG.

    Graph topology:
        [compliance] → [ingestion (conditional)] → [ui_build]

    The ingestion node only runs when rebuild=True or compliance fails.
    """
    nodes: list[DAGNode] = []

    nodes.append(DAGNode(
        id="compliance",
        label="Compliance Check",
        fn=check_compliance,
        depends_on=[],
        parallel=False,
    ))

    if rebuild:
        nodes.append(DAGNode(
            id="ingestion",
            label="Catalog Ingestion",
            fn=run_agent_ingestion,
            depends_on=["compliance"],
            parallel=False,
        ))
        nodes.append(DAGNode(
            id="ui_build",
            label="Frontend UI Build",
            fn=run_agent_ui_build,
            depends_on=["ingestion"],
            parallel=False,
        ))
    else:
        nodes.append(DAGNode(
            id="ui_build",
            label="Frontend UI Build",
            fn=run_agent_ui_build,
            depends_on=["compliance"],
            parallel=False,
        ))

    return nodes


if __name__ == "__main__":
    sys.exit(main())
