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

# ---------------------------------------------------------------------------
# Chief Agent — lazy import so the module is usable without AI key for pure DAG runs
# ---------------------------------------------------------------------------


def _consult_chief(prompt: str, failure_context: str = "") -> dict:
    """Lazy-import and call chief_agent.consult_chief to avoid circular deps."""
    _factory_dir = _BACKEND / "factory"
    if str(_factory_dir) not in sys.path:
        sys.path.insert(0, str(_factory_dir))
    from chief_agent import consult_chief  # noqa: PLC0415
    return consult_chief(prompt, failure_context=failure_context)


# ---------------------------------------------------------------------------
# Grand Task Force — standard end-to-end catalog+UI polish prompt
# ---------------------------------------------------------------------------
GRAND_TASK_FORCE_PROMPT = (
    "Chief, initiate a Grand Task Force to perfect the catalog presentation. "
    "Step 1: Rebuild the data catalog to ensure zero broken prices or missing relationships. "
    "Step 2: Have the Steerer audit InventoryView.tsx and ProductDetailView.tsx against the specs. "
    "Step 3: Run Visual QA to ensure stock badges and accessories display perfectly. "
    "Step 4: Have the Builder fix any visual or data-binding discrepancies. "
    "Step 5: Commit the perfected state."
)


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


def run_grand_task_force(prompt: str = "") -> int:
    """
    Route a free-text prompt through the Chief Agent, convert its queue to a
    DAG, and execute it.  Used by the 'grand_task_force' CLI command and the
    Night Shift autonomous protocol.

    Args:
        prompt: Natural-language instruction.  Defaults to the canonical
                GRAND_TASK_FORCE_PROMPT when empty.
    Returns:
        0 on full success, 1 if any DAG node failed.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    effective_prompt = prompt.strip() or GRAND_TASK_FORCE_PROMPT

    log(f"🚀 Grand Task Force activated.")
    log(f"   Prompt : {effective_prompt[:120]}{'...' if len(effective_prompt) > 120 else ''}")

    plan = _consult_chief(effective_prompt)
    explanation = plan.get("explanation", "")
    proposal = plan.get("proposal", "")
    queue = plan.get("queue", [])

    if explanation:
        log(f"📋 Chief says: {explanation}")
    if proposal:
        log(f"📋 Plan      : {proposal}")

    if not queue:
        log("⚠️  Chief returned an empty queue — nothing to execute.")
        log("   Check GEMINI_API_KEY and re-run with a more specific prompt.")
        return 1

    log(f"📊 Executing DAG with {len(queue)} task(s) from Chief...")
    nodes = build_dynamic_dag_from_queue(queue)
    results = run_dag(nodes)

    all_ok = all(r.success for r in results)
    if all_ok:
        log("✨ Grand Task Force Complete. Catalog & UI polished.")
        return 0

    failed = [r.label for r in results if not r.success]
    log(f"⚠️  Grand Task Force halted. Failed tasks: {', '.join(failed)}")

    # Recovery pass — ask the Chief for a fix plan
    log("🔄 Entering Recovery Mode...")
    failure_report = "\n".join(
        f"FAILED: {r.label} — {r.error}" for r in results if not r.success
    )
    fix_plan = _consult_chief("", failure_context=failure_report)
    fix_queue = fix_plan.get("queue", [])
    if fix_queue:
        log(f"🛠  Recovery queue has {len(fix_queue)} task(s).")
        fix_nodes = build_dynamic_dag_from_queue(fix_queue)
        fix_results = run_dag(fix_nodes)
        all_ok = all(r.success for r in fix_results)
        if all_ok:
            log("✨ Recovery Complete. System stabilised.")
            return 0
    log("❌ Recovery did not fully succeed. Manual intervention may be needed.")
    return 1


def main() -> int:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # If a free-text prompt is passed as the first positional argument,
    # route through the Grand Task Force (Chief → DAG) pipeline.
    # Flags like --rebuild are still honoured when no prompt is present.
    args = sys.argv[1:]
    non_flag_args = [a for a in args if not a.startswith("--")]

    if non_flag_args:
        prompt = " ".join(non_flag_args)
        return run_grand_task_force(prompt)

    rebuild = "--rebuild" in sys.argv

    # Build and execute the standard DAG
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


# ---------------------------------------------------------------------------
# Dynamic DAG Builder  (Pillar: Chief → DAG Bridge)
# ---------------------------------------------------------------------------

def run_agent_tool(tool: str, args: str = "", task: dict | None = None) -> bool:
    """
    Execute a single factory.py tool via subprocess.

    Maps the Chief's tool names to `factory.py` CLI commands.
    Returns True on success (exit-code 0), False on failure.

    Routing notes:
      • 'build'  (no args OR free-text args)  → conductor_main.py rebuild-catalog
      • 'build'  (args ends with .md)          → factory.py build <spec_path>
      • 'implement' (args = spec .md path)     → factory.py build <spec_path>
      • 'task_force'                            → factory.py task_force <id> <goal>
                                                  auto-generates id when absent
    """
    import uuid as _uuid

    task = task or {}
    py = sys.executable
    factory_script = str(_ROOT / "factory.py")
    conductor_script = str(_BACKEND / "conductor_main.py")

    # ---------------------------------------------------------------------------
    # 'build' — catalog rebuild vs. spec materialisation
    # ---------------------------------------------------------------------------
    if tool == "build":
        if args and args.strip().endswith(".md"):
            # Looks like a spec path → materialise code
            cmd = [py, factory_script, "build", args.strip()]
        else:
            # Data rebuild — run conductor rebuild-catalog
            log("   🗄  Routing 'build' → conductor rebuild-catalog")
            result = subprocess.run(
                [py, conductor_script, "rebuild-catalog"],
                cwd=str(_BACKEND),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                log(f"❌ Tool 'build' (catalog rebuild) failed (exit {result.returncode})")
                tail = "\n".join(
                    (result.stdout + "\n" + result.stderr).strip().splitlines()[-20:])
                if tail:
                    log(tail)
                return False
            return True

    # ---------------------------------------------------------------------------
    # 'task_force' — multi-agent coordinator
    # ---------------------------------------------------------------------------
    elif tool == "task_force":
        tf_id   = task.get("id", "") or _uuid.uuid4().hex[:8]
        tf_goal = task.get("goal", "") or args or "Improve the system"
        agents  = ",".join(task.get("agents", ["steerer", "builder", "watchdog"]))
        cmd = [py, factory_script, "task_force", tf_id, tf_goal, agents]

    # ---------------------------------------------------------------------------
    # Standard tool map
    # ---------------------------------------------------------------------------
    else:
        _tool_cmd_map: dict[str, list[str]] = {
            "design":    [py, factory_script, "design", args] if args else [],
            "implement": [py, factory_script, "build", args] if args else [],
            "heal":      [py, factory_script, "heal"],
            "diagnose":  [py, factory_script, "diagnose"],
            "steer":     [py, factory_script, "steer"],
            "doc":       [py, factory_script, "doc"],
            "optimize":  [py, factory_script, "optimize", args] if args else [],
            "commit":    [py, factory_script, "commit"],
            "reflect":   [py, factory_script, "reflect", args or "(no context)"],
        }
        cmd = _tool_cmd_map.get(tool, [])

    if not cmd:
        log(f"⚠️  No command mapped for tool '{tool}' — skipping.")
        return True  # Non-fatal: unknown tool is not a hard failure

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"❌ Tool '{tool}' failed (exit {result.returncode})")
        tail = "\n".join(
            (result.stdout + "\n" + result.stderr).strip().splitlines()[-20:])
        if tail:
            log(tail)
        return False
    return True


def build_dynamic_dag_from_queue(queue: list[dict]) -> list[DAGNode]:
    """
    Convert the Chief Agent's JSON task queue into an executable DAG.

    The Chief outputs tasks as:
        {"tool": str, "args": str, "parallel": bool, ...extra task_force keys...}

    Dependency logic:
      • parallel=True  → depends only on the LAST sequential barrier (or nothing).
      • parallel=False → depends on ALL preceding nodes (acts as a synchronisation
                         barrier, waits for every parallel fan-out to finish).

    This mirrors the execution semantics of nexus.py's execute_swarm() but uses
    the DAG engine so downstream failure propagation is automatic.
    """
    if not queue:
        return []

    nodes: list[DAGNode] = []
    prev_sequential_id: str | None = None  # last barrier node id

    for idx, task in enumerate(queue):
        tool = task.get("tool", "unknown")
        args = task.get("args", "")
        is_parallel = task.get("parallel", False)
        label = f"{tool.upper()} | {args}".strip(" |")
        node_id = f"task_{idx:02d}_{tool}"

        if is_parallel:
            # Parallel node: only depends on the previous sequential barrier
            depends_on = [prev_sequential_id] if prev_sequential_id else []
        else:
            # Sequential barrier: depends on every preceding node (fan-in)
            depends_on = [n.id for n in nodes]

        nodes.append(DAGNode(
            id=node_id,
            label=label,
            fn=lambda t=task: run_agent_tool(
                t.get("tool", ""), t.get("args", ""), t
            ),
            depends_on=depends_on,
            parallel=is_parallel,
        ))

        if not is_parallel:
            prev_sequential_id = node_id

    return nodes


if __name__ == "__main__":
    sys.exit(main())
