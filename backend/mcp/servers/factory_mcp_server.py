"""
HALILIT FACTORY MCP SERVER  (backend/mcp/servers/factory_mcp_server.py)
=======================================================================
Exposes the Dark Factory agent swarm as a standard MCP server (stdio
JSON-RPC).  VS Code Copilot connects via .vscode/mcp.json and can call
any factory agent as a native tool inside chat.

Tools exposed:
  factory_chief_plan   – Ask the Chief to analyse the project and return
                         a JSON task queue.
  factory_build        – Run the Builder agent on a spec file path.
  factory_heal         – Run Watchdog: diagnose + auto-repair (3 cycles).
  factory_diagnose     – Run the scanner (no auto-fix).
  factory_v0_design    – Generate a v0.dev-ready UI spec + prompt from a
                         plain-English description, then optionally
                         integrate output code into the codebase.
  factory_commit       – Stage all changes and create a semantic commit.
  factory_status       – Return environment health as JSON.

  [Level 8 — Liquid MCP Core tools]
  run_frontend_tests   – Run Vitest and return raw terminal output so the
                         LLM can self-correct without a middle-manager.
  git_isolate_workspace – Create an AI feature branch before any edit.
  git_merge_workspace  – Squash-merge or rollback the feature branch.
  apply_udiff_patch    – Apply SEARCH/REPLACE blocks or unified diff to any
                         workspace file. Replaces ast_patcher — no fragile
                         string matching, no Wolverine LLM fallback needed.
  consult_oracle       – JIT Oracle Lifeline: route a stuck problem to a
                         cold-booted, context-free Oracle AI for a radical
                         outside perspective and a step-by-step Rescue Protocol.

  [Level 9 — Bicameral Governance & Backlog Engine]
  request_architectural_review – Submit the Chief's plan to the ruthless Senior
                         Architect (Tech Lead) for APPROVE / VETO before any
                         code is written. Enforces architecture laws.
  fast_pass_image_check – HEAD-only heuristic: validate an image URL in
                         microseconds without downloading it. Skips heavy
                         AI/Vision for the ~95% of obviously-valid images.
  read_roadmap         – Read the full docs/ROADMAP.md backlog.
  update_roadmap       – Tick/untick tasks or move them to Completed.
  consult_product_manager – Ask the Agile PM to pitch the next sprint priority
                         and auto-generate an [EXECUTE] spec for the Chief.

  [Level 10 — Darwin Protocol: Architectural Self-Disruption]
  run_architectural_experiment – Activate the Darwin Agent on a hypothesis: generate
                         a mutation plan, optionally execute it in an isolated Shadow
                         Cell, benchmark old-vs-new, and write PARADIGM_SHIFT_PROPOSAL.md
                         if the data proves ≥20% improvement.
  spawn_shadow_cell      – Physically clone the repo into an isolated sandbox outside
                         the workspace for radical architectural experiments.
  destroy_shadow_cell    – Destroy the Shadow Cell and reclaim disk space.
  get_paradigm_shift_proposal – Read the latest Darwin Agent proposal.

Run standalone (for debugging):
    PYTHONPATH=. python backend/mcp/servers/factory_mcp_server.py

Register in .vscode/mcp.json, then reload VS Code.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Bootstrap: ensure project root is on sys.path & .env is loaded
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger("factory.mcp")

_PYTHON = sys.executable
_FACTORY_PY = str(_ROOT / "factory.py")

# ---------------------------------------------------------------------------
# MCP protocol constants
# ---------------------------------------------------------------------------
PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "halilit-factory", "version": "6.1.0"}

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------
TOOLS: list[dict[str, Any]] = [
    {
        "name": "factory_chief_plan",
        "description": (
            "Ask the Dark Factory Chief to analyse the current project state "
            "and return a prioritised task queue. Provide an optional instruction "
            "to steer the plan (e.g. 'focus on ProductDetailView fixes')."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "Optional steering instruction for the Chief.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "factory_build",
        "description": (
            "Run the Builder agent on a spec file to materialise it into code. "
            "Pass the relative path to a spec (e.g. specs/interface/my_spec.md)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_path": {
                    "type": "string",
                    "description": "Relative path to the spec file (from project root).",
                }
            },
            "required": ["spec_path"],
        },
    },
    {
        "name": "factory_heal",
        "description": "Run the Watchdog agent: scan for errors and auto-repair (up to 3 cycles).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "factory_diagnose",
        "description": "Scan the project for TypeScript / Python errors without making changes.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "factory_v0_design",
        "description": (
            "Generate a ready-to-paste v0.dev prompt for a UI component from a "
            "plain-English description, then optionally integrate v0 output code "
            "into the codebase using the Halilit architecture rules."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Plain-English description of the UI component to design.",
                },
                "component_type": {
                    "type": "string",
                    "description": "Component category hint, e.g. ProductCard, InventoryRow, Dashboard.",
                    "default": "UIComponent",
                },
                "v0_output_code": {
                    "type": "string",
                    "description": "Optional: paste the raw TSX code returned by v0.dev to integrate it.",
                },
                "target_file": {
                    "type": "string",
                    "description": "Optional: relative path where integrated code should be written.",
                },
            },
            "required": ["description"],
        },
    },
    {
        "name": "factory_commit",
        "description": "Stage all current changes and create a semantic git commit.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "factory_status",
        "description": "Return environment health: API key, venv, spec count, agent presence.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # -----------------------------------------------------------------------
    # Level 8 — Liquid MCP Core (Phase 1: Tool Consolidation)
    # -----------------------------------------------------------------------
    {
        "name": "run_frontend_tests",
        "description": (
            "Run the Vitest frontend unit-test suite and return the raw terminal output. "
            "Pass an optional target_file to narrow the run to a single component. "
            "The LLM can read exact error messages and self-correct without a middle-manager."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_file": {
                    "type": "string",
                    "description": "Optional filename filter (e.g. 'GlobalSearch.tsx'). Omit to run all tests.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "git_isolate_workspace",
        "description": (
            "Create and checkout a new AI feature branch before any code changes are made. "
            "Wraps repo_agent.create_feature_branch(). Returns the branch name created."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_name": {
                    "type": "string",
                    "description": "Short slug describing the task (e.g. 'add-debounce-search').",
                }
            },
            "required": ["task_name"],
        },
    },
    {
        "name": "git_merge_workspace",
        "description": (
            "Merge a successful AI feature branch back into the base branch, or trash it on failure. "
            "Wraps repo_agent.merge_and_cleanup()."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "branch_name": {
                    "type": "string",
                    "description": "The feature branch name returned by git_isolate_workspace.",
                },
                "success_status": {
                    "type": "boolean",
                    "description": "True to squash-merge into base, False to delete the branch and rollback.",
                },
            },
            "required": ["branch_name", "success_status"],
        },
    },
    {
        "name": "execute_bash_command",
        "description": (
            "Execute an arbitrary shell command and return stdout + stderr. "
            "Gives the LLM native OS-level autonomy: run npm install, git status, tsc, etc. "
            "working_directory defaults to the project root if omitted."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute (e.g. 'pnpm install react-router-dom').",
                },
                "working_directory": {
                    "type": "string",
                    "description": "Absolute or project-relative working directory. Defaults to project root.",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "apply_udiff_patch",
        "description": (
            "Apply a surgical code patch to a workspace file using either:\n"
            "  • SEARCH/REPLACE blocks (Aider format) — preferred for LLM-generated edits\n"
            "  • Standard Unified Diff (git apply format)\n"
            "The format is auto-detected. This replaces the brittle ast_patcher and never silently\n"
            "corrupts files — it fails loudly if the anchor cannot be found."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "Workspace-relative path to the file to patch "
                        "(e.g. 'frontend/src/components/GlobalSearch.tsx'). "
                        "Required for SEARCH/REPLACE format; optional for unified diff "
                        "(path is taken from the diff header)."
                    ),
                },
                "patch_text": {
                    "type": "string",
                    "description": (
                        "The patch to apply. Use SEARCH/REPLACE blocks:\n"
                        "  <<<<<<< SEARCH\n"
                        "  old code\n"
                        "  =======\n"
                        "  new code\n"
                        "  >>>>>>> REPLACE\n"
                        "Or a standard unified diff string."
                    ),
                },
                "fmt": {
                    "type": "string",
                    "description": "Format hint: 'auto' (default), 'search_replace', or 'unified'.",
                    "enum": ["auto", "search_replace", "unified"],
                    "default": "auto",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, validate the patch but do not write any files.",
                    "default": False,
                },
            },
            "required": ["patch_text"],
        },
    },
    # -----------------------------------------------------------------------
    # Bicameral Governance — Two-Key Pre-Flight Gatekeeper
    # -----------------------------------------------------------------------
    {
        "name": "request_architectural_review",
        "description": (
            "Submit the Chief's proposed plan to the ruthless Senior Architect (Tech Lead) "
            "for pre-flight approval BEFORE any code is written. "
            "The Tech Lead will VETO plans that violate architecture laws (wrong framework, "
            "Redux instead of Zustand, Next.js instead of Vite, etc.) and provide a "
            "corrected strategy. Returns '[APPROVED] ...' or '[VETOED] corrected strategy'. "
            "CRITICAL: The Chief MUST call this tool before delegating any implementation task."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "description": "The operator's original goal / intent.",
                },
                "proposed_plan": {
                    "type": "string",
                    "description": "Human-readable summary of what the Chief intends to do.",
                },
            },
            "required": ["intent", "proposed_plan"],
        },
    },
    # -----------------------------------------------------------------------
    # Fast-Pass Image Heuristic — Data Manager I/O unblock
    # -----------------------------------------------------------------------
    {
        "name": "fast_pass_image_check",
        "description": (
            "Perform a microsecond HEAD-only heuristic check on an image URL. "
            "Returns true if the URL serves a real image (Content-Type is an image type "
            "AND Content-Length > 10 KB). Returns false if the image is broken, "
            "suspiciously small, or returns a non-image content type. "
            "Use this during catalog ingestion to skip heavy AI/Vision validation for "
            "the ~95 percent of images that are obviously valid."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "The full URL of the product image to check.",
                },
            },
            "required": ["image_url"],
        },
    },
    # -----------------------------------------------------------------------
    # Backlog Engine — Product Manager Roadmap tools
    # -----------------------------------------------------------------------
    {
        "name": "read_roadmap",
        "description": (
            "Read the full contents of docs/ROADMAP.md — the factory backlog. "
            "Returns the current sprint tasks, long-term epics, and completed items. "
            "The Product Manager uses this before every briefing to surface the "
            "highest-priority incomplete task."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "update_roadmap",
        "description": (
            "Update a task's status in docs/ROADMAP.md. "
            "Use new_status='complete' to tick a checkbox, 'incomplete' to untick, "
            "or 'move_to_completed' to move the item to the Completed section. "
            "The Product Manager calls this automatically when the Operator confirms a feature is done."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_name": {
                    "type": "string",
                    "description": "The text of the task to find (partial match is fine).",
                },
                "new_status": {
                    "type": "string",
                    "description": "One of: 'complete', 'incomplete', 'move_to_completed'.",
                    "enum": ["complete", "incomplete", "move_to_completed"],
                },
            },
            "required": ["task_name", "new_status"],
        },
    },
    {
        "name": "consult_product_manager",
        "description": (
            "Ask the Agile Product Manager to read the roadmap and brief you on the "
            "highest-priority next task. The PM will explain WHY it is the priority, "
            "assess the technical state, and auto-generate a ready-to-execute Chief spec. "
            "Optionally pass confirm_complete_task to mark a finished feature as done "
            "in the roadmap before the PM formulates the next brief."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string",
                    "description": "Your question or instruction for the PM (e.g. 'What\'s next?').",
                    "default": "What's next?",
                },
                "confirm_complete_task": {
                    "type": "string",
                    "description": "Optional: name / partial text of a task just completed to auto-tick it.",
                },
            },
            "required": [],
        },
    },
    # -----------------------------------------------------------------------
    # JIT Oracle Lifeline (Level 8 Safety Net)
    # -----------------------------------------------------------------------
    {
        "name": "consult_oracle",
        "description": (
            "JIT Oracle Lifeline: when the Swarm or Core LLM is stuck in a failure loop "
            "or feels uncertain about the right approach, invoke this tool to route the "
            "problem to a completely isolated, cold-booted Oracle AI. The Oracle has zero "
            "memory of previous attempts and approaches the problem from first principles, "
            "returning a radical, step-by-step Rescue Protocol. "
            "Trigger this proactively when confused — don't wait for a fatal loop."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "description": "What you are trying to accomplish (the goal, in plain English).",
                },
                "current_code": {
                    "type": "string",
                    "description": "The code / file content that is failing or causing confusion.",
                },
                "error_logs": {
                    "type": "string",
                    "description": "Raw compiler, runtime, or test error output.",
                },
            },
            "required": ["intent"],
        },
    },
    # -----------------------------------------------------------------------
    # Darwin Protocol — Architectural Self-Disruption (Level 10)
    # -----------------------------------------------------------------------
    {
        "name": "run_architectural_experiment",
        "description": (
            "Activate the Darwin Agent (Architectural Red Team). Formulates a hypothesis "
            "about an architectural bottleneck, generates a concrete mutation plan and benchmark "
            "strategy, optionally spins up a Shadow Cell (isolated repo clone) to execute the "
            "mutation, and writes a PARADIGM_SHIFT_PROPOSAL.md if the data proves a ≥20%% gain. "
            "Use this whenever the Operator wants to question the current architecture without "
            "touching the live repository. Safe mode (run_in_cell=false) returns the plan only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "hypothesis": {
                    "type": "string",
                    "description": (
                        "The architectural challenge to explore, e.g. "
                        "'SQLite JOINs for accessory mapping are slow — test NetworkX graph' or "
                        "'Standard Python loops in ingestion are bottlenecked — test asyncio+aiohttp'."
                    ),
                },
                "run_in_cell": {
                    "type": "boolean",
                    "description": (
                        "If true, physically spin up a Shadow Cell, execute mutation commands "
                        "inside it, and run benchmarks. If false (default), return the plan only "
                        "without touching the filesystem."
                    ),
                    "default": False,
                },
            },
            "required": ["hypothesis"],
        },
    },
    {
        "name": "spawn_shadow_cell",
        "description": (
            "Physically clone the entire live repository into an isolated sandbox directory "
            "OUTSIDE the main workspace (halilit_shadow_cell/). The Shadow Cell can be mutated, "
            "benchmarked, and destroyed without ever affecting production code. "
            "Call destroy_shadow_cell when done to free disk space."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "force": {
                    "type": "boolean",
                    "description": "If true (default), destroy any existing Shadow Cell before creating a fresh one.",
                    "default": True,
                }
            },
            "required": [],
        },
    },
    {
        "name": "destroy_shadow_cell",
        "description": (
            "Destroy the Shadow Cell sandbox and reclaim disk space. "
            "Always call this after an architectural experiment is complete."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_paradigm_shift_proposal",
        "description": (
            "Read the latest PARADIGM_SHIFT_PROPOSAL.md written by the Darwin Agent. "
            "Returns the full Markdown document with benchmark evidence and the Governor "
            "decision instructions. Returns a placeholder if no proposal exists yet."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def _run_factory(args: list[str], timeout: int = 120) -> tuple[bool, str]:
    """Run factory.py with given args. Returns (success, output)."""
    cmd = [_PYTHON, _FACTORY_PY] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(_ROOT),
        )
        out = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


def _tool_chief_plan(args: dict[str, Any]) -> str:
    instruction = args.get("instruction", "")
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from chief_agent import consult_chief  # type: ignore
        plan = consult_chief(instruction, is_startup=not instruction)
        return json.dumps(plan, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_build(args: dict[str, Any]) -> str:
    spec = args.get("spec_path", "").strip()
    if not spec:
        return "Error: spec_path is required."
    ok, out = _run_factory(["build", spec], timeout=180)
    return out


def _tool_heal(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["heal"], timeout=240)
    return out


def _tool_diagnose(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["diagnose"], timeout=120)
    return out


def _tool_v0_design(args: dict[str, Any]) -> str:
    description = args.get("description", "")
    component_type = args.get("component_type", "UIComponent")
    v0_code = args.get("v0_output_code", "").strip()
    target_file = args.get("target_file", "").strip()

    try:
        from backend.factory.v0_agent import generate_v0_prompt, integrate_v0_output  # type: ignore
        if v0_code and target_file:
            result = integrate_v0_output(v0_code, target_file)
            return json.dumps(result, indent=2)
        else:
            result = generate_v0_prompt(description, component_type)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_commit(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["commit"], timeout=90)
    return out


def _tool_status(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["status"], timeout=20)
    return out


# ---------------------------------------------------------------------------
# Level 8 — Liquid MCP Core tool handlers
# ---------------------------------------------------------------------------

_FRONTEND_DIR = _ROOT / "frontend"


def _tool_run_frontend_tests(args: dict[str, Any]) -> str:
    """Run Vitest and return the raw terminal output so the LLM can self-correct."""
    target_file: str = args.get("target_file", "").strip()
    cmd = ["pnpm", "test", "--", "--run", "--passWithNoTests"]
    if target_file:
        from pathlib import Path as _P
        cmd.append(_P(target_file).name)
    try:
        result = subprocess.run(
            cmd,
            cwd=str(_FRONTEND_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        raw = (result.stdout + "\n" + result.stderr).strip()
        status = "PASS" if result.returncode == 0 else "FAIL"
        return f"[{status}]\n{raw}"
    except subprocess.TimeoutExpired:
        return "[ERROR] Test run timed out after 120 s."
    except FileNotFoundError:
        return "[ERROR] pnpm not found. Is it installed in the frontend directory?"
    except Exception as exc:
        return f"[ERROR] {exc}"


def _tool_git_isolate_workspace(args: dict[str, Any]) -> str:
    """Create an AI feature branch and return its name."""
    task_name: str = args.get("task_name", "ai-task").strip()
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from repo_agent import create_feature_branch  # type: ignore
        branch = create_feature_branch(task_name)
        return json.dumps({"branch": branch, "status": "created"})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _tool_git_merge_workspace(args: dict[str, Any]) -> str:
    """Merge or trash an AI feature branch depending on success_status."""
    branch_name: str = args.get("branch_name", "").strip()
    success: bool = bool(args.get("success_status", False))
    if not branch_name:
        return json.dumps({"error": "branch_name is required."})
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from repo_agent import merge_and_cleanup  # type: ignore
        merge_and_cleanup(branch_name, success)
        action = "merged" if success else "rolled_back"
        return json.dumps({"branch": branch_name, "status": action})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _tool_execute_bash_command(args: dict[str, Any]) -> str:
    """Execute an arbitrary shell command and return stdout + stderr."""
    command: str = args.get("command", "").strip()
    working_directory: str = args.get("working_directory", "").strip()
    if not command:
        return json.dumps({"error": "command is required."})

    cwd = working_directory if working_directory else str(_ROOT)
    # Resolve relative paths against project root
    from pathlib import Path as _P
    resolved_cwd = str((_ROOT / cwd).resolve()
                       ) if not _P(cwd).is_absolute() else cwd

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=resolved_cwd,
            capture_output=True,
            text=True,
            timeout=180,
        )
        return json.dumps({
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Command timed out after 180 s."})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _tool_apply_udiff_patch(args: dict[str, Any]) -> str:
    """Apply a SEARCH/REPLACE or unified-diff patch — the Level 8 code-edit tool."""
    patch_text: str = args.get("patch_text", "").strip()
    file_path: str = args.get("file_path", "").strip()
    fmt: str = args.get("fmt", "auto")
    dry_run: bool = bool(args.get("dry_run", False))

    if not patch_text:
        return json.dumps({"success": False, "message": "patch_text is required."})

    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from udiff_patcher import apply_udiff  # type: ignore
        result = apply_udiff(
            file_path if file_path else None,
            patch_text,
            fmt=fmt,
            dry_run=dry_run,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return json.dumps({"success": False, "message": str(exc)})


def _tool_consult_oracle(args: dict[str, Any]) -> str:
    """Route a stuck problem to the JIT Oracle Lifeline."""
    intent: str = args.get("intent", "").strip()
    current_code: str = args.get("current_code", "")
    error_logs: str = args.get("error_logs", "")

    if not intent:
        return json.dumps({"error": "intent is required."})

    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from oracle_agent import consult_external_oracle  # type: ignore
        rescue = consult_external_oracle(
            intent=intent,
            current_code=current_code,
            error_logs=error_logs,
        )
        return json.dumps({"rescue_protocol": rescue})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Bicameral Governance tool handlers
# ---------------------------------------------------------------------------

def _tool_request_architectural_review(args: dict[str, Any]) -> str:
    """Submit a plan to the Tech Lead gatekeeper for APPROVE / VETO verdict."""
    intent: str = args.get("intent", "").strip()
    proposed_plan: str = args.get("proposed_plan", "").strip()
    if not intent or not proposed_plan:
        return "[ERROR] Both 'intent' and 'proposed_plan' are required."
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from tech_lead_agent import review_architectural_plan  # type: ignore
        return review_architectural_plan(intent, proposed_plan)
    except Exception as exc:
        return f"[ERROR] Tech Lead unavailable: {exc}"


def _tool_fast_pass_image_check(args: dict[str, Any]) -> str:
    """Perform a synchronous HEAD-only heuristic image check."""
    image_url: str = args.get("image_url", "").strip()
    if not image_url:
        return json.dumps({"valid": False, "error": "image_url is required."})
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "services"))
        from product_image_validation import fast_pass_image_check  # type: ignore
        valid = fast_pass_image_check(image_url)
        return json.dumps({"image_url": image_url, "valid": valid,
                           "validation_path": "fast_pass" if valid else "suspicious"})
    except Exception as exc:
        return json.dumps({"valid": False, "error": str(exc)})


# ---------------------------------------------------------------------------
# Backlog Engine / PM tool handlers
# ---------------------------------------------------------------------------

def _tool_read_roadmap(args: dict[str, Any]) -> str:  # noqa: ARG001
    """Return the full contents of docs/ROADMAP.md."""
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from product_manager import read_roadmap  # type: ignore
        return read_roadmap()
    except Exception as exc:
        roadmap_path = _ROOT / "docs" / "ROADMAP.md"
        if roadmap_path.exists():
            return roadmap_path.read_text(encoding="utf-8")
        return f"[ERROR] Could not read roadmap: {exc}"


def _tool_update_roadmap(args: dict[str, Any]) -> str:
    """Update a task checkbox in docs/ROADMAP.md."""
    task_name: str = args.get("task_name", "").strip()
    new_status: str = args.get("new_status", "complete").strip()
    if not task_name:
        return "[ERROR] task_name is required."
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from product_manager import update_roadmap  # type: ignore
        return update_roadmap(task_name, new_status)
    except Exception as exc:
        return f"[ERROR] Could not update roadmap: {exc}"


def _tool_consult_product_manager(args: dict[str, Any]) -> str:
    """Ask the PM to brief the Operator on the next roadmap priority."""
    user_input: str = args.get("user_input", "What's next?").strip()
    # type: ignore[assignment]
    confirm_task: str = args.get("confirm_complete_task", "").strip() or None
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from product_manager import consult_product_manager  # type: ignore
        return consult_product_manager(user_input, confirm_task)
    except Exception as exc:
        return f"[ERROR] PM Agent unavailable: {exc}"


# ---------------------------------------------------------------------------
# Darwin Protocol handlers (Level 10 — Architectural Self-Disruption)
# ---------------------------------------------------------------------------

def _tool_run_architectural_experiment(args: dict[str, Any]) -> str:
    """
    Activate the Darwin Agent on a hypothesis.
    run_in_cell=False: returns plan only (safe).
    run_in_cell=True:  spins up Shadow Cell, mutates, benchmarks, destroys.
    """
    hypothesis: str = args.get("hypothesis", "").strip()
    run_in_cell: bool = bool(args.get("run_in_cell", False))

    if not hypothesis:
        return "[ERROR] hypothesis is required. Describe the architectural bottleneck to explore."

    try:
        sys.path.insert(0, str(_ROOT))
        from backend.factory.darwin_agent import initiate_darwin_experiment  # type: ignore
        return initiate_darwin_experiment(hypothesis, run_in_cell=run_in_cell)
    except Exception as exc:
        return f"[ERROR] Darwin Agent unavailable: {exc}"


def _tool_spawn_shadow_cell(args: dict[str, Any]) -> str:
    """Spin up an isolated Shadow Cell clone of the live repository."""
    force: bool = bool(args.get("force", True))
    try:
        sys.path.insert(0, str(_ROOT))
        from backend.factory.shadow_cell import spin_up_shadow_cell, shadow_cell_status  # type: ignore
        path = spin_up_shadow_cell(force=force)
        status = shadow_cell_status()
        return json.dumps({"path": path, **status})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _tool_destroy_shadow_cell(args: dict[str, Any]) -> str:  # noqa: ARG001
    """Destroy the Shadow Cell and reclaim disk space."""
    try:
        sys.path.insert(0, str(_ROOT))
        from backend.factory.shadow_cell import destroy_shadow_cell  # type: ignore
        destroy_shadow_cell()
        return json.dumps({"status": "destroyed"})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _tool_get_paradigm_shift_proposal(args: dict[str, Any]) -> str:  # noqa: ARG001
    """Return the latest PARADIGM_SHIFT_PROPOSAL.md (or a placeholder)."""
    try:
        sys.path.insert(0, str(_ROOT))
        from backend.factory.darwin_agent import get_last_proposal  # type: ignore
        return get_last_proposal()
    except Exception as exc:
        proposal_path = _ROOT / "PARADIGM_SHIFT_PROPOSAL.md"
        if proposal_path.exists():
            return proposal_path.read_text(encoding="utf-8")
        return f"[ERROR] Could not read proposal: {exc}"


_TOOL_HANDLERS = {
    "factory_chief_plan": _tool_chief_plan,
    "factory_build": _tool_build,
    "factory_heal": _tool_heal,
    "factory_diagnose": _tool_diagnose,
    "factory_v0_design": _tool_v0_design,
    "factory_commit": _tool_commit,
    "factory_status": _tool_status,
    # Level 8 — Liquid MCP Core
    "run_frontend_tests": _tool_run_frontend_tests,
    "git_isolate_workspace": _tool_git_isolate_workspace,
    "git_merge_workspace": _tool_git_merge_workspace,
    "execute_bash_command": _tool_execute_bash_command,
    "apply_udiff_patch": _tool_apply_udiff_patch,
    # JIT Oracle Lifeline (Level 8 Safety Net)
    "consult_oracle": _tool_consult_oracle,
    # Bicameral Governance tools
    "request_architectural_review": _tool_request_architectural_review,
    "fast_pass_image_check": _tool_fast_pass_image_check,
    # Backlog Engine / PM tools
    "read_roadmap": _tool_read_roadmap,
    "update_roadmap": _tool_update_roadmap,
    "consult_product_manager": _tool_consult_product_manager,
    # Darwin Protocol — Architectural Self-Disruption (Level 10)
    "run_architectural_experiment": _tool_run_architectural_experiment,
    "spawn_shadow_cell": _tool_spawn_shadow_cell,
    "destroy_shadow_cell": _tool_destroy_shadow_cell,
    "get_paradigm_shift_proposal": _tool_get_paradigm_shift_proposal,
}

# ---------------------------------------------------------------------------
# MCP JSON-RPC stdio server loop
# ---------------------------------------------------------------------------


def _respond(request_id: Any, result: Any) -> None:
    msg = json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result})
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _error(request_id: Any, code: int, message: str) -> None:
    msg = json.dumps({"jsonrpc": "2.0", "id": request_id,
                      "error": {"code": code, "message": message}})
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _handle(raw: str) -> None:
    try:
        req = json.loads(raw)
    except json.JSONDecodeError:
        return  # silently drop malformed lines (ping/keepalive etc.)

    req_id = req.get("id")
    method = req.get("method", "")

    # ----- Lifecycle -----
    if method == "initialize":
        _respond(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo": SERVER_INFO,
            "capabilities": {"tools": {}},
        })
        return

    if method == "notifications/initialized":
        return  # no response for notifications

    # ----- Tool discovery -----
    if method == "tools/list":
        _respond(req_id, {"tools": TOOLS})
        return

    # ----- Tool execution -----
    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        handler = _TOOL_HANDLERS.get(tool_name)
        if handler is None:
            _error(req_id, -32601, f"Unknown tool: {tool_name}")
            return
        try:
            output = handler(tool_args)
        except Exception as exc:
            output = f"Error: {exc}"
        _respond(req_id, {
            "content": [{"type": "text", "text": output}],
            "isError": False,
        })
        return

    # ----- Unknown method -----
    if req_id is not None:
        _error(req_id, -32601, f"Method not found: {method}")


def main() -> None:
    logger.info("Halilit Factory MCP Server starting (stdio)")
    for line in sys.stdin:
        line = line.strip()
        if line:
            _handle(line)


if __name__ == "__main__":
    main()
